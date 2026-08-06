import pytest
from app.services.sql.formatter import apply_column_masking, format_sql_results_as_markdown


def test_format_sql_results_as_markdown():
    rows = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    formatted = format_sql_results_as_markdown(rows)
    assert "| id | name |" in formatted
    assert "| 1 | Alice |" in formatted
    assert "| 2 | Bob |" in formatted


def test_apply_column_masking():
    rows = [
        {"id": 1, "email": "user@example.com", "ssn": "123456789", "salary": "100000"},
    ]
    masks = {
        "email": "email",
        "ssn": "partial",
        "salary": "full",
    }
    masked = apply_column_masking(rows, masks)
    assert masked[0]["email"] == "u***@example.com"
    assert masked[0]["ssn"] == "*****6789"
    assert masked[0]["salary"] == "[REDACTED]"
    assert masked[0]["id"] == 1
