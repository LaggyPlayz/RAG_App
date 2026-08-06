from datetime import datetime
from typing import Any

from pydantic import Field

from app.models.common import BaseSchema


class TenantCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=100)
    settings: dict[str, Any] = Field(default_factory=dict)


class TenantResponse(BaseSchema):
    id: str
    name: str
    code: str
    status: str
    settings: dict[str, Any]
    created_at: datetime
    updated_at: datetime
