from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.tenant import Tenant
from app.repositories.base import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    def __init__(self, session: AsyncSession):
        super().__init__(Tenant, session)

    async def get_by_code(self, code: str) -> Tenant | None:
        query = select(Tenant).where(Tenant.code == code)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
