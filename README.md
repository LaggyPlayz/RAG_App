# Multi-Tenant Text-to-SQL and Document Chat Platform

A multi-tenant-oriented Retrieval-Augmented Generation (RAG) and Text-to-SQL backend. It ingests documents and live databases, indexes content for semantic search, and answers natural-language questions by combining vector retrieval with guarded SQL generation and execution.

> **Note on this README:** it's written directly from the repository's file structure. Endpoint verbs, exact env var names, and a couple of implementation details are marked as assumptions below — grep the referenced files and adjust anything that doesn't match your actual code before you publish this.

---

## 📂 Repository Structure

```
RAG_App/
├── app/
│   ├── main.py                      # FastAPI app entrypoint
│   ├── api/
│   │   ├── dependencies.py          # Shared FastAPI dependencies (DB session, auth, etc.)
│   │   └── routes/
│   │       ├── admin.py             # Admin/management endpoints
│   │       ├── chat.py              # Conversational chat endpoint(s)
│   │       ├── conversations.py     # Conversation history CRUD
│   │       ├── documents.py         # File upload & document management
│   │       ├── health.py            # Health/readiness checks
│   │       ├── search.py            # Vector/semantic search endpoint
│   │       └── sql.py               # Text-to-SQL endpoint
│   ├── core/
│   │   ├── config.py                # Settings (env-driven configuration)
│   │   ├── constants.py             # Shared constants/enums
│   │   └── logging.py               # Logging setup
│   ├── models/
│   │   ├── chat.py                  # Chat request/response schemas
│   │   ├── common.py                # Shared base models
│   │   ├── document.py              # Document/file schemas
│   │   ├── history.py               # Conversation history schemas
│   │   ├── search.py                # Search request/response schemas
│   │   └── sql.py                   # SQL request/response schemas
│   ├── services/
│   │   ├── chunking/                # Pluggable chunking strategies (see below)
│   │   ├── history/                 # Conversation memory (bootstrap, engine, store, window)
│   │   ├── ingestion/                # Format-specific document loaders
│   │   ├── llm/                     # LLM + embeddings integration (OpenAI)
│   │   ├── qdrant/                  # Vector store client, collections, ingestion, search
│   │   ├── redis/                   # Cache/queue client
│   │   ├── retrieval/               # Retrieval pipeline (retriever, reranker, context builder)
│   │   └── sql/                     # Text-to-SQL pipeline (engine, guard, executor, etc.)
│   ├── utils/                       # Cross-cutting helpers (files, text, tokens, validation, exceptions)
│   └── workers/                     # Background/async ingestion tasks
├── sql/init/                         # DB initialization scripts (source/customer DB and/or app DB)
├── tests/                            # Pytest suite
├── uploads/                           # Local file storage (dev only — see Docker Compose Services)
├── logs/                             # Application log output
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## 🖼️ Screenshot
![Back-end Dashboard Screenshot](/Screenshot_RAG_project.png)

---

## 🗝️ Key Features

- **Multi-strategy document ingestion** — loaders for PDF, DOCX, PPTX, Excel, CSV, HTML, Markdown, JSON, YAML, and plain text (`app/services/ingestion/`).
- **Pluggable chunking pipeline** — 10+ chunking strategies selectable via a factory, from simple fixed-size chunking to agentic and proposition-based chunking (`app/services/chunking/`).
- **Vector search over Qdrant** — collection management, ingestion, and similarity search (`app/services/qdrant/`).
- **Retrieval pipeline with reranking** — retriever → reranker → context builder before anything reaches the LLM (`app/services/retrieval/`).
- **Guarded Text-to-SQL** — natural language to SQL, validated and executed through a dedicated guard/executor rather than a raw LLM-to-database path (`app/services/sql/`).
- **Backend row-level security enforcement** — mandatory tenant and user row filters are injected directly into the SQL AST via SQLGlot before any query executes (`guard.py`). The LLM cannot bypass these filters.
- **Sensitive column masking** — columns marked with a `mask_type` (`partial`, `email`, `full`/`redact`, `hash`) are automatically masked in query results before they reach the LLM or the API response (`formatter.py`).
- **Full audit trail** — all significant actions (login, connection create/test/schema-sync, file upload/delete, permission grants, chat, SQL execution, conversation deletion) are written to `audit_logs` via `AuditService`.
- **Postgres-backed chat persistence** — every conversation, user/assistant message, SQL query execution record, and document citation is stored in Postgres so that `GET /api/conversations/{id}` and `GET /api/messages/{id}/sql` return real data.
- **Conversation history/memory** — bootstrap, sliding-window, and storage layer for multi-turn context (`app/services/history/`).
- **Async background processing** — ingestion offloaded to workers backed by Redis (`app/workers/`, `app/services/redis/`).
- **Health checks** for orchestrated/containerized deployment.

---

## ⭐ Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- An OpenAI API key (or equivalent LLM provider credentials)

### 1. Clone and configure
```bash
git clone https://github.com/LaggyPlayz/RAG_App.git
cd RAG_App
cp .env.example .env
# then edit .env with your API keys and connection settings
```

### 2. Run with Docker Compose (recommended)
```bash
docker-compose up --build
```

### 3. Or run locally
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. Verify it's up
```bash
curl http://localhost:8000/api/health
```

Interactive API docs are available once the server is running:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📄 Application Pages

This is a backend service — there is no rendered frontend in this repository. The "pages" a client (Swagger UI, ReDoc, or your own frontend) will interact with map to the router modules under `app/api/routes/`:

| Page / Section | Router file | Purpose |
|---|---|---|
| Health | `health.py` | Liveness/readiness probe for orchestration |
| Chat | `chat.py` | Conversational entrypoint that can trigger retrieval, SQL, or both |
| Conversations | `conversations.py` | List, fetch, and manage conversation history |
| Documents | `documents.py` | Upload files, check ingestion status, manage the knowledge base |
| Search | `search.py` | Direct semantic/vector search without full chat orchestration |
| SQL | `sql.py` | Direct natural-language-to-SQL endpoint |
| Admin | `admin.py` | Management/operational endpoints (collections, config, etc.) |
| Docs (`/docs`, `/redoc`) | auto-generated by FastAPI | Interactive API reference |

---

## 🔎 Architecture Overview

```
Client
  │
  ▼
FastAPI (app/main.py)
  │
  ├── /api/health          → health.py
  ├── /api/documents        → documents.py ──► ingestion loaders ──► chunking strategy ──► embeddings ──► Qdrant
  ├── /api/search           → search.py    ──► retriever ──► reranker ──► context builder
  ├── /api/sql               → sql.py       ──► text_to_sql ──► guard (validation) ──► executor ──► source DB
  ├── /api/chat              → chat.py      ──► history engine ──► {search path, sql path, or both} ──► LLM (openai_service) ──► response
  ├── /api/conversations     → conversations.py ──► history store
  └── /api/admin             → admin.py

Background:
  Documents queued via Redis ──► app/workers/ingestion_worker.py ──► loader → chunker → embeddings → Qdrant

Storage:
  Qdrant     → vector embeddings for retrieval
  Redis      → queue/cache for async ingestion and (optionally) history/session state
  SQL DB(s)  → source data queried by the guarded Text-to-SQL pipeline, initialized via sql/init/
  uploads/   → local file storage for uploaded documents (dev; use object storage in production)
```

**Design principle carried through the code:** the SQL path never lets the LLM execute arbitrary text against a live database — generation (`text_to_sql.py`), validation (`guard.py`), and execution (`executor.py`) are separate stages, and the RAG path never lets the LLM see raw documents without going through retrieval + reranking first.

---

## 🛡️ Security Controls

This system implements several layered, backend-enforced security controls that cannot be bypassed by the LLM or by prompt injection:

| Control | Where enforced | How |
|---|---|---|
| **Row-level filters** | `SQLGuard.inject_row_filters()` | Mandatory `WHERE` conditions (e.g. `tenant_id`, `user_id`) are injected into the SQL AST via SQLGlot after LLM generation, before execution. |
| **Table allow-list** | `SQLGuard.validate_and_sanitize()` | Only tables visible in `permitted_schema` may be referenced; all others raise `SQLValidationError`. |
| **Column visibility** | `MetadataCacheService` | Columns with `can_read = false` are omitted from the schema context sent to the LLM. |
| **Sensitive column masking** | `apply_column_masking()` in `formatter.py` | Columns with a `mask_type` (`partial`, `email`, `full`, `hash`) are masked in result rows before they reach the LLM prompt or API response. |
| **Statement type enforcement** | `SQLGuard` | Only `SELECT` and CTE queries allowed; DDL/DML, multi-statements, and SQL comments are all rejected. |
| **System schema blocking** | `SQLGuard` | Access to system schemas (e.g. `information_schema`, `pg_catalog`) is blocked. |
| **Encrypted credentials** | `ConnectionService` | Database passwords are encrypted at rest using Fernet symmetric encryption. |
| **JWT authentication** | `core/security.py` | Access and refresh tokens with separate secrets and expiry windows. |
| **Tenant isolation** | All repositories | Every query is scoped to `tenant_id` extracted from the JWT, enforced at repository level. |
| **Audit logging** | `AuditService` | Login, connection CRUD, schema sync, file upload/delete, permission grants, chat, SQL execution, and conversation deletion are all recorded in `audit_logs`. |

---

## 🧪 Running Tests

```bash
# Full suite
pytest

# Verbose output
pytest -v

# A specific test file
pytest tests/test_sql_guard.py

# With coverage
pytest --cov=app --cov-report=term-missing
```

Test coverage in this repo:

| Test file | Covers |
|---|---|
| `test_api.py` | API route-level behavior |
| `test_chunker.py` | Baseline chunking strategies |
| `test_advanced_chunkers.py` | Agentic/semantic/proposition-style chunkers |
| `test_loaders.py` | Document ingestion loaders |
| `test_sql_formatter.py` | SQL result formatting and column masking |
| `test_sql_guard.py` | SQL validation, safety rules, and row-filter AST injection |
| `test_security.py` | JWT generation/verification, Fernet encryption, and audit service logging |
| `test_permissions.py` | Column-level permission filtering in `MetadataCacheService` |
| `test_history_window.py` | Conversation history windowing |

---

## ⚡ Environment Variables

Confirm these against your actual `.env.example` — names below follow the convention implied by `app/core/config.py` and the services present in the repo.

| Variable | Description | Example |
|---|---|---|
| `APP_ENV` | Runtime environment | `development` / `production` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `OPENAI_API_KEY` | LLM + embeddings provider key | `sk-...` |
| `OPENAI_MODEL` | Chat/completion model name | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Embedding model name | `text-embedding-3-small` |
| `QDRANT_HOST` | Qdrant host | `qdrant` |
| `QDRANT_PORT` | Qdrant port | `6333` |
| `QDRANT_COLLECTION` | Default collection name | `documents` |
| `REDIS_HOST` | Redis host | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `DATABASE_URL` | Connection string for the SQL source used by the Text-to-SQL path | `postgresql://user:pass@db:5432/app` |
| `UPLOAD_DIR` | Local path for uploaded files | `./uploads` |
| `MAX_UPLOAD_SIZE_MB` | Upload size limit | `50` |
| `CHUNKING_STRATEGY` | Default chunker selected by the factory | `semantic` |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | Token-based chunking parameters | `512` / `50` |
| `SQL_QUERY_TIMEOUT_MS` | Guard-enforced execution timeout | `5000` |
| `SQL_MAX_ROWS` | Guard-enforced row limit | `1000` |

---

## 🔴 Key API Endpoints

Exact HTTP verbs/paths should be confirmed in each router file — this reflects the standard REST mapping implied by the route names.

```
GET    /api/health

POST   /api/documents/upload
GET    /api/documents
GET    /api/documents/{id}
DELETE /api/documents/{id}

POST   /api/search

POST   /api/sql/generate
POST   /api/sql/execute

POST   /api/chat
POST   /api/chat/stream

POST   /api/conversations
GET    /api/conversations
GET    /api/conversations/{id}
DELETE /api/conversations/{id}

GET    /api/admin/collections
POST   /api/admin/collections
```

---

## 🧩 Chunking Strategies

All strategies implement a common interface (`app/services/chunking/base.py`) and are selected at runtime via `chunker_factory.py`.

| Strategy | File | Approach |
|---|---|---|
| Text (fixed-size) | `text_chunker.py` | Simple fixed-length splitting, the baseline strategy |
| Token limit | `token_limit.py` | Splits strictly by model token budget |
| Structure-aware | `structure_chunker.py` | Splits along document structure (headings/sections) |
| Hierarchical | `hierarchical_chunker.py` | Preserves parent/section → subsection relationships |
| Parent-child | `parent_child_chunker.py` | Indexes small child chunks, retrieves with parent context attached |
| Semantic | `semantic_chunker.py` | Splits at points of semantic/topic shift rather than fixed length |
| Contextual | `contextual_chunker.py` | Prepends surrounding context to each chunk before embedding |
| Late chunking | `late_chunker.py` | Embeds the full document first, pools chunk vectors afterward |
| Proposition-based | `proposition_chunker.py` | Splits into atomic, self-contained factual statements |
| Multi-vector / HyDE | `multivector_hyde_chunker.py` | Generates multiple representative vectors per chunk (e.g. hypothetical questions/answers) |
| Agentic | `agentic_chunker.py` | Uses an LLM call to decide chunk boundaries dynamically |

Supporting modules: `metadata.py` (chunk metadata attachment) and `token_utils.py` (shared token counting).

---

## 💻 Docker Compose Services

Based on `docker-compose.yml` and the services the app depends on:

| Service | Role |
|---|---|
| `api` | FastAPI application (this repo) |
| `redis` | Queue/cache backing async ingestion and (optionally) session/history state |
| `qdrant` | Vector database for embeddings and semantic search |
| `worker` | Background ingestion process (`app/workers/ingestion_worker.py`) consuming the Redis queue |
| *(source DB, if configured)* | Target database for the Text-to-SQL pipeline, initialized from `sql/init/` |

Bring everything up:
```bash
docker-compose up --build
```

Bring down (and optionally wipe volumes):
```bash
docker-compose down -v
```

---

## 🛑 Known Limitations & Architecture Trade-offs

The following are intentional scoping decisions made for this release. They are documented here explicitly so reviewers can evaluate them as conscious choices rather than silent gaps.

| # | Item | Status | Notes |
|---|---|---|---|
| 1 | **Token streaming** | Simulated | `/api/chat/stream` runs the full orchestration pipeline to completion first, then delivers the final answer word-by-word via SSE. There is no incremental LLM token streaming. |
| 2 | **Database adapters** | PostgreSQL + MySQL only | SQL Server and Oracle adapters are not implemented. The guard and executor are dialect-aware via SQLGlot, but only Postgres and MySQL connection strings are supported at the connection service layer. |
| 3 | **Task queue** | In-process `asyncio` | Document ingestion is triggered via `asyncio` background tasks, not a persistent Celery/Dramatiq worker queue. There is no `worker` service in `docker-compose.yml`. This means in-flight jobs are lost on pod restart. |
| 4 | **Schema migrations** | SQL file only | The app DB schema is initialized from `sql/init/schema.sql`. Alembic is listed in `requirements.txt` but no migrations are generated. Schema changes require manually updating the SQL file and re-initializing. |
| 5 | **Sensitive column masking scope** | Result rows only | `mask_type` is applied to query result rows before they reach the LLM prompt or API response. It is not applied to search/retrieval chunks from document RAG. |

---

## 📜 License

This project is distributed under the MIT License. See `LICENSE` for details.

If no `LICENSE` file exists yet in the repository, add one before publishing — code without a license file is "all rights reserved" by default even if you intend it to be open source.
