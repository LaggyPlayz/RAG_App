from typing import Any


def format_sql_results_as_markdown(rows: list[dict[str, Any]], max_rows_in_table: int = 20) -> str:
    """Format a list of database rows into a readable markdown table for LLM context."""
    if not rows:
        return "No results returned."

    columns = list(rows[0].keys())
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"

    row_strings = []
    for row in rows[:max_rows_in_table]:
        values = [str(row.get(col, "")).replace("\n", " ") for col in columns]
        row_strings.append("| " + " | ".join(values) + " |")

    table = "\n".join([header, separator] + row_strings)

    if len(rows) > max_rows_in_table:
        table += f"\n\n*(Showing top {max_rows_in_table} of {len(rows)} total rows)*"

    return table
