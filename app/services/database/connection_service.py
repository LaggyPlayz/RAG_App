import uuid
from datetime import datetime, timezone

from app.core.encryption import decrypt_value, encrypt_value
from app.db.models.database_connection import DatabaseConnection
from app.models.database_connection import ConnectionCreate, ConnectionResponse, ConnectionTestResult, ConnectionUpdate
from app.repositories.connection_repo import ConnectionRepository
from app.services.database.connection_tester import test_connection
from app.services.database.dialect_resolver import build_sqlalchemy_url
from app.utils.exceptions import DuplicateError, NotFoundError


class ConnectionService:
    def __init__(self, connection_repo: ConnectionRepository):
        self.repo = connection_repo

    async def create_connection(
        self, tenant_id: str, user_id: str, data: ConnectionCreate
    ) -> DatabaseConnection:
        existing = await self.repo.get_by_name(data.name, tenant_id)
        if existing:
            raise DuplicateError(f"Connection with name '{data.name}' already exists in tenant")

        encrypted_pass = encrypt_value(data.password) if data.password else None
        encrypted_conn_str = encrypt_value(data.connection_string) if data.connection_string else None

        conn = DatabaseConnection(
            tenant_id=uuid.UUID(tenant_id),
            created_by=uuid.UUID(user_id) if user_id else None,
            name=data.name,
            database_type=data.database_type,
            host=data.host,
            port=data.port,
            database_name=data.database_name,
            username=data.username,
            encrypted_password=encrypted_pass,
            encrypted_connection_string=encrypted_conn_str,
            ssl_enabled=data.ssl_enabled,
            ssl_settings=data.ssl_settings,
            connection_options=data.connection_options,
            status="pending",
        )
        return await self.repo.create(conn)

    async def test_existing_connection(
        self, connection_id: str, tenant_id: str
    ) -> ConnectionTestResult:
        conn = await self.repo.get_by_id(connection_id, tenant_id)
        if not conn:
            raise NotFoundError(f"Database connection '{connection_id}' not found")

        plain_pass = decrypt_value(conn.encrypted_password) if conn.encrypted_password else None
        plain_conn_str = decrypt_value(conn.encrypted_connection_string) if conn.encrypted_connection_string else None

        result = test_connection(
            db_type=conn.database_type,
            host=conn.host,
            port=conn.port,
            database_name=conn.database_name,
            username=conn.username,
            password=plain_pass,
            connection_string=plain_conn_str,
        )

        conn.last_tested_at = datetime.now(timezone.utc)
        conn.last_test_message = result.message
        conn.status = "connected" if result.success else "failed"
        await self.repo.update(conn)

        return result

    def get_decrypted_connection_url(self, conn: DatabaseConnection) -> str:
        plain_pass = decrypt_value(conn.encrypted_password) if conn.encrypted_password else None
        plain_conn_str = decrypt_value(conn.encrypted_connection_string) if conn.encrypted_connection_string else None

        return build_sqlalchemy_url(
            db_type=conn.database_type,
            host=conn.host,
            port=conn.port,
            database_name=conn.database_name,
            username=conn.username,
            password=plain_pass,
            connection_string=plain_conn_str,
        )
