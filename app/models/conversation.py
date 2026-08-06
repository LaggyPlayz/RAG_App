from datetime import datetime
from typing import Any

from pydantic import Field

from app.models.common import BaseSchema, Citation


class MessageResponse(BaseSchema):
    id: str
    conversation_id: str
    role: str
    message_type: str
    content: str
    structured_content: dict[str, Any] | None = None
    detected_intent: str | None = None
    selected_sources: list[str] = []
    citations: list[Citation] = []
    status: str
    created_at: datetime


class ConversationCreate(BaseSchema):
    title: str | None = None
    active_connection_ids: list[str] = Field(default_factory=list)
    active_knowledge_base_ids: list[str] = Field(default_factory=list)


class ConversationResponse(BaseSchema):
    id: str
    tenant_id: str
    user_id: str
    title: str | None = None
    status: str
    active_connection_ids: list[str]
    active_knowledge_base_ids: list[str]
    last_message_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []
