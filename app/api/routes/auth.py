from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user_payload,
    verify_password,
    verify_token,
)
from app.models.auth import LoginRequest, RefreshTokenRequest, TokenResponse, UserProfile
from app.repositories.user_repo import UserRepository
from app.utils.exceptions import AuthenticationError

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(request.email)
    if not user or not user.password_hash:
        raise AuthenticationError("Invalid email or password")

    if not verify_password(request.password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    payload = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "is_tenant_admin": user.is_tenant_admin,
    }

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    payload = verify_token(request.refresh_token, expected_type="refresh")
    new_payload = {
        "sub": payload["sub"],
        "tenant_id": payload["tenant_id"],
        "email": payload.get("email"),
        "is_tenant_admin": payload.get("is_tenant_admin", False),
    }

    access_token = create_access_token(new_payload)
    new_refresh = create_refresh_token(new_payload)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=1800,
    )


@router.get("/me", response_model=UserProfile)
async def get_me(payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(payload["sub"])
    if not user:
        raise AuthenticationError("User not found")

    return UserProfile(
        id=str(user.id),
        tenant_id=str(user.tenant_id),
        email=user.email,
        full_name=user.full_name,
        is_tenant_admin=user.is_tenant_admin,
        status=user.status,
    )
