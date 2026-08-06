import asyncio
import logging

from app.workers.tasks import run_ingestion_task

logger = logging.getLogger(__name__)


def trigger_file_ingestion(file_id: str, tenant_id: str) -> None:
    """Helper to dispatch background ingestion task."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(run_ingestion_task(file_id, tenant_id))
    except RuntimeError:
        # Fallback if no event loop running in current thread
        asyncio.run(run_ingestion_task(file_id, tenant_id))
