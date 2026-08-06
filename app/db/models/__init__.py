"""Import all ORM models so Alembic and Base.metadata.create_all see them."""

from app.db.models.tenant import Tenant  # noqa: F401
from app.db.models.user import User  # noqa: F401
from app.db.models.role import Role, UserRole  # noqa: F401
from app.db.models.database_connection import DatabaseConnection  # noqa: F401
from app.db.models.database_schema import DatabaseSchema, DatabaseTable, DatabaseColumn  # noqa: F401
from app.db.models.permission import TablePermission, ColumnPermission  # noqa: F401
from app.db.models.knowledge_base import KnowledgeBase  # noqa: F401
from app.db.models.file import File  # noqa: F401
from app.db.models.document_chunk import DocumentChunk  # noqa: F401
from app.db.models.conversation import Conversation  # noqa: F401
from app.db.models.message import Message  # noqa: F401
from app.db.models.query_execution import QueryExecution  # noqa: F401
from app.db.models.citation import MessageCitation  # noqa: F401
from app.db.models.audit_log import AuditLog  # noqa: F401
