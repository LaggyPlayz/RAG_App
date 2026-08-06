import uuid

from app.db.models.database_schema import DatabaseSchema
from app.repositories.permission_repo import PermissionRepository
from app.repositories.schema_repo import SchemaRepository


class MetadataCacheService:
    def __init__(self, schema_repo: SchemaRepository, permission_repo: PermissionRepository):
        self.schema_repo = schema_repo
        self.permission_repo = permission_repo

    async def get_permitted_schema(
        self,
        connection_ids: list[str],
        tenant_id: str,
        user_id: str,
        role_ids: list[str],
        is_admin: bool = False,
    ) -> dict:
        """Retrieve schema metadata for given connections, filtered by user table/column permissions.

        Returns a dictionary structure suitable for prompt injection:
        {
          "table_name": {
             "columns": [{"name": "id", "type": "INTEGER", "primary_key": True}, ...],
             "row_filter": {"user_id": "{user_id}"}
          }
        }
        """
        permitted_schema: dict = {}

        # Fetch permissions for non-admins
        user_permissions: dict[str, dict] = {}
        if not is_admin:
            perms = await self.permission_repo.get_permissions_for_user(tenant_id, user_id, role_ids)
            for p in perms:
                table_id_str = str(p.table_id)
                col_perms = {
                    str(cp.column_id): {"can_read": cp.can_read, "mask_type": getattr(cp, "mask_type", None)}
                    for cp in p.column_permissions
                }
                user_permissions[table_id_str] = {
                    "can_read": p.can_read,
                    "row_filter": p.row_filter,
                    "column_permissions": col_perms,
                }

        for conn_id in connection_ids:
            schemas = await self.schema_repo.get_schemas_for_connection(conn_id)
            for schema in schemas:
                for table in schema.tables:
                    if not table.is_enabled:
                        continue

                    table_id_str = str(table.id)

                    # Admin gets access to all enabled tables
                    if is_admin:
                        cols = [
                            {"name": c.column_name, "type": c.data_type, "is_pk": c.is_primary_key, "mask_type": None}
                            for c in table.columns
                        ]
                        permitted_schema[table.table_name] = {
                            "schema": schema.schema_name,
                            "columns": cols,
                            "row_filter": {},
                        }
                    else:
                        perm = user_permissions.get(table_id_str)
                        if not perm or not perm.get("can_read", True):
                            continue

                        col_map = perm.get("column_permissions", {})
                        cols = []
                        for c in table.columns:
                            col_id_str = str(c.id)
                            col_perm = col_map.get(col_id_str)
                            if isinstance(col_perm, dict):
                                if not col_perm.get("can_read", True):
                                    continue
                                mask_type = col_perm.get("mask_type")
                            elif col_perm is False:
                                continue
                            else:
                                mask_type = None

                            cols.append({
                                "name": c.column_name,
                                "type": c.data_type,
                                "is_pk": c.is_primary_key,
                                "mask_type": mask_type,
                            })

                        permitted_schema[table.table_name] = {
                            "schema": schema.schema_name,
                            "columns": cols,
                            "row_filter": perm.get("row_filter", {}),
                        }

        return permitted_schema

