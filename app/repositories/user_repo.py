import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str, tenant_id: uuid.UUID | str | None = None) -> User | None:
        query = select(User).where(User.email == email).options(selectinload(User.roles))
        if tenant_id is not None:
            if isinstance(tenant_id, str):
                tenant_id = uuid.UUID(tenant_id)
            query = query.where(User.tenant_id == tenant_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_roles(self, user_id: uuid.UUID | str) -> User | None:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        query = select(User).where(User.id == user_id).options(selectinload(User.roles))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
