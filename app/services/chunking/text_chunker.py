from app.services.chunking.base import BaseChunker, Chunk
from app.utils.token_utils import count_tokens


class TextChunker(BaseChunker):
    """Recursive character/token-based text splitter with overlap."""

    def __init__(self, chunk_size_tokens: int = 500, chunk_overlap_tokens: int = 50):
        self.chunk_size = chunk_size_tokens
        self.chunk_overlap = chunk_overlap_tokens

    def chunk(self, text: str, page_number: int | None = None) -> list[Chunk]:
        if not text or not text.strip():
            return []

        paragraphs = text.split("\n\n")
        chunks: list[Chunk] = []

        current_text = ""
        current_tokens = 0
        chunk_idx = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_tokens = count_tokens(para)

            if current_tokens + para_tokens > self.chunk_size and current_text:
                chunks.append(
                    Chunk(
                        chunk_index=chunk_idx,
                        content=current_text.strip(),
                        page_number=page_number,
                        token_count=current_tokens,
                    )
                )
                chunk_idx += 1
                # Simple overlap heuristic
                words = current_text.split()
                overlap_words = words[-max(10, self.chunk_overlap // 2):]
                current_text = " ".join(overlap_words) + "\n\n" + para
                current_tokens = count_tokens(current_text)
            else:
                if current_text:
                    current_text += "\n\n" + para
                else:
                    current_text = para
                current_tokens += para_tokens

        if current_text.strip():
            chunks.append(
                Chunk(
                    chunk_index=chunk_idx,
                    content=current_text.strip(),
                    page_number=page_number,
                    token_count=count_tokens(current_text.strip()),
                )
            )

        return chunks
