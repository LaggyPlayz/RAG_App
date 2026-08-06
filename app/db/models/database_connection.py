import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantMixin, TimestampMixin, generate_uuid


class DatabaseConnection(Base, TenantMixin, TimestampMixin):
    __tablename__ = "database_connections"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_database_connection_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    database_type: Mapped[str] = mapped_column(String(50), nullable=False)
    host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    database_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    encrypted_password: Mapped[str | None] = mapped_column(String, nullable=True)
    encrypted_connection_string: Mapped[str | None] = mapped_column(String, nullable=True)
    ssl_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ssl_settings: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    connection_options: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    last_tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_test_message: Mapped[str | None] = mapped_column(String, nullable=True)
    schema_sync_status: Mapped[str | None] = mapped_column(String(30), default="pending")
    last_schema_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    tenant = relationship("Tenant", back_populates="connections")
    schemas = relationship("DatabaseSchema", back_populates="connection", cascade="all, delete-orphan")
    tables = relationship("DatabaseTable", back_populates="connection", cascade="all, delete-orphan")
