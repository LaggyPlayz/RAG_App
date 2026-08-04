from typing import Any

from pydantic import Field

from app.models.common import BaseSchema, Citation


class SQLExecutionSummary(BaseSchema):
    query_execution_id: str | None = None
    query: str
    row_count: int = 0
    result_preview: list[dict[str, Any]] | None = None
    error: str | None = None


class ChatRequest(BaseSchema):
    conversation_id: str | None = None
    message: str = Field(..., min_length=1)
    database_connection_ids: list[str] = Field(default_factory=list)
    knowledge_base_ids: list[str] = Field(default_factory=list)
    stream: bool = False


class ChatResponse(BaseSchema):
    message_id: str
    conversation_id: str
    answer: str
    intent: str = "general"
    sources_used: list[str] = Field(default_factory=list)
    sql: SQLExecutionSummary | None = None
    citations: list[Citation] = Field(default_factory=list)