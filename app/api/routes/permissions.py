from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.tenant_context import get_tenant_id, require_tenant_admin
from app.models.permission import ColumnPermissionResponse, TablePermissionCreate, TablePermissionResponse
from app.repositories.permission_repo import PermissionRepository
from app.repositories.user_repo import UserRepository
from app.services.permission_service import PermissionService

from app.api.dependencies import get_audit_service
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/permissions", tags=["permissions"])


@router.post("/table", response_model=TablePermissionResponse)
async def create_table_permission(
    request: TablePermissionCreate,
    tenant_id: str = Depends(get_tenant_id),
    admin_payload: dict = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db),
    audit_svc: AuditService = Depends(get_audit_service),
):
    perm_repo = PermissionRepository(db)
    user_repo = UserRepository(db)
    service = PermissionService(perm_repo, user_repo)

    tp = await service.grant_table_permission(tenant_id, request)

    await audit_svc.log_event(
        action="permission_granted",
        tenant_id=tenant_id,
        user_id=admin_payload.get("sub"),
        resource_type="table_permission",
        resource_id=str(tp.id),
        details={"table_id": request.table_id, "connection_id": request.connection_id},
    )


    cols_res = [
        ColumnPermissionResponse(
            id=str(cp.id),
            column_id=str(cp.column_id),
            can_read=cp.can_read,
            can_filter=cp.can_filter,
            can_aggregate=cp.can_aggregate,
            mask_type=cp.mask_type,
        )
        for cp in tp.column_permissions
    ]

    return TablePermissionResponse(
        id=str(tp.id),
        tenant_id=str(tp.tenant_id),
        role_id=str(tp.role_id) if tp.role_id else None,
        user_id=str(tp.user_id) if tp.user_id else None,
        connection_id=str(tp.connection_id),
        table_id=str(tp.table_id),
        can_read=tp.can_read,
        can_insert=tp.can_insert,
        can_update=tp.can_update,
        can_delete=tp.can_delete,
        row_filter=tp.row_filter or {},
        column_permissions=cols_res,
        created_at=tp.created_at,
    )
