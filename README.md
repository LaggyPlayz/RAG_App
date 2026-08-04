# Multi-Tenant Text-to-SQL and Document Chat Platform (Backend)

Secure, production-grade backend platform built with **FastAPI**, **SQLAlchemy 2**, **PostgreSQL**, **Qdrant**, **Redis**, and **LangGraph**. Allows authenticated multi-tenant users to connect live business databases, upload knowledge base files (PDF, Word, Excel, CSV, text), and perform conversational database, document, and hybrid search.

---

## Key Features

- **Multi-Tenancy & Auth**: Strict tenant isolation on every entity with JWT access/refresh authentication and password hashing.
- **Runtime Connection CRUD**: Connect target SQL databases at runtime with Fernet encrypted credentials at rest.
- **Schema Discovery & Metadata Cache**: Introspect customer database schemas, tables, columns, keys, and filter by table/column permissions.
- **Safe Text-to-SQL (SQLGlot)**: AST SQL parsing and security guard blocking multi-statements, comments, DDL/DML, system schemas, and unauthorized table access.
- **Document RAG**: Document parsing (PDF, DOCX, CSV, Excel, TXT), chunking, vector embedding, and Qdrant similarity search with MMR reranking.
- **LangGraph Chat Orchestrator**: Multi-agent state graph classifying query intent (General, Database, Document, Hybrid) and merging evidence into grounded responses with citations.
- **Streaming API**: Server-Sent Events (SSE) streaming support for instant response delivery.

---

## Quick Start (Docker Compose)

```bash
# 1. Clone repository & populate environment
cp .env.example .env

# 2. Start full stack (API, PostgreSQL, Redis, Qdrant)
docker-compose up --build -d

# 3. Access Swagger UI Dashboard
# Open http://localhost:8000/docs in your browser
```

---

## Manual Local Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8000
```

---

## Running Unit & Integration Tests

```bash
pytest tests/ -v
```
