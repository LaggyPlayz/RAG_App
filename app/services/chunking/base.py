from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    chunk_index: int
    content: str
    page_number: int | None = None
    section_title: str | None = None
    token_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, text: str, page_number: int | None = None) -> list[Chunk]:
        """Split text into chunks."""
        pass
