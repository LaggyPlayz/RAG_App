import uuid
from datetime import datetime, timezone

from app.core.constants import DB_TYPE_MYSQL, DB_TYPE_POSTGRESQL
from app.db.models.database_connection import DatabaseConnection
from app.db.models.database_schema import DatabaseColumn, DatabaseSchema, DatabaseTable
from app.repositories.connection_repo import ConnectionRepository
from app.repositories.schema_repo import SchemaRepository
from app.services.database.adapters.mysql import MySQLAdapter
from app.services.database.adapters.postgresql import PostgreSQLAdapter
from app.services.database.connection_service import ConnectionService
from app.utils.exceptions import NotFoundError, SchemaDiscoveryError


class SchemaDiscoveryService:
    def __init__(
        self,
        connection_service: ConnectionService,
        connection_repo: ConnectionRepository,
        schema_repo: SchemaRepository,
    ):
        self.connection_service = connection_service
        self.connection_repo = connection_repo
        self.schema_repo = schema_repo

    def _get_adapter(self, db_type: str):
        db_type_lower = db_type.lower()
        if db_type_lower in (DB_TYPE_POSTGRESQL, "postgres"):
            return PostgreSQLAdapter()
        elif db_type_lower in (DB_TYPE_MYSQL, "mariadb"):
            return MySQLAdapter()
        else:
            # Fallback to PostgreSQL adapter if compliant
            return PostgreSQLAdapter()

    async def sync_schema(self, connection_id: str, tenant_id: str) -> None:
        conn = await self.connection_repo.get_by_id(connection_id, tenant_id)
        if not conn:
            raise NotFoundError(f"Connection '{connection_id}' not found")

        conn.schema_sync_status = "in_progress"
        await self.connection_repo.update(conn)

        try:
            url = self.connection_service.get_decrypted_connection_url(conn)
            adapter = self._get_adapter(conn.database_type)

            discovered_schemas = adapter.discover_schemas(url)

            # Clear old cached metadata for this connection
            await self.schema_repo.clear_connection_metadata(conn.id)

            tenant_uuid = uuid.UUID(tenant_id)
            conn_uuid = uuid.UUID(connection_id)

            for schema_meta in discovered_schemas:
                db_schema = DatabaseSchema(
                    tenant_id=tenant_uuid,
                    connection_id=conn_uuid,
                    schema_name=schema_meta.schema_name,
                )
                db_schema = await self.schema_repo.create(db_schema)

                for table_meta in schema_meta.tables:
                    db_table = DatabaseTable(
                        tenant_id=tenant_uuid,
                        connection_id=conn_uuid,
                        schema_id=db_schema.id,
                        table_name=table_meta.table_name,
                        table_type=table_meta.table_type,
                        primary_key_columns=table_meta.primary_keys,
                        estimated_row_count=table_meta.estimated_row_count,
                    )
                    self.schema_repo.session.add(db_table)
                    await self.schema_repo.session.flush()

                    for col_meta in table_meta.columns:
                        db_column = DatabaseColumn(
                            tenant_id=tenant_uuid,
                            table_id=db_table.id,
                            column_name=col_meta.name,
                            data_type=col_meta.data_type,
                            ordinal_position=col_meta.ordinal_position,
                            is_nullable=col_meta.is_nullable,
                            is_primary_key=col_meta.is_primary_key,
                            is_foreign_key=col_meta.is_foreign_key,
                            referenced_schema=col_meta.referenced_schema,
                            referenced_table=col_meta.referenced_table,
                            referenced_column=col_meta.referenced_column,
                        )
                        self.schema_repo.session.add(db_column)

            conn.schema_sync_status = "completed"
            conn.last_schema_sync_at = datetime.now(timezone.utc)
            await self.connection_repo.update(conn)

        except Exception as exc:
            conn.schema_sync_status = "failed"
            await self.connection_repo.update(conn)
            raise SchemaDiscoveryError(f"Schema sync failed: {str(exc)}") from exc
