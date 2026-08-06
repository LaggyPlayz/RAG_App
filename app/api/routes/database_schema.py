from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.tenant_context import get_tenant_id
from app.models.database_schema import ColumnResponse, SchemaResponse, TableResponse
from app.repositories.schema_repo import SchemaRepository

router = APIRouter(prefix="/api/database-connections", tags=["database-schema"])


@router.get("/{id}/schemas", response_model=list[SchemaResponse])
async def get_connection_schemas(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = SchemaRepository(db)
    schemas = await repo.get_schemas_for_connection(id)

    res = []
    for s in schemas:
        tables_res = []
        for t in s.tables:
            cols_res = [
                ColumnResponse(
                    id=str(c.id),
                    column_name=c.column_name,
                    data_type=c.data_type,
                    ordinal_position=c.ordinal_position,
                    is_nullable=c.is_nullable,
                    is_primary_key=c.is_primary_key,
                    is_foreign_key=c.is_foreign_key,
                    is_sensitive=c.is_sensitive,
                    referenced_schema=c.referenced_schema,
                    referenced_table=c.referenced_table,
                    referenced_column=c.referenced_column,
                    description=c.description,
                    sample_values=c.sample_values or [],
                )
                for c in t.columns
            ]
            tables_res.append(
                TableResponse(
                    id=str(t.id),
                    connection_id=str(t.connection_id),
                    schema_id=str(t.schema_id) if t.schema_id else None,
                    table_name=t.table_name,
                    table_type=t.table_type,
                    description=t.description,
                    estimated_row_count=t.estimated_row_count,
                    primary_key_columns=t.primary_key_columns or [],
                    is_enabled=t.is_enabled,
                    is_sensitive=t.is_sensitive,
                    columns=cols_res,
                    created_at=t.created_at,
                    updated_at=t.updated_at,
                )
            )

        res.append(
            SchemaResponse(
                id=str(s.id),
                connection_id=str(s.connection_id),
                schema_name=s.schema_name,
                description=s.description,
                tables=tables_res,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
        )

    return res


@router.get("/{id}/tables", response_model=list[TableResponse])
async def get_connection_tables(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = SchemaRepository(db)
    tables = await repo.get_tables_for_connection(id)

    res = []
    for t in tables:
        cols_res = [
            ColumnResponse(
                id=str(c.id),
                column_name=c.column_name,
                data_type=c.data_type,
                ordinal_position=c.ordinal_position,
                is_nullable=c.is_nullable,
                is_primary_key=c.is_primary_key,
                is_foreign_key=c.is_foreign_key,
                is_sensitive=c.is_sensitive,
                referenced_schema=c.referenced_schema,
                referenced_table=c.referenced_table,
                referenced_column=c.referenced_column,
                description=c.description,
                sample_values=c.sample_values or [],
            )
            for c in t.columns
        ]
        res.append(
            TableResponse(
                id=str(t.id),
                connection_id=str(t.connection_id),
                schema_id=str(t.schema_id) if t.schema_id else None,
                table_name=t.table_name,
                table_type=t.table_type,
                description=t.description,
                estimated_row_count=t.estimated_row_count,
                primary_key_columns=t.primary_key_columns or [],
                is_enabled=t.is_enabled,
                is_sensitive=t.is_sensitive,
                columns=cols_res,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
        )

    return res
