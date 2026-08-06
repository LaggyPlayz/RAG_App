from collections.abc import AsyncGenerator

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.utils.exceptions import LLMServiceError

_settings = get_settings()
_client = AsyncOpenAI(api_key=_settings.openai_api_key)


class OpenAIService:
    def __init__(self, model: str | None = None):
        self.model = model or _settings.openai_model

    async def complete(self, messages: list[dict]) -> str:
        try:
            response = await _client.chat.completions.create(model=self.model, messages=messages)
        except Exception as exc:
            raise LLMServiceError(f"Chat completion failed: {exc}") from exc
        return response.choices[0].message.content or ""

    async def stream(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        try:
            response_stream = await _client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )
            async for chunk in response_stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as exc:
            raise LLMServiceError(f"Chat completion stream failed: {exc}") from exc