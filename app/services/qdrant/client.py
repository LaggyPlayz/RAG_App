from functools import lru_cache

from qdrant_client import AsyncQdrantClient

from app.core.config import get_settings


@lru_cache
def get_qdrant_client() -> AsyncQdrantClient:
    settings = get_settings()
    return AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)