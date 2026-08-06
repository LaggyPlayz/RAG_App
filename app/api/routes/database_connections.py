from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.tenant_context import get_tenant_id, get_user_id
from app.models.database_connection import ConnectionCreate, ConnectionResponse, ConnectionTestResult
from app.repositories.connection_repo import ConnectionRepository
from app.repositories.schema_repo import SchemaRepository
from app.services.database.connection_service import ConnectionService
from app.services.database.schema_discovery import SchemaDiscoveryService
from app.utils.exceptions import NotFoundError

router = APIRouter(prefix="/api/database-connections", tags=["database-connections"])


@router.post("", response_model=ConnectionResponse)
async def create_connection(
    request: ConnectionCreate,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ConnectionRepository(db)
    svc = ConnectionService(repo)
    conn = await svc.create_connection(tenant_id, user_id, request)

    return ConnectionResponse(
        id=str(conn.id),
        tenant_id=str(conn.tenant_id),
        name=conn.name,
        database_type=conn.database_type,
        host=conn.host,
        port=conn.port,
        database_name=conn.database_name,
        username=conn.username,
        ssl_enabled=conn.ssl_enabled,
        status=conn.status,
        last_tested_at=conn.last_tested_at,
        last_test_message=conn.last_test_message,
        schema_sync_status=conn.schema_sync_status,
        last_schema_sync_at=conn.last_schema_sync_at,
        is_active=conn.is_active,
        created_at=conn.created_at,
        updated_at=conn.updated_at,
    )


@router.get("", response_model=list[ConnectionResponse])
async def list_connections(
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ConnectionRepository(db)
    connections = await repo.list_all(tenant_id=tenant_id)
    return [
        ConnectionResponse(
            id=str(c.id),
            tenant_id=str(c.tenant_id),
            name=c.name,
            database_type=c.database_type,
            host=c.host,
            port=c.port,
            database_name=c.database_name,
            username=c.username,
            ssl_enabled=c.ssl_enabled,
            status=c.status,
            last_tested_at=c.last_tested_at,
            last_test_message=c.last_test_message,
            schema_sync_status=c.schema_sync_status,
            last_schema_sync_at=c.last_schema_sync_at,
            is_active=c.is_active,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in connections
    ]


@router.get("/{id}", response_model=ConnectionResponse)
async def get_connection(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ConnectionRepository(db)
    conn = await repo.get_by_id(id, tenant_id=tenant_id)
    if not conn:
        raise NotFoundError(f"Connection '{id}' not found")

    return ConnectionResponse(
        id=str(conn.id),
        tenant_id=str(conn.tenant_id),
        name=conn.name,
        database_type=conn.database_type,
        host=conn.host,
        port=conn.port,
        database_name=conn.database_name,
        username=conn.username,
        ssl_enabled=conn.ssl_enabled,
        status=conn.status,
        last_tested_at=conn.last_tested_at,
        last_test_message=conn.last_test_message,
        schema_sync_status=conn.schema_sync_status,
        last_schema_sync_at=conn.last_schema_sync_at,
        is_active=conn.is_active,
        created_at=conn.created_at,
        updated_at=conn.updated_at,
    )


@router.post("/{id}/test", response_model=ConnectionTestResult)
async def test_connection(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ConnectionRepository(db)
    svc = ConnectionService(repo)
    return await svc.test_existing_connection(id, tenant_id)


@router.post("/{id}/sync-schema")
async def sync_schema(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    conn_repo = ConnectionRepository(db)
    schema_repo = SchemaRepository(db)
    conn_svc = ConnectionService(conn_repo)
    discovery_svc = SchemaDiscoveryService(conn_svc, conn_repo, schema_repo)

    await discovery_svc.sync_schema(id, tenant_id)
    return {"status": "ok", "message": "Schema sync completed successfully"}
