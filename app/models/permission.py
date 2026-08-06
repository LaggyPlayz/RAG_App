from datetime import datetime
from typing import Any

from pydantic import Field

from app.models.common import BaseSchema


class ColumnPermissionCreate(BaseSchema):
    column_id: str
    can_read: bool = True
    can_filter: bool = True
    can_aggregate: bool = True
    mask_type: str | None = None


class ColumnPermissionResponse(BaseSchema):
    id: str
    column_id: str
    can_read: bool
    can_filter: bool
    can_aggregate: bool
    mask_type: str | None = None


class TablePermissionCreate(BaseSchema):
    role_id: str | None = None
    user_id: str | None = None
    connection_id: str
    table_id: str
    can_read: bool = True
    can_insert: bool = False
    can_update: bool = False
    can_delete: bool = False
    row_filter: dict[str, Any] = Field(default_factory=dict)
    column_permissions: list[ColumnPermissionCreate] = Field(default_factory=list)


class TablePermissionResponse(BaseSchema):
    id: str
    tenant_id: str
    role_id: str | None = None
    user_id: str | None = None
    connection_id: str
    table_id: str
    can_read: bool
    can_insert: bool
    can_update: bool
    can_delete: bool
    row_filter: dict[str, Any]
    column_permissions: list[ColumnPermissionResponse] = []
    created_at: datetime
