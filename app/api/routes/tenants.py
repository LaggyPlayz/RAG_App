from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.db.models.tenant import Tenant
from app.models.tenant import TenantCreate, TenantResponse
from app.repositories.tenant_repo import TenantRepository
from app.utils.exceptions import DuplicateError

router = APIRouter(prefix="/api/tenants", tags=["tenants"])


@router.post("", response_model=TenantResponse)
async def create_tenant(request: TenantCreate, db: AsyncSession = Depends(get_db)):
    repo = TenantRepository(db)
    existing = await repo.get_by_code(request.code)
    if existing:
        raise DuplicateError(f"Tenant code '{request.code}' already exists")

    tenant = Tenant(
        name=request.name,
        code=request.code,
        settings=request.settings,
    )
    tenant = await repo.create(tenant)
    return TenantResponse(
        id=str(tenant.id),
        name=tenant.name,
        code=tenant.code,
        status=tenant.status,
        settings=tenant.settings,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )


@router.get("", response_model=list[TenantResponse])
async def list_tenants(db: AsyncSession = Depends(get_db)):
    repo = TenantRepository(db)
    tenants = await repo.list_all()
    return [
        TenantResponse(
            id=str(t.id),
            name=t.name,
            code=t.code,
            status=t.status,
            settings=t.settings,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )
        for t in tenants
    ]
