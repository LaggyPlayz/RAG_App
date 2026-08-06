from app.agents.state import AgentState


class HybridMergerNode:
    """Merges structured SQL database results and unstructured vector document evidence into unified context."""

    async def merge(self, state: AgentState) -> AgentState:
        sql_res = state.get("sql_markdown_result")
        doc_res = state.get("document_context")

        combined_parts = []
        if sql_res:
            combined_parts.append(f"### Structured Database Query Results:\n{sql_res}")
        if doc_res:
            combined_parts.append(f"### Document Evidence:\n{doc_res}")

        state["merged_context"] = "\n\n".join(combined_parts)
        return state
