from datetime import datetime
from typing import Any

from app.models.common import BaseSchema


class FileResponse(BaseSchema):
    id: str
    tenant_id: str
    knowledge_base_id: str | None = None
    original_name: str
    stored_name: str
    mime_type: str | None = None
    extension: str | None = None
    file_size_bytes: int | None = None
    processing_status: str
    processing_error: str | None = None
    page_count: int | None = None
    extracted_text_length: int | None = None
    metadata_info: dict[str, Any] = {}
    created_at: datetime
    processed_at: datetime | None = None


class FileUploadResponse(BaseSchema):
    file_id: str
    original_name: str
    file_size_bytes: int
    status: str
    message: str
