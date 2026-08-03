from qdrant_client.http import models as qmodels

from app.core.config import get_settings
from app.services.qdrant.client import get_qdrant_client
from app.utils.exceptions import VectorStoreError


async def ensure_collection(collection_name: str | None = None, vector_size: int | None = None) -> None:
    """Create the collection if it doesn't exist yet. Called on app startup.

    Does NOT touch ingestion — this only guarantees the collection the
    retrieval path reads from is present, so a fresh environment doesn't
    fail with "collection not found" before any documents are ingested.
    """
    settings = get_settings()
    collection_name = collection_name or settings.qdrant_collection
    vector_size = vector_size or settings.embedding_dimensions
    client = get_qdrant_client()
    try:
        exists = await client.collection_exists(collection_name)
        if not exists:
            await client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
            )
    except Exception as exc:
        raise VectorStoreError(f"Could not ensure collection '{collection_name}': {exc}") from exc