import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(AuditLog, session)

    async def log_action(
        self,
        action: str,
        tenant_id: uuid.UUID | str | None = None,
        user_id: uuid.UUID | str | None = None,
        resource_type: str | None = None,
        resource_id: uuid.UUID | str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict | None = None,
    ) -> AuditLog:
        if isinstance(tenant_id, str):
            tenant_id = uuid.UUID(tenant_id)
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        if isinstance(resource_id, str):
            resource_id = uuid.UUID(resource_id)

        audit_entry = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
        )
        return await self.create(audit_entry)
