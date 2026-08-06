import os
import uuid
from datetime import datetime, timezone

from fastapi import UploadFile

from app.core.config import get_settings
from app.db.models.file import File
from app.repositories.file_repo import FileRepository
from app.utils.exceptions import FileTooLargeError, UnsupportedFileTypeError
from app.core.constants import SUPPORTED_FILE_EXTENSIONS

_settings = get_settings()


class UploadService:
    def __init__(self, file_repo: FileRepository):
        self.file_repo = file_repo

    async def save_uploaded_file(
        self,
        file: UploadFile,
        tenant_id: str,
        user_id: str,
        knowledge_base_id: str | None = None,
    ) -> File:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in SUPPORTED_FILE_EXTENSIONS:
            raise UnsupportedFileTypeError(f"Unsupported file type: '{ext}'")

        # Create upload directory if it doesn't exist
        target_dir = os.path.join(_settings.upload_dir, tenant_id)
        os.makedirs(target_dir, exist_ok=True)

        unique_name = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(target_dir, unique_name)

        content = await file.read()
        file_size = len(content)

        max_bytes = _settings.max_upload_size_mb * 1024 * 1024
        if file_size > max_bytes:
            raise FileTooLargeError(f"File size ({file_size} bytes) exceeds limit of {_settings.max_upload_size_mb} MB")

        with open(file_path, "wb") as f:
            f.write(content)

        db_file = File(
            tenant_id=uuid.UUID(tenant_id),
            knowledge_base_id=uuid.UUID(knowledge_base_id) if knowledge_base_id else None,
            uploaded_by=uuid.UUID(user_id) if user_id else None,
            original_name=file.filename or "unknown",
            stored_name=unique_name,
            storage_path=file_path,
            mime_type=file.content_type,
            extension=ext,
            file_size_bytes=file_size,
            processing_status="pending",
        )
        return await self.file_repo.create(db_file)
