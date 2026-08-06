"""Application settings, loaded from environment variables / .env.

Extended to support PostgreSQL, JWT auth, encryption, file storage,
SQL execution safety, and all platform configuration.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # ── PostgreSQL ──
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/rag_platform",
        alias="DATABASE_URL",
    )
    database_url_sync: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/rag_platform",
        alias="DATABASE_URL_SYNC",
    )

    # ── JWT Authentication ──
    jwt_secret_key: str = Field(default="change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    # ── Credential Encryption ──
    encryption_key: str = Field(default="change-me", alias="ENCRYPTION_KEY")

    # ── LLM / Embeddings ──
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    embedding_dimensions: int = Field(default=1536, alias="EMBEDDING_DIMENSIONS")

    # ── Qdrant ──
    qdrant_host: str = Field(default="localhost", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")
    qdrant_collection: str = Field(default="documents", alias="QDRANT_COLLECTION")

    # ── Redis ──
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")

    # ── File Storage ──
    upload_dir: str = Field(default="./uploads", alias="UPLOAD_DIR")
    max_upload_size_mb: int = Field(default=50, alias="MAX_UPLOAD_SIZE_MB")

    # ── Retrieval ──
    retrieval_top_k: int = Field(default=20, alias="RETRIEVAL_TOP_K")
    rerank_top_k: int = Field(default=6, alias="RERANK_TOP_K")
    rerank_mmr_lambda: float = Field(default=0.5, alias="RERANK_MMR_LAMBDA")
    context_max_tokens: int = Field(default=3000, alias="CONTEXT_MAX_TOKENS")

    # ── Conversation History ──
    history_max_messages: int = Field(default=12, alias="HISTORY_MAX_MESSAGES")
    history_max_tokens: int = Field(default=2000, alias="HISTORY_MAX_TOKENS")
    history_ttl_seconds: int = Field(default=60 * 60 * 24 * 7, alias="HISTORY_TTL_SECONDS")

    # ── SQL Execution Safety ──
    sql_query_timeout_seconds: int = Field(default=30, alias="SQL_QUERY_TIMEOUT_SECONDS")
    sql_max_result_rows: int = Field(default=1000, alias="SQL_MAX_RESULT_ROWS")


@lru_cache
def get_settings() -> Settings:
    return Settings()