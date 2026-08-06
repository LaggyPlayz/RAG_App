import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import hash_password
from app.core.tenant_context import get_tenant_id, require_tenant_admin
from app.db.models.user import User
from app.models.user import UserCreate, UserResponse
from app.repositories.user_repo import UserRepository
from app.utils.exceptions import DuplicateError

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserResponse)
async def create_user(
    request: UserCreate,
    tenant_id: str = Depends(get_tenant_id),
    _admin: dict = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    existing = await repo.get_by_email(request.email, tenant_id=tenant_id)
    if existing:
        raise DuplicateError(f"User with email '{request.email}' already exists in tenant")

    user = User(
        tenant_id=uuid.UUID(tenant_id),
        email=request.email,
        full_name=request.full_name,
        password_hash=hash_password(request.password),
        is_tenant_admin=request.is_tenant_admin,
    )
    user = await repo.create(user)
    return UserResponse(
        id=str(user.id),
        tenant_id=str(user.tenant_id),
        email=user.email,
        full_name=user.full_name,
        status=user.status,
        is_tenant_admin=user.is_tenant_admin,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("", response_model=list[UserResponse])
async def list_users(
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    users = await repo.list_all(tenant_id=tenant_id)
    return [
        UserResponse(
            id=str(u.id),
            tenant_id=str(u.tenant_id),
            email=u.email,
            full_name=u.full_name,
            status=u.status,
            is_tenant_admin=u.is_tenant_admin,
            created_at=u.created_at,
            updated_at=u.updated_at,
        )
        for u in users
    ]
