from datetime import datetime
from typing import Any

from app.models.common import BaseSchema


class AuditLogResponse(BaseSchema):
    id: str
    tenant_id: str | None = None
    user_id: str | None = None
    action: str
    resource_type: str | None = None
    resource_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    request_id: str | None = None
    details: dict[str, Any]
    created_at: datetime
