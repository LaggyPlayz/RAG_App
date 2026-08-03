from dataclasses import dataclass

from qdrant_client.http import models as qmodels

from app.core.config import get_settings
from app.services.qdrant.client import get_qdrant_client
from app.utils.exceptions import VectorStoreError


@dataclass
class ScoredChunk:
    id: str
    score: float
    content: str
    file_id: str
    file_name: str
    knowledge_base_id: str | None
    page_number: int | None
    chunk_index: int | None
    vector: list[float] | None = None


def _build_filter(knowledge_base_ids: list[str]) -> qmodels.Filter | None:
    if not knowledge_base_ids:
        return None
    return qmodels.Filter(
        must=[qmodels.FieldCondition(key="knowledge_base_id", match=qmodels.MatchAny(any=knowledge_base_ids))]
    )


async def vector_search(
    query_vector: list[float],
    top_k: int,
    knowledge_base_ids: list[str] | None = None,
    collection_name: str | None = None,
    with_vectors: bool = False,
) -> list[ScoredChunk]:
    """Search Qdrant and map results into ScoredChunk.

    Assumes points were indexed (by the ingestion pipeline) with payload
    keys: content, file_id, file_name, knowledge_base_id, page_number,
    chunk_index. Adjust the payload.get(...) keys below if your ingestion
    pipeline uses different field names.
    """
    settings = get_settings()
    collection_name = collection_name or settings.qdrant_collection
    client = get_qdrant_client()

    try:
        results = await client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=_build_filter(knowledge_base_ids or []),
            with_vectors=with_vectors,
        )
    except Exception as exc:
        raise VectorStoreError(f"Vector search failed: {exc}") from exc

    chunks: list[ScoredChunk] = []
    for point in results:
        payload = point.payload or {}
        chunks.append(
            ScoredChunk(
                id=str(point.id),
                score=point.score,
                content=payload.get("content", ""),
                file_id=payload.get("file_id", ""),
                file_name=payload.get("file_name", "unknown"),
                knowledge_base_id=payload.get("knowledge_base_id"),
                page_number=payload.get("page_number"),
                chunk_index=payload.get("chunk_index"),
                vector=point.vector if with_vectors else None,
            )
        )
    return chunks