from pydantic import Field

from app.models.common import BaseSchema, Citation


class ChatRequest(BaseSchema):
    conversation_id: str | None = None
    message: str = Field(..., min_length=1)
    knowledge_base_ids: list[str] = Field(default_factory=list)
    stream: bool = False


class ChatResponse(BaseSchema):
    message_id: str
    conversation_id: str
    answer: str
    sources_used: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)