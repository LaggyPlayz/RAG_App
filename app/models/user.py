from datetime import datetime

from pydantic import EmailStr, Field

from app.models.common import BaseSchema


class UserCreate(BaseSchema):
    email: EmailStr
    full_name: str | None = None
    password: str = Field(..., min_length=6)
    is_tenant_admin: bool = False


class UserUpdate(BaseSchema):
    full_name: str | None = None
    status: str | None = None
    is_tenant_admin: bool | None = None


class UserResponse(BaseSchema):
    id: str
    tenant_id: str
    email: str
    full_name: str | None = None
    status: str
    is_tenant_admin: bool
    created_at: datetime
    updated_at: datetime
