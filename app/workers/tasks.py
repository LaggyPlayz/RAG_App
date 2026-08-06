import asyncio
import logging

from app.core.database import async_session_factory
from app.repositories.file_repo import FileRepository
from app.services.documents.document_processor import DocumentProcessor
from app.services.llm.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


async def run_ingestion_task(file_id: str, tenant_id: str) -> None:
    """Async background task that processes an uploaded file."""
    async with async_session_factory() as session:
        file_repo = FileRepository(session)
        embedding_service = EmbeddingService()
        processor = DocumentProcessor(file_repo, embedding_service)

        try:
            logger.info(f"Starting ingestion background task for file {file_id}")
            await processor.process_file(file_id, tenant_id)
            await session.commit()
            logger.info(f"Successfully processed file {file_id}")
        except Exception as exc:
            await session.rollback()
            logger.error(f"Error processing file {file_id}: {str(exc)}")
