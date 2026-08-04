from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.tenant_context import get_tenant_id
from app.models.query_execution import QueryExecutionResponse
from app.repositories.query_execution_repo import QueryExecutionRepository
from app.utils.exceptions import NotFoundError

router = APIRouter(tags=["sql"])


@router.get("/api/messages/{id}/sql", response_model=QueryExecutionResponse)
async def get_message_sql(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = QueryExecutionRepository(db)
    q = await repo.get_by_message_id(id)
    if not q:
        raise NotFoundError(f"No SQL execution record found for message '{id}'")

    return QueryExecutionResponse(
        id=str(q.id),
        tenant_id=str(q.tenant_id),
        conversation_id=str(q.conversation_id) if q.conversation_id else None,
        message_id=str(q.message_id) if q.message_id else None,
        connection_id=str(q.connection_id),
        generated_sql=q.generated_sql,
        normalized_sql=q.normalized_sql,
        query_type=q.query_type,
        validation_status=q.validation_status,
        validation_errors=q.validation_errors or [],
        execution_status=q.execution_status,
        execution_time_ms=q.execution_time_ms,
        returned_row_count=q.returned_row_count,
        result_preview=q.result_preview,
        error_code=q.error_code,
        error_message=q.error_message,
        created_at=q.created_at,
    )
