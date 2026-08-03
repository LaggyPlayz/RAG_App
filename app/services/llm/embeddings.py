from openai import AsyncOpenAI

from app.core.config import get_settings
from app.utils.exceptions import LLMServiceError

_settings = get_settings()
_client = AsyncOpenAI(api_key=_settings.openai_api_key)


class EmbeddingService:
    def __init__(self, model: str | None = None):
        self.model = model or _settings.embedding_model

    async def embed_text(self, text: str) -> list[float]:
        vectors = await self.embed_batch([text])
        return vectors[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            response = await _client.embeddings.create(model=self.model, input=texts)
        except Exception as exc:
            raise LLMServiceError(f"Embedding request failed: {exc}") from exc
        return [item.embedding for item in response.data]