import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.knowledge_base import KnowledgeBase
from app.repositories.base import BaseRepository


class KnowledgeBaseRepository(BaseRepository[KnowledgeBase]):
    def __init__(self, session: AsyncSession):
        super().__init__(KnowledgeBase, session)

    async def get_with_files(self, kb_id: uuid.UUID | str, tenant_id: uuid.UUID | str | None = None) -> KnowledgeBase | None:
        if isinstance(kb_id, str):
            kb_id = uuid.UUID(kb_id)
        query = select(KnowledgeBase).where(KnowledgeBase.id == kb_id).options(selectinload(KnowledgeBase.files))
        if tenant_id is not None:
            if isinstance(tenant_id, str):
                tenant_id = uuid.UUID(tenant_id)
            query = query.where(KnowledgeBase.tenant_id == tenant_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str, tenant_id: uuid.UUID | str) -> KnowledgeBase | None:
        if isinstance(tenant_id, str):
            tenant_id = uuid.UUID(tenant_id)
        query = select(KnowledgeBase).where(KnowledgeBase.name == name, KnowledgeBase.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
