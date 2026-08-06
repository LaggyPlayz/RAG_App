from app.core.config import get_settings
from app.models.history import ConversationHistory, HistoryMessage
from app.services.history.store import HistoryStore
from app.services.history.window import apply_window


class HistoryEngine:
    def __init__(self, store: HistoryStore | None = None):
        self.store = store or HistoryStore()
        self.settings = get_settings()

    async def get_windowed_history(self, conversation_id: str) -> list[HistoryMessage]:
        history = await self.store.get(conversation_id)
        return apply_window(
            history.messages,
            max_messages=self.settings.history_max_messages,
            max_tokens=self.settings.history_max_tokens,
        )

    async def get_full_history(self, conversation_id: str) -> ConversationHistory:
        return await self.store.get(conversation_id)

    async def append_user_message(self, conversation_id: str, content: str) -> None:
        await self.store.append(conversation_id, role="user", content=content)

    async def append_assistant_message(self, conversation_id: str, content: str) -> None:
        await self.store.append(conversation_id, role="assistant", content=content)

    async def clear(self, conversation_id: str) -> None:
        await self.store.delete(conversation_id)