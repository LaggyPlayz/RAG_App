"""FastAPI entrypoint.

This wires up the routes built in this pass (health, search, chat).
documents/sql/conversations/admin routers are left commented out —
uncomment them once those slices are implemented, so importing this
file doesn't break on routers that don't exist yet.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import chat, health, search

# from app.api.routes import admin, conversations, documents, sql
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.services.qdrant.collections import ensure_collection
from app.utils.exceptions import AppError

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(title="RAG_App", version="0.1.0")

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(search.router)
# app.include_router(documents.router)
# app.include_router(sql.router)
# app.include_router(conversations.router)
# app.include_router(admin.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message, "details": exc.details},
    )


@app.on_event("startup")
async def on_startup():
    await ensure_collection()