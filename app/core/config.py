"""Application settings, loaded from environment variables / .env.

Only the fields needed by the retrieval + chat orchestration slice are
defined here. If app/core/config.py already has other fields (SQL,
ingestion, auth, etc.) in your repo, merge those in rather than
overwriting them wholesale.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # LLM / embeddings
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    embedding_dimensions: int = Field(default=1536, alias="EMBEDDING_DIMENSIONS")

    # Qdrant
    qdrant_host: str = Field(default="localhost", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")
    qdrant_collection: str = Field(default="documents", alias="QDRANT_COLLECTION")

    # Redis (conversation history store)
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")

    # Retrieval
    retrieval_top_k: int = Field(default=20, alias="RETRIEVAL_TOP_K")
    rerank_top_k: int = Field(default=6, alias="RERANK_TOP_K")
    rerank_mmr_lambda: float = Field(default=0.5, alias="RERANK_MMR_LAMBDA")
    context_max_tokens: int = Field(default=3000, alias="CONTEXT_MAX_TOKENS")

    # Conversation history
    history_max_messages: int = Field(default=12, alias="HISTORY_MAX_MESSAGES")
    history_max_tokens: int = Field(default=2000, alias="HISTORY_MAX_TOKENS")
    history_ttl_seconds: int = Field(default=60 * 60 * 24 * 7, alias="HISTORY_TTL_SECONDS")


@lru_cache
def get_settings() -> Settings:
    return Settings()