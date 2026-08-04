import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.conversation import Conversation
from app.db.models.message import Message
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Conversation, session)

    async def get_with_messages(self, conv_id: uuid.UUID | str, tenant_id: uuid.UUID | str | None = None) -> Conversation | None:
        if isinstance(conv_id, str):
            conv_id = uuid.UUID(conv_id)
        query = (
            select(Conversation)
            .where(Conversation.id == conv_id)
            .options(selectinload(Conversation.messages).selectinload(Message.citations))
        )
        if tenant_id is not None:
            if isinstance(tenant_id, str):
                tenant_id = uuid.UUID(tenant_id)
            query = query.where(Conversation.tenant_id == tenant_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID | str, limit: int = 50, offset: int = 0) -> list[Conversation]:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_message(self, message: Message) -> Message:
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message
