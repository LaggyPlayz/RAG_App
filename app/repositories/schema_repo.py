import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.database_schema import DatabaseColumn, DatabaseSchema, DatabaseTable
from app.repositories.base import BaseRepository


class SchemaRepository(BaseRepository[DatabaseSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(DatabaseSchema, session)

    async def get_schemas_for_connection(self, connection_id: uuid.UUID | str) -> list[DatabaseSchema]:
        if isinstance(connection_id, str):
            connection_id = uuid.UUID(connection_id)
        query = (
            select(DatabaseSchema)
            .where(DatabaseSchema.connection_id == connection_id)
            .options(selectinload(DatabaseSchema.tables).selectinload(DatabaseTable.columns))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_tables_for_connection(self, connection_id: uuid.UUID | str) -> list[DatabaseTable]:
        if isinstance(connection_id, str):
            connection_id = uuid.UUID(connection_id)
        query = (
            select(DatabaseTable)
            .where(DatabaseTable.connection_id == connection_id)
            .options(selectinload(DatabaseTable.columns))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def clear_connection_metadata(self, connection_id: uuid.UUID | str) -> None:
        if isinstance(connection_id, str):
            connection_id = uuid.UUID(connection_id)
        query = delete(DatabaseSchema).where(DatabaseSchema.connection_id == connection_id)
        await self.session.execute(query)
