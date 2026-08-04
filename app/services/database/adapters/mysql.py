from sqlalchemy import create_engine, inspect

from app.services.database.adapters.base import BaseDialectAdapter, ColumnMeta, SchemaMeta, TableMeta


class MySQLAdapter(BaseDialectAdapter):
    def discover_schemas(self, connection_url: str) -> list[SchemaMeta]:
        engine = create_engine(connection_url)
        inspector = inspect(engine)

        default_schema = inspector.default_schema_name or "default"
        table_names = inspector.get_table_names(schema=default_schema)
        tables: list[TableMeta] = []

        for table_name in table_names:
            pk_constraint = inspector.get_pk_constraint(table_name, schema=default_schema)
            pk_cols = set(pk_constraint.get("constrained_columns", []) if pk_constraint else [])

            fk_constraints = inspector.get_foreign_keys(table_name, schema=default_schema)
            fk_map: dict[str, tuple[str | None, str | None, str | None]] = {}
            for fk in fk_constraints:
                ref_schema = fk.get("referred_schema")
                ref_table = fk.get("referred_table")
                constrained = fk.get("constrained_columns", [])
                referred = fk.get("referred_columns", [])
                for c_col, r_col in zip(constrained, referred):
                    fk_map[c_col] = (ref_schema, ref_table, r_col)

            raw_columns = inspector.get_columns(table_name, schema=default_schema)
            cols: list[ColumnMeta] = []

            for i, col in enumerate(raw_columns, start=1):
                col_name = col["name"]
                is_pk = col_name in pk_cols
                is_fk = col_name in fk_map
                ref_s, ref_t, ref_c = fk_map.get(col_name, (None, None, None))

                cols.append(
                    ColumnMeta(
                        name=col_name,
                        data_type=str(col["type"]),
                        ordinal_position=i,
                        is_nullable=col.get("nullable", True),
                        is_primary_key=is_pk,
                        is_foreign_key=is_fk,
                        referenced_schema=ref_s,
                        referenced_table=ref_t,
                        referenced_column=ref_c,
                    )
                )

            tables.append(
                TableMeta(
                    schema_name=default_schema,
                    table_name=table_name,
                    columns=cols,
                    primary_keys=list(pk_cols),
                )
            )

        engine.dispose()
        return [SchemaMeta(schema_name=default_schema, tables=tables)]
