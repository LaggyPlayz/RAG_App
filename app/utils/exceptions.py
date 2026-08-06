"""Application-level exceptions.

These map to clean, structured HTTP responses via the exception handler
registered in app/main.py — never let a raw exception (with a stack
trace or internal error string) reach the client.
"""


class AppError(Exception):
    status_code = 500
    error_code = "internal_error"

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


# ── Auth ──

class AuthenticationError(AppError):
    status_code = 401
    error_code = "authentication_failed"


class AuthorizationError(AppError):
    status_code = 403
    error_code = "authorization_denied"


class TokenExpiredError(AppError):
    status_code = 401
    error_code = "token_expired"


# ── Tenant ──

class TenantNotFoundError(AppError):
    status_code = 404
    error_code = "tenant_not_found"


# ── Resources ──

class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class ConversationNotFoundError(AppError):
    status_code = 404
    error_code = "conversation_not_found"


class DuplicateError(AppError):
    status_code = 409
    error_code = "duplicate_resource"


# ── Database Connections ──

class ConnectionTestError(AppError):
    status_code = 422
    error_code = "connection_test_failed"


class SchemaDiscoveryError(AppError):
    status_code = 502
    error_code = "schema_discovery_failed"


# ── SQL ──

class SQLValidationError(AppError):
    status_code = 422
    error_code = "sql_validation_failed"


class SQLExecutionError(AppError):
    status_code = 502
    error_code = "sql_execution_failed"


# ── Documents ──

class FileProcessingError(AppError):
    status_code = 422
    error_code = "file_processing_failed"


class UnsupportedFileTypeError(AppError):
    status_code = 415
    error_code = "unsupported_file_type"


class FileTooLargeError(AppError):
    status_code = 413
    error_code = "file_too_large"


# ── External Services ──

class RetrievalError(AppError):
    status_code = 502
    error_code = "retrieval_failed"


class VectorStoreError(AppError):
    status_code = 502
    error_code = "vector_store_failed"


class LLMServiceError(AppError):
    status_code = 502
    error_code = "llm_service_failed"