import uuid
from datetime import datetime, timezone

from app.db.models.document_chunk import DocumentChunk
from app.db.models.file import File
from app.repositories.file_repo import FileRepository
from app.services.chunking.chunker_factory import ChunkerFactory
from app.services.ingestion.loader_factory import LoaderFactory
from app.services.llm.embeddings import EmbeddingService
from app.services.qdrant.ingestion import upsert_document_chunks
from app.utils.exceptions import FileProcessingError


class DocumentProcessor:
    """Orchestrates document processing: Load -> Chunk -> Embed -> Qdrant indexing -> DB updates."""

    def __init__(self, file_repo: FileRepository, embedding_service: EmbeddingService):
        self.file_repo = file_repo
        self.embedding_service = embedding_service

    async def process_file(self, file_id: str, tenant_id: str) -> None:
        db_file = await self.file_repo.get_by_id(file_id, tenant_id)
        if not db_file:
            raise FileProcessingError(f"File '{file_id}' not found")

        db_file.processing_status = "processing"
        await self.file_repo.update(db_file)

        try:
            # 1. Load pages
            loader = LoaderFactory.get_loader(db_file.storage_path)
            pages = loader.load(db_file.storage_path)

            # 2. Chunk pages
            chunker = ChunkerFactory.get_chunker()
            all_chunks: list[dict] = []
            db_chunks: list[DocumentChunk] = []

            total_extracted_text_len = 0
            page_count = len(pages)

            for page in pages:
                total_extracted_text_len += len(page.text)
                extracted_chunks = chunker.chunk(page.text, page_number=page.page_number)

                for c in extracted_chunks:
                    chunk_id = str(uuid.uuid4())
                    db_chunk = DocumentChunk(
                        id=uuid.UUID(chunk_id),
                        tenant_id=db_file.tenant_id,
                        knowledge_base_id=db_file.knowledge_base_id or uuid.uuid4(),
                        file_id=db_file.id,
                        chunk_index=c.chunk_index,
                        content=c.content,
                        page_number=c.page_number,
                        token_count=c.token_count,
                    )
                    db_chunks.append(db_chunk)

                    all_chunks.append({
                        "id": chunk_id,
                        "text": c.content,
                        "payload": {
                            "content": c.content,
                            "file_id": str(db_file.id),
                            "file_name": db_file.original_name,
                            "knowledge_base_id": str(db_file.knowledge_base_id) if db_file.knowledge_base_id else None,
                            "tenant_id": str(db_file.tenant_id),
                            "page_number": c.page_number,
                            "chunk_index": c.chunk_index,
                        }
                    })

            # 3. Embed chunks in batch
            texts = [c["text"] for c in all_chunks]
            if texts:
                vectors = await self.embedding_service.embed_batch(texts)
                for item, vector in zip(all_chunks, vectors):
                    item["vector"] = vector

                # 4. Upsert to Qdrant
                await upsert_document_chunks(all_chunks)

            # Save DB chunk records
            for db_c in db_chunks:
                self.file_repo.session.add(db_c)

            db_file.page_count = page_count
            db_file.extracted_text_length = total_extracted_text_len
            db_file.processing_status = "completed"
            db_file.processed_at = datetime.now(timezone.utc)
            await self.file_repo.update(db_file)

        except Exception as exc:
            db_file.processing_status = "failed"
            db_file.processing_error = str(exc)
            await self.file_repo.update(db_file)
            raise FileProcessingError(f"Failed to process file: {str(exc)}") from exc
