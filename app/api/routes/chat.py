import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import (
    get_context_builder,
    get_history_engine,
    get_openai_service,
    get_reranker,
    get_retriever,
)
from app.core.config import get_settings
from app.models.chat import ChatRequest, ChatResponse
from app.models.common import Citation
from app.services.history.bootstrap import bootstrap_conversation
from app.services.history.engine import HistoryEngine
from app.services.llm.openai_service import OpenAIService
from app.services.llm.prompts import SYSTEM_PROMPT_GENERAL, SYSTEM_PROMPT_RAG, build_user_turn
from app.services.retrieval.context_builder import ContextBuilder
from app.services.retrieval.reranker import Reranker
from app.services.retrieval.retriever import Retriever

router = APIRouter(prefix="/api/chat", tags=["chat"])


async def _prepare_turn(
    request: ChatRequest,
    retriever: Retriever,
    reranker: Reranker,
    context_builder: ContextBuilder,
    history_engine: HistoryEngine,
) -> tuple[str, list[dict], list[Citation], list[str]]:
    """Shared orchestration for both the blocking and streaming chat endpoints.

    Only retrieves when knowledge_base_ids is non-empty. This slice
    doesn't include an intent classifier — that's a reasonable next
    addition, but keeping selection explicit (client picks the KBs)
    avoids adding an extra LLM call and a failure mode for this pass.
    """
    settings = get_settings()
    conversation_id = bootstrap_conversation(request.conversation_id)

    citations: list[Citation] = []
    sources_used: list[str] = []
    context_text = None

    if request.knowledge_base_ids:
        query_vector = await retriever.embedding_service.embed_text(request.message)
        candidates = await retriever.retrieve(
            query=request.message,
            knowledge_base_ids=request.knowledge_base_ids,
            top_k=settings.retrieval_top_k,
            with_vectors=True,
        )
        ranked = reranker.rerank(query_vector, candidates, top_k=settings.rerank_top_k)
        context_text, citations = context_builder.build(ranked)
        if citations:
            sources_used.append("documents")

    history = await history_engine.get_windowed_history(conversation_id)
    system_prompt = SYSTEM_PROMPT_RAG if context_text else SYSTEM_PROMPT_GENERAL

    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": build_user_turn(request.message, context_text)})

    # Persist the user's turn before generating the answer, so a failure
    # mid-generation doesn't silently drop what the user actually asked.
    await history_engine.append_user_message(conversation_id, request.message)

    return conversation_id, messages, citations, sources_used


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    retriever: Retriever = Depends(get_retriever),
    reranker: Reranker = Depends(get_reranker),
    context_builder: ContextBuilder = Depends(get_context_builder),
    history_engine: HistoryEngine = Depends(get_history_engine),
    llm: OpenAIService = Depends(get_openai_service),
):
    conversation_id, messages, citations, sources_used = await _prepare_turn(
        request, retriever, reranker, context_builder, history_engine
    )

    answer = await llm.complete(messages)
    await history_engine.append_assistant_message(conversation_id, answer)

    return ChatResponse(
        message_id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        answer=answer,
        sources_used=sources_used,
        citations=citations,
    )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    retriever: Retriever = Depends(get_retriever),
    reranker: Reranker = Depends(get_reranker),
    context_builder: ContextBuilder = Depends(get_context_builder),
    history_engine: HistoryEngine = Depends(get_history_engine),
    llm: OpenAIService = Depends(get_openai_service),
):
    conversation_id, messages, citations, sources_used = await _prepare_turn(
        request, retriever, reranker, context_builder, history_engine
    )

    async def event_generator():
        full_answer = ""
        yield f"event: start\ndata: {conversation_id}\n\n"
        async for token in llm.stream(messages):
            full_answer += token
            yield f"event: token\ndata: {token}\n\n"
        await history_engine.append_assistant_message(conversation_id, full_answer)
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")