from datetime import datetime
from typing import Any

from pydantic import Field

from app.models.common import BaseSchema


class KnowledgeBaseCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    embedding_model: str | None = None
    chunking_config: dict[str, Any] = Field(default_factory=dict)


class KnowledgeBaseResponse(BaseSchema):
    id: str
    tenant_id: str
    name: str
    description: str | None = None
    embedding_model: str | None = None
    chunking_config: dict[str, Any]
    file_count: int = 0
    created_at: datetime
    updated_at: datetime
