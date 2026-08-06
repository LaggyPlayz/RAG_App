import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.tenant_context import get_tenant_id, get_user_id
from app.db.models.knowledge_base import KnowledgeBase
from app.models.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseResponse
from app.repositories.knowledge_base_repo import KnowledgeBaseRepository
from app.utils.exceptions import DuplicateError, NotFoundError

router = APIRouter(prefix="/api/knowledge-bases", tags=["knowledge-bases"])


@router.post("", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    request: KnowledgeBaseCreate,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = KnowledgeBaseRepository(db)
    existing = await repo.get_by_name(request.name, tenant_id)
    if existing:
        raise DuplicateError(f"Knowledge base '{request.name}' already exists in tenant")

    kb = KnowledgeBase(
        tenant_id=uuid.UUID(tenant_id),
        created_by=uuid.UUID(user_id) if user_id else None,
        name=request.name,
        description=request.description,
        embedding_model=request.embedding_model,
        chunking_config=request.chunking_config,
    )
    kb = await repo.create(kb)

    return KnowledgeBaseResponse(
        id=str(kb.id),
        tenant_id=str(kb.tenant_id),
        name=kb.name,
        description=kb.description,
        embedding_model=kb.embedding_model,
        chunking_config=kb.chunking_config or {},
        file_count=0,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
    )


@router.get("", response_model=list[KnowledgeBaseResponse])
async def list_knowledge_bases(
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = KnowledgeBaseRepository(db)
    kbs = await repo.list_all(tenant_id=tenant_id)
    res = []
    for kb in kbs:
        kb_with_files = await repo.get_with_files(kb.id, tenant_id)
        file_count = len(kb_with_files.files) if kb_with_files else 0
        res.append(
            KnowledgeBaseResponse(
                id=str(kb.id),
                tenant_id=str(kb.tenant_id),
                name=kb.name,
                description=kb.description,
                embedding_model=kb.embedding_model,
                chunking_config=kb.chunking_config or {},
                file_count=file_count,
                created_at=kb.created_at,
                updated_at=kb.updated_at,
            )
        )
    return res
