"""Application-wide constants and enums."""

# ── Chat Intent Types ──
GENERAL = "general"
DATABASE = "database"
DOCUMENT = "document"
HYBRID = "hybrid"
CLARIFICATION = "clarification"

CHAT_INTENTS = {GENERAL, DATABASE, DOCUMENT, HYBRID, CLARIFICATION}

# ── Message Roles ──
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM = "system"

# ── Message Types ──
MESSAGE_TYPE_TEXT = "text"
MESSAGE_TYPE_SQL = "sql"
MESSAGE_TYPE_ERROR = "error"

# ── Entity Statuses ──
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_PENDING = "pending"
STATUS_SUSPENDED = "suspended"

# ── Connection Statuses ──
CONN_STATUS_PENDING = "pending"
CONN_STATUS_CONNECTED = "connected"
CONN_STATUS_FAILED = "failed"
CONN_STATUS_DISCONNECTED = "disconnected"

# ── Schema Sync Statuses ──
SCHEMA_SYNC_PENDING = "pending"
SCHEMA_SYNC_IN_PROGRESS = "in_progress"
SCHEMA_SYNC_COMPLETED = "completed"
SCHEMA_SYNC_FAILED = "failed"

# ── File Processing Statuses ──
FILE_STATUS_PENDING = "pending"
FILE_STATUS_PROCESSING = "processing"
FILE_STATUS_COMPLETED = "completed"
FILE_STATUS_FAILED = "failed"

# ── Conversation Statuses ──
CONV_STATUS_ACTIVE = "active"
CONV_STATUS_ARCHIVED = "archived"

# ── SQL Validation ──
SQL_ALLOWED_STATEMENTS = {"SELECT", "WITH"}

SQL_BLOCKED_STATEMENTS = {
    "DROP", "TRUNCATE", "ALTER", "CREATE", "GRANT", "REVOKE",
    "EXEC", "CALL", "COPY", "ATTACH", "DETACH",
    "INSERT", "UPDATE", "DELETE", "MERGE",
}

SQL_BLOCKED_SYSTEM_SCHEMAS = {
    "pg_catalog", "information_schema", "pg_toast",
    "mysql", "sys", "performance_schema",
    "master", "msdb", "tempdb", "model",
}

# ── Database Types ──
DB_TYPE_POSTGRESQL = "postgresql"
DB_TYPE_MYSQL = "mysql"
DB_TYPE_SQLSERVER = "sqlserver"
DB_TYPE_ORACLE = "oracle"
DB_TYPE_SQLITE = "sqlite"

SUPPORTED_DB_TYPES = {DB_TYPE_POSTGRESQL, DB_TYPE_MYSQL, DB_TYPE_SQLSERVER, DB_TYPE_ORACLE, DB_TYPE_SQLITE}

# ── Supported File Extensions ──
SUPPORTED_FILE_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".md", ".json", ".html"}

# ── Query Execution Statuses ──
QUERY_VALIDATION_PASSED = "passed"
QUERY_VALIDATION_FAILED = "failed"
QUERY_EXECUTION_SUCCESS = "success"
QUERY_EXECUTION_ERROR = "error"
QUERY_EXECUTION_TIMEOUT = "timeout"

# ── Citation Types ──
CITATION_TYPE_DOCUMENT = "document"
CITATION_TYPE_DATABASE = "database"

# ── Audit Actions ──
AUDIT_LOGIN = "login"
AUDIT_LOGOUT = "logout"
AUDIT_CONNECTION_CREATE = "connection_create"
AUDIT_CONNECTION_TEST = "connection_test"
AUDIT_CONNECTION_DELETE = "connection_delete"
AUDIT_SCHEMA_SYNC = "schema_sync"
AUDIT_FILE_UPLOAD = "file_upload"
AUDIT_FILE_DELETE = "file_delete"
AUDIT_SQL_EXECUTE = "sql_execute"
AUDIT_SQL_BLOCKED = "sql_blocked"
AUDIT_CHAT = "chat"
AUDIT_PERMISSION_CHANGE = "permission_change"

# ── Table Types ──
TABLE_TYPE_TABLE = "table"
TABLE_TYPE_VIEW = "view"
