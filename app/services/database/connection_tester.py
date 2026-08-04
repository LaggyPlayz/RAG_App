import time

from sqlalchemy import create_engine, text

from app.models.database_connection import ConnectionTestResult
from app.services.database.dialect_resolver import build_sqlalchemy_url


def test_connection(
    db_type: str,
    host: str | None = None,
    port: int | None = None,
    database_name: str | None = None,
    username: str | None = None,
    password: str | None = None,
    connection_string: str | None = None,
) -> ConnectionTestResult:
    """Test runtime connectivity to a customer business database."""
    try:
        url = build_sqlalchemy_url(
            db_type=db_type,
            host=host,
            port=port,
            database_name=database_name,
            username=username,
            password=password,
            connection_string=connection_string,
        )

        start_time = time.time()
        engine = create_engine(url, connect_args={"connect_timeout": 5} if db_type == "postgresql" else {})

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        latency_ms = int((time.time() - start_time) * 1000)
        engine.dispose()

        return ConnectionTestResult(
            success=True,
            message="Database connection test successful",
            latency_ms=latency_ms,
        )
    except Exception as exc:
        return ConnectionTestResult(
            success=False,
            message=f"Connection failed: {str(exc)}",
            latency_ms=None,
            details={"error": str(exc)},
        )
