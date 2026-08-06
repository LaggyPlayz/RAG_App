from app.services.audit_service import AuditService
from app.core.database import get_db
from functools import lru_cache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings, get_settings
from app.services.history.engine import HistoryEngine
from app.services.llm.embeddings import EmbeddingService
from app.services.llm.openai_service import OpenAIService
from app.services.retrieval.context_builder import ContextBuilder
from app.services.retrieval.reranker import Reranker
from app.services.retrieval.retriever import Retriever


def get_settings_dep() -> Settings:
    return get_settings()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


@lru_cache
def get_openai_service() -> OpenAIService:
    return OpenAIService()


@lru_cache
def get_retriever() -> Retriever:
    return Retriever(embedding_service=get_embedding_service())


@lru_cache
def get_reranker() -> Reranker:
    return Reranker()


@lru_cache
def get_context_builder() -> ContextBuilder:
    return ContextBuilder()


def get_history_engine() -> HistoryEngine:
    # Not cached: HistoryEngine itself is stateless aside from the Redis
    # client, which is already a cached singleton — cheap to construct
    # per request, avoids any shared mutable state across requests.
    return HistoryEngine()


from app.repositories.audit_repo import AuditRepository
from app.services.audit_service import AuditService


def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    repo = AuditRepository(db)
    return AuditService(repo)

