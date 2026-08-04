from datetime import datetime
from typing import Any

from app.models.common import BaseSchema


class QueryExecutionResponse(BaseSchema):
    id: str
    tenant_id: str
    conversation_id: str | None = None
    message_id: str | None = None
    connection_id: str
    generated_sql: str
    normalized_sql: str | None = None
    query_type: str | None = None
    validation_status: str
    validation_errors: list[Any] = []
    execution_status: str | None = None
    execution_time_ms: int | None = None
    returned_row_count: int | None = None
    result_preview: dict[str, Any] | None = None
    error_code: str | None = None
    error_message: str | None = None
    created_at: datetime
