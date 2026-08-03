from app.core.config import get_settings
from app.models.common import Citation
from app.services.qdrant.search import ScoredChunk
from app.utils.token_utils import count_tokens, truncate_to_tokens


class ContextBuilder:
    def __init__(self, max_tokens: int | None = None):
        settings = get_settings()
        self.max_tokens = max_tokens or settings.context_max_tokens

    def build(self, chunks: list[ScoredChunk]) -> tuple[str, list[Citation]]:
        """Build a numbered, source-tagged context string within a token budget.

        Returns (context_text, citations) where citation order matches
        the [n] numbering used in context_text, so the LLM's inline
        citations line up with the citations list returned to the client.
        """
        parts: list[str] = []
        citations: list[Citation] = []
        used_tokens = 0

        for i, chunk in enumerate(chunks, start=1):
            content = chunk.content.strip()
            if not content:
                continue

            page_suffix = f", p.{chunk.page_number}" if chunk.page_number is not None else ""
            snippet = f"[{i}] (source: {chunk.file_name}{page_suffix})\n{content}"
            snippet_tokens = count_tokens(snippet)

            if used_tokens + snippet_tokens > self.max_tokens:
                remaining = self.max_tokens - used_tokens
                if remaining <= 0:
                    break
                snippet = truncate_to_tokens(snippet, remaining)
                snippet_tokens = remaining

            parts.append(snippet)
            used_tokens += snippet_tokens
            citations.append(
                Citation(
                    file_id=chunk.file_id,
                    file_name=chunk.file_name,
                    page_number=chunk.page_number,
                    chunk_index=chunk.chunk_index,
                    score=chunk.score,
                )
            )

            if used_tokens >= self.max_tokens:
                break

        return "\n\n".join(parts), citations