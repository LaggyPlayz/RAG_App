from datetime import datetime
from typing import Any

from pydantic import Field

from app.models.common import BaseSchema


class ConnectionCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    database_type: str = Field(..., description="postgresql, mysql, sqlserver, oracle, sqlite")
    host: str | None = None
    port: int | None = None
    database_name: str | None = None
    username: str | None = None
    password: str | None = None
    connection_string: str | None = None
    ssl_enabled: bool = False
    ssl_settings: dict[str, Any] = Field(default_factory=dict)
    connection_options: dict[str, Any] = Field(default_factory=dict)


class ConnectionUpdate(BaseSchema):
    name: str | None = None
    host: str | None = None
    port: int | None = None
    database_name: str | None = None
    username: str | None = None
    password: str | None = None
    connection_string: str | None = None
    ssl_enabled: bool | None = None
    is_active: bool | None = None


class ConnectionResponse(BaseSchema):
    id: str
    tenant_id: str
    name: str
    database_type: str
    host: str | None = None
    port: int | None = None
    database_name: str | None = None
    username: str | None = None
    ssl_enabled: bool
    status: str
    last_tested_at: datetime | None = None
    last_test_message: str | None = None
    schema_sync_status: str | None = None
    last_schema_sync_at: datetime | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ConnectionTestResult(BaseSchema):
    success: bool
    message: str
    latency_ms: int | None = None
    details: dict[str, Any] = Field(default_factory=dict)
