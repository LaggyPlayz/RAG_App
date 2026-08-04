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

    def validate_and_sanitize(
        self,
        sql: str,
        dialect: str = "postgres",
        allowed_tables: set[str] | None = None,
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

        # Return standardized, formatted SQL
        return parsed.sql(dialect=dialect)


def validate_sql(sql: str, dialect: str = "postgres", allowed_tables: set[str] | None = None) -> str:
    guard = SQLGuard()
    return guard.validate_and_sanitize(sql, dialect, allowed_tables)
