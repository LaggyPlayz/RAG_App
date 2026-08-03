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


class ConversationNotFoundError(AppError):
    status_code = 404
    error_code = "conversation_not_found"


class RetrievalError(AppError):
    status_code = 502
    error_code = "retrieval_failed"


class VectorStoreError(AppError):
    status_code = 502
    error_code = "vector_store_failed"


class LLMServiceError(AppError):
    status_code = 502
    error_code = "llm_service_failed"