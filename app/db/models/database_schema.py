import uuid
from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantMixin, TimestampMixin, generate_uuid


class DatabaseSchema(Base, TenantMixin, TimestampMixin):
    __tablename__ = "database_schemas"
    __table_args__ = (
        UniqueConstraint("connection_id", "schema_name", name="uq_database_schema"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    connection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("database_connections.id", ondelete="CASCADE"), nullable=False)
    schema_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    connection = relationship("DatabaseConnection", back_populates="schemas")
    tables = relationship("DatabaseTable", back_populates="schema_rel", cascade="all, delete-orphan")


class DatabaseTable(Base, TenantMixin, TimestampMixin):
    __tablename__ = "database_tables"
    __table_args__ = (
        UniqueConstraint("connection_id", "schema_id", "table_name", name="uq_database_table"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    connection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("database_connections.id", ondelete="CASCADE"), nullable=False)
    schema_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("database_schemas.id", ondelete="CASCADE"), nullable=True)
    table_name: Mapped[str] = mapped_column(String(255), nullable=False)
    table_type: Mapped[str] = mapped_column(String(50), nullable=False, default="table")
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    estimated_row_count: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    primary_key_columns: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    metadata_info: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)

    connection = relationship("DatabaseConnection", back_populates="tables")
    schema_rel = relationship("DatabaseSchema", back_populates="tables")
    columns = relationship("DatabaseColumn", back_populates="table", cascade="all, delete-orphan")


class DatabaseColumn(Base, TenantMixin, TimestampMixin):
    __tablename__ = "database_columns"
    __table_args__ = (
        UniqueConstraint("table_id", "column_name", name="uq_database_column"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    table_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("database_tables.id", ondelete="CASCADE"), nullable=False)
    column_name: Mapped[str] = mapped_column(String(255), nullable=False)
    data_type: Mapped[str] = mapped_column(String(100), nullable=False)
    ordinal_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_nullable: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_primary_key: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_foreign_key: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    referenced_schema: Mapped[str | None] = mapped_column(String(255), nullable=True)
    referenced_table: Mapped[str | None] = mapped_column(String(255), nullable=True)
    referenced_column: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    sample_values: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)

    table = relationship("DatabaseTable", back_populates="columns")
