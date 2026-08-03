import json

from app.core.config import get_settings
from app.models.history import ConversationHistory, HistoryMessage
from app.services.redis.client import get_redis_client


def _key(conversation_id: str) -> str:
    return f"conversation:{conversation_id}:history"


class HistoryStore:
    def __init__(self):
        self.settings = get_settings()
        self.redis = get_redis_client()

    async def get(self, conversation_id: str) -> ConversationHistory:
        raw = await self.redis.get(_key(conversation_id))
        if not raw:
            return ConversationHistory(conversation_id=conversation_id, messages=[])
        return ConversationHistory(**json.loads(raw))

    async def save(self, history: ConversationHistory) -> None:
        await self.redis.set(
            _key(history.conversation_id),
            history.model_dump_json(),
            ex=self.settings.history_ttl_seconds,
        )

    async def append(self, conversation_id: str, role: str, content: str) -> ConversationHistory:
        history = await self.get(conversation_id)
        history.messages.append(HistoryMessage(role=role, content=content))
        await self.save(history)
        return history

    async def delete(self, conversation_id: str) -> None:
        await self.redis.delete(_key(conversation_id))