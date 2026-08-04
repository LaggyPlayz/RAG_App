from app.services.chunking.text_chunker import TextChunker


class ChunkerFactory:
    @staticmethod
    def get_chunker(chunking_config: dict | None = None):
        config = chunking_config or {}
        chunk_size = config.get("chunk_size", 500)
        chunk_overlap = config.get("chunk_overlap", 50)
        return TextChunker(chunk_size_tokens=chunk_size, chunk_overlap_tokens=chunk_overlap)
