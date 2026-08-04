import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.role import Role, UserRole
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)

    async def get_by_name(self, name: str, tenant_id: uuid.UUID | str) -> Role | None:
        if isinstance(tenant_id, str):
            tenant_id = uuid.UUID(tenant_id)
        query = select(Role).where(Role.name == name, Role.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def assign_role_to_user(self, user_id: uuid.UUID | str, role_id: uuid.UUID | str) -> UserRole:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        if isinstance(role_id, str):
            role_id = uuid.UUID(role_id)

        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)
        await self.session.flush()
        return user_role

    async def remove_role_from_user(self, user_id: uuid.UUID | str, role_id: uuid.UUID | str) -> bool:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        if isinstance(role_id, str):
            role_id = uuid.UUID(role_id)

        query = delete(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        result = await self.session.execute(query)
        return result.rowcount > 0
