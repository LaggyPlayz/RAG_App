from datetime import datetime

from pydantic import Field

from app.models.common import BaseSchema


class RoleCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class RoleResponse(BaseSchema):
    id: str
    tenant_id: str
    name: str
    description: str | None = None
    created_at: datetime


class RoleAssignment(BaseSchema):
    user_id: str
    role_id: str
