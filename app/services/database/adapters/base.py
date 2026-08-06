from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ColumnMeta:
    name: str
    data_type: str
    ordinal_position: int
    is_nullable: bool
    is_primary_key: bool = False
    is_foreign_key: bool = False
    referenced_schema: str | None = None
    referenced_table: str | None = None
    referenced_column: str | None = None
    sample_values: list[Any] = field(default_factory=list)


@dataclass
class TableMeta:
    schema_name: str
    table_name: str
    table_type: str = "table"
    columns: list[ColumnMeta] = field(default_factory=list)
    primary_keys: list[str] = field(default_factory=list)
    estimated_row_count: int | None = None


@dataclass
class SchemaMeta:
    schema_name: str
    tables: list[TableMeta] = field(default_factory=list)


class BaseDialectAdapter(ABC):
    """Abstract interface for inspecting remote source database metadata."""

    @abstractmethod
    def discover_schemas(self, connection_url: str) -> list[SchemaMeta]:
        """Discover schemas, tables, columns, primary keys, and foreign keys."""
        pass
