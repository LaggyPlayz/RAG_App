import hashlib
from typing import Any


def apply_column_masking(rows: list[dict[str, Any]], column_masks: dict[str, str]) -> list[dict[str, Any]]:
    """Apply masking (partial, email, full, hash) to sensitive column values in result rows.

    column_masks: dictionary mapping lowercase column_name -> mask_type.
    """
    if not rows or not column_masks:
        return rows

    normalized_masks = {k.lower(): v.lower() for k, v in column_masks.items()}
    masked_rows = []

    for row in rows:
        masked_row = dict(row)
        for col, val in row.items():
            col_lower = col.lower()
            if col_lower in normalized_masks and val is not None:
                mask_type = normalized_masks[col_lower]
                val_str = str(val)

                if mask_type in ("partial", "ssn", "phone"):
                    masked_row[col] = "*" * max(0, len(val_str) - 4) + val_str[-4:]
                elif mask_type == "email":
                    if "@" in val_str:
                        user_part, domain = val_str.split("@", 1)
                        masked_row[col] = f"{user_part[0]}***@{domain}"
                    else:
                        masked_row[col] = "***@***.***"
                elif mask_type in ("full", "redact"):
                    masked_row[col] = "[REDACTED]"
                elif mask_type == "hash":
                    masked_row[col] = hashlib.sha256(val_str.encode("utf-8")).hexdigest()[:12]

        masked_rows.append(masked_row)

    return masked_rows


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

