import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_context_builder,
    get_history_engine,
    get_openai_service,
    get_reranker,
    get_retriever,
)
from app.agents.graph import ChatOrchestratorGraph
from app.agents.state import AgentState
from app.core.database import get_db
from app.core.tenant_context import get_tenant_id, get_user_id
from app.models.chat import ChatRequest, ChatResponse
from app.repositories.connection_repo import ConnectionRepository
from app.repositories.permission_repo import PermissionRepository
from app.repositories.schema_repo import SchemaRepository
from app.repositories.user_repo import UserRepository
from app.services.database.connection_service import ConnectionService
from app.services.database.metadata_cache import MetadataCacheService
from app.services.history.bootstrap import bootstrap_conversation
from app.services.history.engine import HistoryEngine
from app.services.llm.openai_service import OpenAIService
from app.services.permission_service import PermissionService
from app.services.retrieval.context_builder import ContextBuilder
from app.services.retrieval.reranker import Reranker
from app.services.retrieval.retriever import Retriever
from app.services.sql.engine import SQLEngine

router = APIRouter(prefix="/api/chat", tags=["chat"])


async def _run_orchestration(
    request: ChatRequest,
    tenant_id: str,
    user_id: str,
    db: AsyncSession,
    retriever: Retriever,
    reranker: Reranker,
    context_builder: ContextBuilder,
    llm: OpenAIService,
) -> tuple[str, AgentState]:
    conversation_id = bootstrap_conversation(request.conversation_id)

    # Resolve roles for permissions
    perm_repo = PermissionRepository(db)
    user_repo = UserRepository(db)
    perm_svc = PermissionService(perm_repo, user_repo)
    role_ids = await perm_svc.get_user_role_ids(user_id)

    user = await user_repo.get_by_id(user_id)
    is_admin = user.is_tenant_admin if user else False

    # Setup SQL Engine dependencies
    conn_repo = ConnectionRepository(db)
    schema_repo = SchemaRepository(db)
    conn_svc = ConnectionService(conn_repo)
    metadata_cache = MetadataCacheService(schema_repo, perm_repo)
    sql_engine = SQLEngine(conn_svc, metadata_cache, llm)

    orchestrator = ChatOrchestratorGraph(
        llm_service=llm,
        sql_engine=sql_engine,
        retriever=retriever,
        reranker=reranker,
        context_builder=context_builder,
    )

    initial_state: AgentState = {
        "user_message": request.message,
        "conversation_id": conversation_id,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "role_ids": role_ids,
        "is_admin": is_admin,
        "database_connection_ids": request.database_connection_ids,
        "knowledge_base_ids": request.knowledge_base_ids,
        "sources_used": [],
    }

    final_state = await orchestrator.run(initial_state)
    return conversation_id, final_state


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
    retriever: Retriever = Depends(get_retriever),
    reranker: Reranker = Depends(get_reranker),
    context_builder: ContextBuilder = Depends(get_context_builder),
    history_engine: HistoryEngine = Depends(get_history_engine),
    llm: OpenAIService = Depends(get_openai_service),
):
    conversation_id, final_state = await _run_orchestration(
        request, tenant_id, user_id, db, retriever, reranker, context_builder, llm
    )

    answer = final_state.get("final_answer", "")
    citations = final_state.get("citations", [])
    sources_used = final_state.get("sources_used", [])
    sql_summary = final_state.get("sql_summary")
    intent = final_state.get("detected_intent", "general")

    await history_engine.append_user_message(conversation_id, request.message)
    await history_engine.append_assistant_message(conversation_id, answer)

    return ChatResponse(
        message_id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        answer=answer,
        intent=intent,
        sources_used=sources_used,
        sql=sql_summary,
        citations=citations,
    )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
    retriever: Retriever = Depends(get_retriever),
    reranker: Reranker = Depends(get_reranker),
    context_builder: ContextBuilder = Depends(get_context_builder),
    history_engine: HistoryEngine = Depends(get_history_engine),
    llm: OpenAIService = Depends(get_openai_service),
):
    conversation_id, final_state = await _run_orchestration(
        request, tenant_id, user_id, db, retriever, reranker, context_builder, llm
    )

    answer = final_state.get("final_answer", "")

    async def event_generator():
        yield f"event: start\ndata: {conversation_id}\n\n"
        # Stream answer tokens
        for token in answer.split(" "):
            yield f"event: token\ndata: {token} \n\n"
        await history_engine.append_user_message(conversation_id, request.message)
        await history_engine.append_assistant_message(conversation_id, answer)
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")