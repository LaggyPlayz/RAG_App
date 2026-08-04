import uuid
from typing import Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic async repository providing CRUD operations with optional tenant isolation."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: uuid.UUID | str, tenant_id: uuid.UUID | str | None = None) -> ModelType | None:
        if isinstance(entity_id, str):
            entity_id = uuid.UUID(entity_id)

        query = select(self.model).where(self.model.id == entity_id)
        if tenant_id is not None:
            if isinstance(tenant_id, str):
                tenant_id = uuid.UUID(tenant_id)
            if hasattr(self.model, "tenant_id"):
                query = query.where(self.model.tenant_id == tenant_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_all(self, tenant_id: uuid.UUID | str | None = None, limit: int = 100, offset: int = 0) -> list[ModelType]:
        query = select(self.model)
        if tenant_id is not None:
            if isinstance(tenant_id, str):
                tenant_id = uuid.UUID(tenant_id)
            if hasattr(self.model, "tenant_id"):
                query = query.where(self.model.tenant_id == tenant_id)

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelType) -> ModelType:
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, entity_id: uuid.UUID | str, tenant_id: uuid.UUID | str | None = None) -> bool:
        if isinstance(entity_id, str):
            entity_id = uuid.UUID(entity_id)

        query = delete(self.model).where(self.model.id == entity_id)
        if tenant_id is not None:
            if isinstance(tenant_id, str):
                tenant_id = uuid.UUID(tenant_id)
            if hasattr(self.model, "tenant_id"):
                query = query.where(self.model.tenant_id == tenant_id)

        result = await self.session.execute(query)
        return result.rowcount > 0
