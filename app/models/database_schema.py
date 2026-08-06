from datetime import datetime
from typing import Any

from app.models.common import BaseSchema


class ColumnResponse(BaseSchema):
    id: str
    column_name: str
    data_type: str
    ordinal_position: int | None = None
    is_nullable: bool | None = None
    is_primary_key: bool
    is_foreign_key: bool
    is_sensitive: bool
    referenced_schema: str | None = None
    referenced_table: str | None = None
    referenced_column: str | None = None
    description: str | None = None
    sample_values: list[Any] = []


class TableResponse(BaseSchema):
    id: str
    connection_id: str
    schema_id: str | None = None
    table_name: str
    table_type: str
    description: str | None = None
    estimated_row_count: int | None = None
    primary_key_columns: list[str] = []
    is_enabled: bool
    is_sensitive: bool
    columns: list[ColumnResponse] = []
    created_at: datetime
    updated_at: datetime


class SchemaResponse(BaseSchema):
    id: str
    connection_id: str
    schema_name: str
    description: str | None = None
    tables: list[TableResponse] = []
    created_at: datetime
    updated_at: datetime
