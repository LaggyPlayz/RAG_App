import uuid
from typing import Any

from app.repositories.audit_repo import AuditRepository


class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self.repo = audit_repo

    async def log_event(
        self,
        action: str,
        tenant_id: str | None = None,
        user_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        await self.repo.log_action(
            action=action,
            tenant_id=tenant_id,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )
