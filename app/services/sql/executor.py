import time
from typing import Any

from sqlalchemy import create_engine, text

from app.core.config import get_settings
from app.utils.exceptions import SQLExecutionError

_settings = get_settings()


class SQLExecutor:
    """Executes validated SQL queries against target source databases safely."""

    def execute_query(
        self,
        connection_url: str,
        sql: str,
        timeout_seconds: int | None = None,
        max_rows: int | None = None,
    ) -> tuple[list[dict[str, Any]], int, int]:
        """Execute a read-only query and return (rows_list, row_count, latency_ms)."""
        timeout = timeout_seconds or _settings.sql_query_timeout_seconds
        max_limit = max_rows or _settings.sql_max_result_rows

        try:
            start_time = time.time()
            engine = create_engine(
                connection_url,
                connect_args={"options": f"-c statement_timeout={timeout * 1000}"}
                if "postgresql" in connection_url
                else {},
            )

            with engine.connect() as conn:
                result = conn.execute(text(sql))
                keys = list(result.keys())
                fetched_rows = result.fetchmany(max_limit)

                rows = [dict(zip(keys, row)) for row in fetched_rows]

            latency_ms = int((time.time() - start_time) * 1000)
            engine.dispose()

            return rows, len(rows), latency_ms

        except Exception as exc:
            raise SQLExecutionError(f"Error executing SQL query: {str(exc)}") from exc
