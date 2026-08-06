import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import hash_password
from app.db.models.tenant import Tenant
from app.db.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/seed")
async def seed_initial_data(db: AsyncSession = Depends(get_db)):
    """Seed initial default tenant and admin user for development/testing."""
    from sqlalchemy import select
    res = await db.execute(select(Tenant).where(Tenant.code == "default-tenant"))
    existing_tenant = res.scalar_one_or_none()

    if not existing_tenant:
        tenant = Tenant(
            name="Default Tenant",
            code="default-tenant",
            settings={},
        )
        db.add(tenant)
        await db.flush()

        admin_user = User(
            tenant_id=tenant.id,
            email="admin@example.com",
            full_name="Default Admin User",
            password_hash=hash_password("admin123"),
            is_tenant_admin=True,
        )
        db.add(admin_user)
        await db.commit()

        return {
            "status": "seeded",
            "tenant_id": str(tenant.id),
            "tenant_code": tenant.code,
            "admin_email": admin_user.email,
            "admin_password": "admin123",
        }

    return {"status": "already_exists", "tenant_id": str(existing_tenant.id)}
