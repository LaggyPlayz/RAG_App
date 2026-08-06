import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.database_connection import DatabaseConnection
from app.repositories.base import BaseRepository


class ConnectionRepository(BaseRepository[DatabaseConnection]):
    def __init__(self, session: AsyncSession):
        super().__init__(DatabaseConnection, session)

    async def get_by_name(self, name: str, tenant_id: uuid.UUID | str) -> DatabaseConnection | None:
        if isinstance(tenant_id, str):
            tenant_id = uuid.UUID(tenant_id)
        query = select(DatabaseConnection).where(
            DatabaseConnection.name == name,
            DatabaseConnection.tenant_id == tenant_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_active(self, tenant_id: uuid.UUID | str) -> list[DatabaseConnection]:
        if isinstance(tenant_id, str):
            tenant_id = uuid.UUID(tenant_id)
        query = select(DatabaseConnection).where(
            DatabaseConnection.tenant_id == tenant_id,
            DatabaseConnection.is_active == True,
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
