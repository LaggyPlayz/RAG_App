from fastapi import APIRouter, Depends, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.tenant_context import get_tenant_id, get_user_id
from app.models.file import FileResponse, FileUploadResponse
from app.repositories.file_repo import FileRepository
from app.services.documents.upload_service import UploadService
from app.utils.exceptions import NotFoundError
from app.workers.ingestion_worker import trigger_file_ingestion

from app.api.dependencies import get_audit_service
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/files", tags=["documents"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile,
    knowledge_base_id: str | None = Form(None),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
    audit_svc: AuditService = Depends(get_audit_service),
):
    file_repo = FileRepository(db)
    upload_svc = UploadService(file_repo)

    db_file = await upload_svc.save_uploaded_file(
        file=file,
        tenant_id=tenant_id,
        user_id=user_id,
        knowledge_base_id=knowledge_base_id,
    )

    # Trigger async processing in background worker
    trigger_file_ingestion(str(db_file.id), tenant_id)

    await audit_svc.log_event(
        action="file_uploaded",
        tenant_id=tenant_id,
        user_id=user_id,
        resource_type="file",
        resource_id=str(db_file.id),
        details={"original_name": db_file.original_name},
    )

    return FileUploadResponse(
        file_id=str(db_file.id),
        original_name=db_file.original_name,
        file_size_bytes=db_file.file_size_bytes or 0,
        status="pending",
        message="File uploaded successfully and processing started",
    )



@router.get("", response_model=list[FileResponse])
async def list_files(
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = FileRepository(db)
    files = await repo.list_all(tenant_id=tenant_id)
    return [
        FileResponse(
            id=str(f.id),
            tenant_id=str(f.tenant_id),
            knowledge_base_id=str(f.knowledge_base_id) if f.knowledge_base_id else None,
            original_name=f.original_name,
            stored_name=f.stored_name,
            mime_type=f.mime_type,
            extension=f.extension,
            file_size_bytes=f.file_size_bytes,
            processing_status=f.processing_status,
            processing_error=f.processing_error,
            page_count=f.page_count,
            extracted_text_length=f.extracted_text_length,
            metadata_info=f.metadata_info or {},
            created_at=f.created_at,
            processed_at=f.processed_at,
        )
        for f in files
    ]


@router.get("/{id}", response_model=FileResponse)
async def get_file(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = FileRepository(db)
    f = await repo.get_by_id(id, tenant_id=tenant_id)
    if not f:
        raise NotFoundError(f"File '{id}' not found")

    return FileResponse(
        id=str(f.id),
        tenant_id=str(f.tenant_id),
        knowledge_base_id=str(f.knowledge_base_id) if f.knowledge_base_id else None,
        original_name=f.original_name,
        stored_name=f.stored_name,
        mime_type=f.mime_type,
        extension=f.extension,
        file_size_bytes=f.file_size_bytes,
        processing_status=f.processing_status,
        processing_error=f.processing_error,
        page_count=f.page_count,
        extracted_text_length=f.extracted_text_length,
        metadata_info=f.metadata_info or {},
        created_at=f.created_at,
        processed_at=f.processed_at,
    )


@router.delete("/{id}")
async def delete_file(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
    audit_svc: AuditService = Depends(get_audit_service),
):
    repo = FileRepository(db)
    deleted = await repo.delete(id, tenant_id=tenant_id)
    if not deleted:
        raise NotFoundError(f"File '{id}' not found")

    await audit_svc.log_event(
        action="file_deleted",
        tenant_id=tenant_id,
        user_id=user_id,
        resource_type="file",
        resource_id=id,
    )

    return {"status": "ok", "message": f"File '{id}' deleted successfully"}



@router.post("/{id}/reprocess")
async def reprocess_file(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = FileRepository(db)
    f = await repo.get_by_id(id, tenant_id=tenant_id)
    if not f:
        raise NotFoundError(f"File '{id}' not found")

    trigger_file_ingestion(id, tenant_id)
    return {"status": "ok", "message": f"Reprocessing triggered for file '{id}'"}
