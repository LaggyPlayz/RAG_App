def build_schema_prompt_context(permitted_schema: dict) -> str:
    """Format permitted schema dict into readable DDL-style text for the LLM prompt."""
    if not permitted_schema:
        return "No accessible tables found."

    lines = []
    for table_name, table_info in permitted_schema.items():
        cols_text = ", ".join([f"{c['name']} ({c['type']})" for c in table_info.get("columns", [])])
        lines.append(f"Table: {table_name}")
        lines.append(f"Columns: {cols_text}")
        if table_info.get("row_filter"):
            lines.append(f"Required Row Filter Rule: {table_info['row_filter']}")
        lines.append("")

    return "\n".join(lines)
