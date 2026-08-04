import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.file import File
from app.repositories.base import BaseRepository


class FileRepository(BaseRepository[File]):
    def __init__(self, session: AsyncSession):
        super().__init__(File, session)

    async def list_by_knowledge_base(self, kb_id: uuid.UUID | str) -> list[File]:
        if isinstance(kb_id, str):
            kb_id = uuid.UUID(kb_id)
        query = select(File).where(File.knowledge_base_id == kb_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
