from app.core.config import get_settings
from app.services.llm.embeddings import EmbeddingService
from app.services.qdrant.search import ScoredChunk, vector_search
from app.utils.exceptions import RetrievalError


class Retriever:
    def __init__(self, embedding_service: EmbeddingService | None = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.settings = get_settings()

    async def retrieve(
        self,
        query: str,
        knowledge_base_ids: list[str] | None = None,
        top_k: int | None = None,
        with_vectors: bool = False,
    ) -> list[ScoredChunk]:
        top_k = top_k or self.settings.retrieval_top_k
        try:
            query_vector = await self.embedding_service.embed_text(query)
        except Exception as exc:
            raise RetrievalError(f"Failed to embed query: {exc}") from exc

        return await vector_search(
            query_vector=query_vector,
            top_k=top_k,
            knowledge_base_ids=knowledge_base_ids,
            with_vectors=with_vectors,
        )