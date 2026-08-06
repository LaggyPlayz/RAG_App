import pytest
from app.services.sql.guard import SQLGuard
from app.utils.exceptions import SQLValidationError


def test_sql_guard_valid_select():
    guard = SQLGuard()
    sql = "SELECT id, name FROM customers WHERE country = 'EG'"
    validated = guard.validate_and_sanitize(sql, dialect="postgres", allowed_tables={"customers"})
    assert "customers" in validated.lower()


def test_sql_guard_blocks_drop():
    guard = SQLGuard()
    sql = "DROP TABLE users;"
    with pytest.raises(SQLValidationError):
        guard.validate_and_sanitize(sql, dialect="postgres")


def test_sql_guard_blocks_multiple_statements():
    guard = SQLGuard()
    sql = "SELECT * FROM users; DELETE FROM users;"
    with pytest.raises(SQLValidationError):
        guard.validate_and_sanitize(sql, dialect="postgres")


def test_sql_guard_blocks_comments():
    guard = SQLGuard()
    sql = "SELECT * FROM users -- inline comment"
    with pytest.raises(SQLValidationError):
        guard.validate_and_sanitize(sql, dialect="postgres")


def test_sql_guard_unauthorized_table():
    guard = SQLGuard()
    sql = "SELECT * FROM secret_financials"
    with pytest.raises(SQLValidationError):
        guard.validate_and_sanitize(sql, dialect="postgres", allowed_tables={"customers", "orders"})


def test_sql_guard_row_filter_injection():
    guard = SQLGuard()
    sql = "SELECT id, name FROM customers"
    permitted_schema = {
        "customers": {
            "columns": [{"name": "id"}, {"name": "name"}],
            "row_filter": {"tenant_id": "{tenant_id}", "user_id": "{user_id}"},
        }
    }
    validated = guard.validate_and_sanitize(
        sql,
        dialect="postgres",
        permitted_schema=permitted_schema,
        tenant_id="tenant-123",
        user_id="user-456",
    )
    validated_lower = validated.lower()
    assert "where" in validated_lower
    assert "tenant-123" in validated
    assert "user-456" in validated

