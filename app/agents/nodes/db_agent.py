from app.agents.state import AgentState
from app.services.sql.engine import SQLEngine


class DatabaseAgentNode:
    def __init__(self, sql_engine: SQLEngine):
        self.sql_engine = sql_engine

    async def execute(self, state: AgentState) -> AgentState:
        msg = state.get("user_message", "")
        db_conn_ids = state.get("database_connection_ids", [])
        tenant_id = state.get("tenant_id", "")
        user_id = state.get("user_id", "")
        role_ids = state.get("role_ids", [])
        is_admin = state.get("is_admin", False)

        markdown_res, summary, rows = await self.sql_engine.execute_text_to_sql_pipeline(
            question=msg,
            connection_ids=db_conn_ids,
            tenant_id=tenant_id,
            user_id=user_id,
            role_ids=role_ids,
            is_admin=is_admin,
        )

        state["sql_markdown_result"] = markdown_res
        state["sql_summary"] = summary
        state["raw_sql_rows"] = rows

        sources = state.get("sources_used", [])
        if "database" not in sources:
            sources.append("database")
        state["sources_used"] = sources

        return state
