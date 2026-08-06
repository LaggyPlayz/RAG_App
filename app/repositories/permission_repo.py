import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.permission import ColumnPermission, TablePermission
from app.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[TablePermission]):
    def __init__(self, session: AsyncSession):
        super().__init__(TablePermission, session)

    async def get_permissions_for_user(
        self, tenant_id: uuid.UUID | str, user_id: uuid.UUID | str, role_ids: list[uuid.UUID | str]
    ) -> list[TablePermission]:
        if isinstance(tenant_id, str):
            tenant_id = uuid.UUID(tenant_id)
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        converted_role_ids = [uuid.UUID(r) if isinstance(r, str) else r for r in role_ids]

        conditions = [TablePermission.user_id == user_id]
        if converted_role_ids:
            conditions.append(TablePermission.role_id.in_(converted_role_ids))

        from sqlalchemy import or_
        query = (
            select(TablePermission)
            .where(TablePermission.tenant_id == tenant_id, or_(*conditions))
            .options(selectinload(TablePermission.column_permissions))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_permissions_for_table(self, table_id: uuid.UUID | str) -> list[TablePermission]:
        if isinstance(table_id, str):
            table_id = uuid.UUID(table_id)
        query = (
            select(TablePermission)
            .where(TablePermission.table_id == table_id)
            .options(selectinload(TablePermission.column_permissions))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
