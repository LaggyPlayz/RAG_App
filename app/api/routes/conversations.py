import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.tenant_context import get_tenant_id, get_user_id
from app.db.models.conversation import Conversation
from app.models.conversation import ConversationCreate, ConversationResponse, MessageResponse
from app.models.common import Citation
from app.repositories.conversation_repo import ConversationRepository
from app.utils.exceptions import NotFoundError

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ConversationRepository(db)
    conv = Conversation(
        tenant_id=uuid.UUID(tenant_id),
        user_id=uuid.UUID(user_id),
        title=request.title or "New Conversation",
        active_connection_ids=request.active_connection_ids,
        active_knowledge_base_ids=request.active_knowledge_base_ids,
    )
    conv = await repo.create(conv)
    return ConversationResponse(
        id=str(conv.id),
        tenant_id=str(conv.tenant_id),
        user_id=str(conv.user_id),
        title=conv.title,
        status=conv.status,
        active_connection_ids=conv.active_connection_ids,
        active_knowledge_base_ids=conv.active_knowledge_base_ids,
        last_message_at=conv.last_message_at,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[],
    )


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    user_id: str = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ConversationRepository(db)
    convs = await repo.list_by_user(user_id)
    return [
        ConversationResponse(
            id=str(c.id),
            tenant_id=str(c.tenant_id),
            user_id=str(c.user_id),
            title=c.title,
            status=c.status,
            active_connection_ids=c.active_connection_ids,
            active_knowledge_base_ids=c.active_knowledge_base_ids,
            last_message_at=c.last_message_at,
            created_at=c.created_at,
            updated_at=c.updated_at,
            messages=[],
        )
        for c in convs
    ]


@router.get("/{id}", response_model=ConversationResponse)
async def get_conversation(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ConversationRepository(db)
    conv = await repo.get_with_messages(id, tenant_id=tenant_id)
    if not conv:
        raise NotFoundError(f"Conversation '{id}' not found")

    messages_res = []
    for m in conv.messages:
        cits = [
            Citation(
                file_id=str(cit.file_id) if cit.file_id else "",
                file_name=cit.title or "file",
                page_number=cit.page_number,
                score=float(cit.relevance_score or 1.0),
            )
            for cit in m.citations
        ]
        messages_res.append(
            MessageResponse(
                id=str(m.id),
                conversation_id=str(m.conversation_id),
                role=m.role,
                message_type=m.message_type,
                content=m.content,
                structured_content=m.structured_content,
                detected_intent=m.detected_intent,
                selected_sources=m.selected_sources or [],
                citations=cits,
                status=m.status,
                created_at=m.created_at,
            )
        )

    return ConversationResponse(
        id=str(conv.id),
        tenant_id=str(conv.tenant_id),
        user_id=str(conv.user_id),
        title=conv.title,
        status=conv.status,
        active_connection_ids=conv.active_connection_ids,
        active_knowledge_base_ids=conv.active_knowledge_base_ids,
        last_message_at=conv.last_message_at,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=messages_res,
    )


@router.delete("/{id}")
async def delete_conversation(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ConversationRepository(db)
    deleted = await repo.delete(id, tenant_id=tenant_id)
    if not deleted:
        raise NotFoundError(f"Conversation '{id}' not found")
    return {"status": "ok", "message": f"Conversation '{id}' deleted"}
