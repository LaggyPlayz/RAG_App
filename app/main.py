"""FastAPI Application Entrypoint.

Registers all API routes, database startup initialization, exception handlers,
CORS middleware, and OpenAPI dashboard documentation metadata.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import get_engine
from app.core.logging import setup_logging
from app.db.base import Base
import app.db.models  # Load all ORM models
from app.services.qdrant.collections import ensure_collection
from app.utils.exceptions import AppError

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(
    title="RAG-Backend",
    version="1.0.7",
    description="Production-ready Retrieval-Augmented Generation (RAG) Backend API with Multi-Tenant Text-to-SQL and Document Chat Platform",
    openapi_url="/openapi.json",
    docs_url="/docs",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include central router
app.include_router(api_router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message, "details": exc.details},
    )


@app.on_event("startup")
async def on_startup():
    # Ensure Qdrant collection exists
    await ensure_collection()

    # Ensure PostgreSQL database tables exist
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)