import uuid

from app.db.models.permission import ColumnPermission, TablePermission
from app.models.permission import TablePermissionCreate, TablePermissionResponse
from app.repositories.permission_repo import PermissionRepository
from app.repositories.user_repo import UserRepository


class PermissionService:
    def __init__(self, permission_repo: PermissionRepository, user_repo: UserRepository):
        self.permission_repo = permission_repo
        self.user_repo = user_repo

    async def get_user_role_ids(self, user_id: str) -> list[str]:
        user = await self.user_repo.get_with_roles(user_id)
        if not user:
            return []
        return [str(role.id) for role in user.roles]

    async def grant_table_permission(
        self, tenant_id: str, data: TablePermissionCreate
    ) -> TablePermission:
        tp = TablePermission(
            tenant_id=uuid.UUID(tenant_id),
            role_id=uuid.UUID(data.role_id) if data.role_id else None,
            user_id=uuid.UUID(data.user_id) if data.user_id else None,
            connection_id=uuid.UUID(data.connection_id),
            table_id=uuid.UUID(data.table_id),
            can_read=data.can_read,
            can_insert=data.can_insert,
            can_update=data.can_update,
            can_delete=data.can_delete,
            row_filter=data.row_filter,
        )
        tp = await self.permission_repo.create(tp)

        for col_p in data.column_permissions:
            cp = ColumnPermission(
                table_permission_id=tp.id,
                column_id=uuid.UUID(col_p.column_id),
                can_read=col_p.can_read,
                can_filter=col_p.can_filter,
                can_aggregate=col_p.can_aggregate,
                mask_type=col_p.mask_type,
            )
            self.permission_repo.session.add(cp)

        await self.permission_repo.session.flush()
        return tp
