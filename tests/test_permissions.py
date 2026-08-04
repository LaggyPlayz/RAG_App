import pytest
from app.services.database.metadata_cache import MetadataCacheService


class MockSchemaRepo:
    async def get_schemas_for_connection(self, conn_id):
        class MockCol:
            def __init__(self, cid, name, dtype, is_pk=False):
                self.id = cid
                self.column_name = name
                self.data_type = dtype
                self.is_primary_key = is_pk

        class MockTable:
            def __init__(self, tid, name, cols):
                self.id = tid
                self.table_name = name
                self.is_enabled = True
                self.columns = cols

        class MockSchema:
            def __init__(self, sname, tables):
                self.schema_name = sname
                self.tables = tables

        cols = [
            MockCol("col-1", "id", "INTEGER", True),
            MockCol("col-2", "name", "VARCHAR"),
            MockCol("col-3", "salary", "NUMERIC"),
        ]
        table = MockTable("tbl-1", "employees", cols)
        return [MockSchema("public", [table])]


class MockPermRepo:
    async def get_permissions_for_user(self, tenant_id, user_id, role_ids):
        class MockColPerm:
            def __init__(self, col_id, can_read):
                self.column_id = col_id
                self.can_read = can_read

        class MockTablePerm:
            def __init__(self, table_id, can_read, col_perms):
                self.table_id = table_id
                self.can_read = can_read
                self.row_filter = {}
                self.column_permissions = col_perms

        return [
            MockTablePerm(
                "tbl-1",
                can_read=True,
                col_perms=[
                    MockColPerm("col-1", True),
                    MockColPerm("col-2", True),
                    MockColPerm("col-3", False),  # Omit sensitive salary column
                ],
            )
        ]


@pytest.mark.asyncio
async def test_metadata_cache_filters_sensitive_columns():
    schema_repo = MockSchemaRepo()
    perm_repo = MockPermRepo()
    cache_svc = MetadataCacheService(schema_repo, perm_repo)

    result = await cache_svc.get_permitted_schema(
        connection_ids=["conn-1"],
        tenant_id="tenant-1",
        user_id="user-1",
        role_ids=[],
        is_admin=False,
    )

    assert "employees" in result
    cols = [c["name"] for c in result["employees"]["columns"]]
    assert "id" in cols
    assert "name" in cols
    assert "salary" not in cols  # Sensitive column filtered out by permissions
