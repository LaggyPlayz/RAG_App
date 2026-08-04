import uuid

from qdrant_client.http import models as qmodels

from app.core.config import get_settings
from app.services.qdrant.client import get_qdrant_client
from app.utils.exceptions import VectorStoreError

_settings = get_settings()


async def upsert_document_chunks(
    chunks: list[dict],
    collection_name: str | None = None,
) -> None:
    """Upsert embedded document chunks to Qdrant.

    Each dict in `chunks` must contain:
    - id: str / UUID
    - vector: list[float]
    - payload: dict (content, file_id, file_name, knowledge_base_id, tenant_id, page_number, chunk_index)
    """
    if not chunks:
        return

    collection = collection_name or _settings.qdrant_collection
    client = get_qdrant_client()

    points = [
        qmodels.PointStruct(
            id=c["id"] if isinstance(c["id"], str) else str(c["id"]),
            vector=c["vector"],
            payload=c["payload"],
        )
        for c in chunks
    ]

    try:
        await client.upsert(
            collection_name=collection,
            points=points,
        )
    except Exception as exc:
        raise VectorStoreError(f"Failed to upsert points to Qdrant: {str(exc)}") from exc
