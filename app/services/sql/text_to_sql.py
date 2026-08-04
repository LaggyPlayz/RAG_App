from app.services.llm.openai_service import OpenAIService
from app.services.sql.guard import SQLGuard
from app.utils.exceptions import SQLValidationError


class TextToSQLService:
    def __init__(self, llm_service: OpenAIService):
        self.llm = llm_service
        self.guard = SQLGuard()

    def _build_prompt(self, user_query: str, schema_context: str, dialect: str) -> list[dict]:
        system_prompt = (
            f"You are an expert SQL engineer. Generate a single, valid, read-only SQL query in {dialect} dialect "
            "to answer the user's question based strictly on the provided schema.\n\n"
            "Rules:\n"
            "1. Output ONLY the raw SQL query inside a markdown ```sql code block. Do not add explanations.\n"
            "2. Only use the tables and columns present in the schema.\n"
            "3. Use SELECT queries only. No DROP, ALTER, UPDATE, DELETE, CREATE, or multiple statements.\n"
            "4. Always limit results to 100 rows unless explicitly specified.\n\n"
            f"Allowed Database Schema:\n{schema_context}"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]

    async def generate_sql(
        self,
        user_query: str,
        schema_context: str,
        dialect: str = "postgres",
        allowed_tables: set[str] | None = None,
    ) -> str:
        messages = self._build_prompt(user_query, schema_context, dialect)
        raw_response = await self.llm.complete(messages)

        # Extract SQL from markdown code block if wrapped
        sql = raw_response.strip()
        if "```" in sql:
            lines = sql.split("\n")
            code_lines = []
            in_block = False
            for line in lines:
                if line.startswith("```"):
                    in_block = not in_block
                    continue
                if in_block:
                    code_lines.append(line)
            sql = "\n".join(code_lines).strip()

        # Validate generated SQL with SQLGuard
        validated_sql = self.guard.validate_and_sanitize(sql, dialect=dialect, allowed_tables=allowed_tables)
        return validated_sql
