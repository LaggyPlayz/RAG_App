import re
import sqlglot
from sqlglot import exp

from app.core.constants import (
    SQL_ALLOWED_STATEMENTS,
    SQL_BLOCKED_STATEMENTS,
    SQL_BLOCKED_SYSTEM_SCHEMAS,
)
from app.utils.exceptions import SQLValidationError


class SQLGuard:
    """SQL validator and sanitizer using SQLGlot parsing rules.

    Enforces mandatory security controls:
    1. Blocks non-SELECT / DDL / DML statements.
    2. Blocks multiple statements in a single query.
    3. Blocks SQL comments and system schema access.
    4. Validates that referenced tables exist in the allowed schema.
    """

    def inject_row_filters(
        self,
        parsed: exp.Expression,
        permitted_schema: dict,
        tenant_id: str | None = None,
        user_id: str | None = None,
        dialect: str = "postgres",
    ) -> exp.Expression:
        """Inject mandatory tenant and row-level security filters into the SQL AST."""
        if not permitted_schema:
            return parsed

        # Normalize schema lookup (lowercase table names)
        schema_map = {k.lower(): v for k, v in permitted_schema.items()}

        for table_node in list(parsed.find_all(exp.Table)):
            table_name = table_node.name.lower()
            table_info = schema_map.get(table_name)
            if not table_info:
                continue

            row_filter = table_info.get("row_filter")
            if not row_filter:
                continue

            alias = table_node.alias_or_name

            # Handle dict filters e.g. {"tenant_id": "{tenant_id}", "department": "Sales"}
            conditions = []
            if isinstance(row_filter, dict):
                sql_cond = row_filter.get("sql") or row_filter.get("condition")
                if sql_cond:
                    formatted_cond = str(sql_cond).format(
                        tenant_id=tenant_id or "",
                        user_id=user_id or "",
                    )
                    parsed_cond = sqlglot.parse_one(formatted_cond, read=dialect)
                    if parsed_cond:
                        conditions.append(parsed_cond)
                else:
                    for col, val in row_filter.items():
                        if col in ("sql", "condition"):
                            continue
                        val_str = str(val).format(
                            tenant_id=tenant_id or "",
                            user_id=user_id or "",
                        )
                        # Construct alias.col = 'val' condition
                        col_expr = exp.column(col, table=alias if alias != table_name else None)
                        val_expr = exp.Literal.string(val_str)
                        conditions.append(exp.EQ(this=col_expr, expression=val_expr))
            elif isinstance(row_filter, str):
                formatted_cond = row_filter.format(
                    tenant_id=tenant_id or "",
                    user_id=user_id or "",
                )
                parsed_cond = sqlglot.parse_one(formatted_cond, read=dialect)
                if parsed_cond:
                    conditions.append(parsed_cond)

            for cond in conditions:
                parsed = parsed.where(cond, copy=False)

        return parsed

    def validate_and_sanitize(
        self,
        sql: str,
        dialect: str = "postgres",
        allowed_tables: set[str] | None = None,
        permitted_schema: dict | None = None,
        tenant_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        if not sql or not sql.strip():
            raise SQLValidationError("Empty SQL query")

        # 1. Block multiple statements (semicolon check unless trailing)
        clean_sql = sql.strip().rstrip(";")
        if ";" in clean_sql:
            raise SQLValidationError("Multiple SQL statements are strictly forbidden")

        # 2. Block SQL comment patterns
        if re.search(r"--|/\*|\*/", clean_sql):
            raise SQLValidationError("SQL comments are forbidden for security reasons")

        # 3. Parse with SQLGlot
        try:
            parsed = sqlglot.parse_one(clean_sql, read=dialect)
        except Exception as exc:
            raise SQLValidationError(f"SQL Syntax Error: {str(exc)}") from exc

        if parsed is None:
            raise SQLValidationError("Failed to parse SQL query")

        # 4. Enforce statement type (Only SELECT and CTEs allowed)
        if not isinstance(parsed, (exp.Select, exp.Union)):
            raise SQLValidationError(f"Only SELECT queries are allowed. Got statement type: {type(parsed).__name__}")

        if permitted_schema and allowed_tables is None:
            allowed_tables = set(permitted_schema.keys())

        # 5. Inspect AST for forbidden keywords / functions / schemas
        for node in parsed.walk():
            # Check for blocked statement nodes
            node_type = type(node).__name__.upper()
            if node_type in SQL_BLOCKED_STATEMENTS:
                raise SQLValidationError(f"Destructive or forbidden statement '{node_type}' detected")

            # Check table references
            if isinstance(node, exp.Table):
                table_name = node.name.lower()
                schema_name = node.db.lower() if node.db else None

                # Block system schemas
                if schema_name and schema_name in SQL_BLOCKED_SYSTEM_SCHEMAS:
                    raise SQLValidationError(f"Access to system schema '{schema_name}' is forbidden")

                # Validate against allowed tables if provided
                if allowed_tables is not None:
                    normalized_allowed = {t.lower() for t in allowed_tables}
                    if table_name not in normalized_allowed:
                        raise SQLValidationError(f"Access to table '{table_name}' is not permitted")

        # 6. Inject backend mandatory row-level security filters
        if permitted_schema:
            parsed = self.inject_row_filters(
                parsed,
                permitted_schema=permitted_schema,
                tenant_id=tenant_id,
                user_id=user_id,
                dialect=dialect,
            )

        # Return standardized, formatted SQL
        return parsed.sql(dialect=dialect)


def validate_sql(
    sql: str,
    dialect: str = "postgres",
    allowed_tables: set[str] | None = None,
    permitted_schema: dict | None = None,
    tenant_id: str | None = None,
    user_id: str | None = None,
) -> str:
    guard = SQLGuard()
    return guard.validate_and_sanitize(
        sql,
        dialect=dialect,
        allowed_tables=allowed_tables,
        permitted_schema=permitted_schema,
        tenant_id=tenant_id,
        user_id=user_id,
    )

