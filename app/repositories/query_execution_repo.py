import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.query_execution import QueryExecution
from app.repositories.base import BaseRepository


class QueryExecutionRepository(BaseRepository[QueryExecution]):
    def __init__(self, session: AsyncSession):
        super().__init__(QueryExecution, session)

    async def get_by_message_id(self, message_id: uuid.UUID | str) -> QueryExecution | None:
        if isinstance(message_id, str):
            message_id = uuid.UUID(message_id)
        query = select(QueryExecution).where(QueryExecution.message_id == message_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
