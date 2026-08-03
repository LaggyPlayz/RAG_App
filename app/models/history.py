from datetime import datetime

from pydantic import Field

from app.models.common import BaseSchema


class HistoryMessage(BaseSchema):
    role: str  # "user" | "assistant" | "system"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationHistory(BaseSchema):
    conversation_id: str
    messages: list[HistoryMessage] = Field(default_factory=list)