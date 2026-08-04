from typing import Any, TypedDict, Annotated
from app.models.common import Citation
from app.models.chat import SQLExecutionSummary


class AgentState(TypedDict, total=False):
    # Inputs
    user_message: str
    conversation_id: str
    tenant_id: str
    user_id: str
    role_ids: list[str]
    is_admin: bool
    database_connection_ids: list[str]
    knowledge_base_ids: list[str]

    # Processed states
    detected_intent: str  # general, database, document, hybrid, clarification
    sources_used: list[str]

    # Database Retrieval
    sql_summary: SQLExecutionSummary | None
    sql_markdown_result: str | None
    raw_sql_rows: list[dict[str, Any]] | None

    # Document Retrieval
    document_context: str | None
    citations: list[Citation]

    # Final Output
    final_answer: str
