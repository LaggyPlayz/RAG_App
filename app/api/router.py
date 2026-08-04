from fastapi import APIRouter

from app.api.routes import (
    admin,
    auth,
    chat,
    conversations,
    database_connections,
    database_schema,
    documents,
    health,
    knowledge_bases,
    permissions,
    search,
    sql,
    tenants,
    users,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(tenants.router)
api_router.include_router(users.router)
api_router.include_router(database_connections.router)
api_router.include_router(database_schema.router)
api_router.include_router(permissions.router)
api_router.include_router(documents.router)
api_router.include_router(knowledge_bases.router)
api_router.include_router(conversations.router)
api_router.include_router(chat.router)
api_router.include_router(search.router)
api_router.include_router(sql.router)
api_router.include_router(admin.router)
