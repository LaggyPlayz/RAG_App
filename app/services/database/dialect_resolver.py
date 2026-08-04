from app.core.constants import (
    DB_TYPE_MYSQL,
    DB_TYPE_ORACLE,
    DB_TYPE_POSTGRESQL,
    DB_TYPE_SQLITE,
    DB_TYPE_SQLSERVER,
)
from app.utils.exceptions import AppError


def build_sqlalchemy_url(
    db_type: str,
    host: str | None = None,
    port: int | None = None,
    database_name: str | None = None,
    username: str | None = None,
    password: str | None = None,
    connection_string: str | None = None,
) -> str:
    """Build a standard SQLAlchemy connection URL from connection parameters."""
    if connection_string:
        return connection_string

    db_type_lower = db_type.lower()
    user_pass = f"{username}:{password}@" if username and password else (f"{username}@" if username else "")
    host_port = f"{host}:{port}" if host and port else (host or "localhost")

    if db_type_lower in (DB_TYPE_POSTGRESQL, "postgres"):
        port = port or 5432
        return f"postgresql+psycopg2://{user_pass}{host}:{port}/{database_name or 'postgres'}"
    elif db_type_lower in (DB_TYPE_MYSQL, "mariadb"):
        port = port or 3306
        return f"mysql+pymysql://{user_pass}{host}:{port}/{database_name or ''}"
    elif db_type_lower in (DB_TYPE_SQLSERVER, "mssql"):
        port = port or 1433
        return f"mssql+pyodbc://{user_pass}{host}:{port}/{database_name or ''}?driver=ODBC+Driver+17+for+SQL+Server"
    elif db_type_lower in (DB_TYPE_ORACLE, "oracle"):
        port = port or 1521
        return f"oracle+cx_oracle://{user_pass}{host}:{port}/?service_name={database_name or 'XE'}"
    elif db_type_lower == DB_TYPE_SQLITE:
        return f"sqlite:///{database_name or ':memory:'}"
    else:
        raise AppError(f"Unsupported database type: {db_type}")


def get_sqlglot_dialect(db_type: str) -> str:
    """Map platform database type string to SQLGlot dialect string."""
    db_type_lower = db_type.lower()
    mapping = {
        DB_TYPE_POSTGRESQL: "postgres",
        "postgres": "postgres",
        DB_TYPE_MYSQL: "mysql",
        "mariadb": "mysql",
        DB_TYPE_SQLSERVER: "tsql",
        "mssql": "tsql",
        DB_TYPE_ORACLE: "oracle",
        DB_TYPE_SQLITE: "sqlite",
    }
    return mapping.get(db_type_lower, "postgres")
