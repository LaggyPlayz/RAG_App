from app.agents.state import AgentState
from app.core.config import get_settings
from app.services.retrieval.context_builder import ContextBuilder
from app.services.retrieval.reranker import Reranker
from app.services.retrieval.retriever import Retriever

_settings = get_settings()


class DocumentAgentNode:
    def __init__(self, retriever: Retriever, reranker: Reranker, context_builder: ContextBuilder):
        self.retriever = retriever
        self.reranker = reranker
        self.context_builder = context_builder

    async def retrieve(self, state: AgentState) -> AgentState:
        msg = state.get("user_message", "")
        kb_ids = state.get("knowledge_base_ids", [])

        if not kb_ids:
            state["document_context"] = None
            state["citations"] = []
            return state

        query_vec = await self.retriever.embedding_service.embed_text(msg)
        candidates = await self.retriever.retrieve(
            query=msg,
            knowledge_base_ids=kb_ids,
            top_k=_settings.retrieval_top_k,
            with_vectors=True,
        )

        ranked = self.reranker.rerank(query_vec, candidates, top_k=_settings.rerank_top_k)
        context_text, citations = self.context_builder.build(ranked)

        state["document_context"] = context_text
        state["citations"] = citations

        sources = state.get("sources_used", [])
        if citations and "documents" not in sources:
            sources.append("documents")
        state["sources_used"] = sources

        return state
