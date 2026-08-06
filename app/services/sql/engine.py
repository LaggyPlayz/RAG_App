from typing import Any

from app.models.chat import SQLExecutionSummary
from app.services.database.connection_service import ConnectionService
from app.services.database.metadata_cache import MetadataCacheService
from app.services.llm.openai_service import OpenAIService
from app.services.sql.executor import SQLExecutor
from app.services.sql.formatter import format_sql_results_as_markdown
from app.services.sql.schema_inspector import build_schema_prompt_context
from app.services.sql.text_to_sql import TextToSQLService
from app.utils.exceptions import SQLExecutionError, SQLValidationError


class SQLEngine:
    """High-level facade orchestrating Text-to-SQL generation and safe execution."""

    def __init__(
        self,
        connection_service: ConnectionService,
        metadata_cache_service: MetadataCacheService,
        llm_service: OpenAIService,
    ):
        self.connection_service = connection_service
        self.metadata_cache = metadata_cache_service
        self.text_to_sql = TextToSQLService(llm_service)
        self.executor = SQLExecutor()

    async def execute_text_to_sql_pipeline(
        self,
        question: str,
        connection_ids: list[str],
        tenant_id: str,
        user_id: str,
        role_ids: list[str],
        is_admin: bool = False,
    ) -> tuple[str, SQLExecutionSummary, list[dict[str, Any]]]:
        """Runs: Schema resolution -> Prompt formatting -> SQL generation -> Validation -> Execution -> Formatting.

        Returns (markdown_formatted_result, summary_object, raw_rows).
        """
        if not connection_ids:
            return "No database connections selected.", SQLExecutionSummary(query="", row_count=0, error="No connections provided"), []

        # 1. Resolve permission-filtered schema
        permitted_schema = await self.metadata_cache.get_permitted_schema(
            connection_ids=connection_ids,
            tenant_id=tenant_id,
            user_id=user_id,
            role_ids=role_ids,
            is_admin=is_admin,
        )

        if not permitted_schema:
            return "No permitted database tables available for this query.", SQLExecutionSummary(query="", row_count=0, error="No permitted tables"), []

        schema_context = build_schema_prompt_context(permitted_schema)
        allowed_tables = set(permitted_schema.keys())

        # 2. Get first active connection instance to run query against
        conn = await self.connection_service.repo.get_by_id(connection_ids[0], tenant_id)
        if not conn:
            return "Selected database connection not found.", SQLExecutionSummary(query="", row_count=0, error="Connection not found"), []

        connection_url = self.connection_service.get_decrypted_connection_url(conn)

        # 3. Generate and validate SQL with AST row-level filter injection
        try:
            sql = await self.text_to_sql.generate_sql(
                user_query=question,
                schema_context=schema_context,
                dialect=conn.database_type,
                allowed_tables=allowed_tables,
                permitted_schema=permitted_schema,
                tenant_id=tenant_id,
                user_id=user_id,
            )
        except SQLValidationError as exc:
            return f"SQL Generation Failed: {exc.message}", SQLExecutionSummary(query="", row_count=0, error=exc.message), []


        # 4. Execute query safely
        try:
            rows, count, latency = self.executor.execute_query(connection_url, sql)
            markdown_result = format_sql_results_as_markdown(rows)

            summary = SQLExecutionSummary(
                query=sql,
                row_count=count,
                result_preview=rows[:5],
            )
            return markdown_result, summary, rows
        except SQLExecutionError as exc:
            return f"SQL Execution Failed: {exc.message}", SQLExecutionSummary(query=sql, row_count=0, error=exc.message), []
