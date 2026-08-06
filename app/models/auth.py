from pydantic import EmailStr, Field

from app.models.common import BaseSchema


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class UserProfile(BaseSchema):
    id: str
    tenant_id: str
    email: str
    full_name: str | None = None
    is_tenant_admin: bool
    status: str
