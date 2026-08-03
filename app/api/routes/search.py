from fastapi import APIRouter, Depends

from app.api.dependencies import get_reranker, get_retriever
from app.core.config import get_settings
from app.models.search import SearchRequest, SearchResponse, SearchResultItem
from app.services.retrieval.reranker import Reranker
from app.services.retrieval.retriever import Retriever

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    retriever: Retriever = Depends(get_retriever),
    reranker: Reranker = Depends(get_reranker),
):
    settings = get_settings()
    top_k = request.top_k or settings.rerank_top_k

    query_vector = await retriever.embedding_service.embed_text(request.query)
    candidates = await retriever.retrieve(
        query=request.query,
        knowledge_base_ids=request.knowledge_base_ids,
        top_k=settings.retrieval_top_k,
        with_vectors=True,
    )
    ranked = reranker.rerank(query_vector, candidates, top_k=top_k)

    results = [
        SearchResultItem(
            file_id=c.file_id,
            file_name=c.file_name,
            page_number=c.page_number,
            chunk_index=c.chunk_index,
            score=c.score,
            content=c.content,
        )
        for c in ranked
    ]
    return SearchResponse(query=request.query, results=results)