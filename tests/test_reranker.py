from app.services.qdrant.search import ScoredChunk
from app.services.retrieval.reranker import Reranker


def _chunk(id_, vector, score):
    return ScoredChunk(
        id=id_,
        score=score,
        content=f"content-{id_}",
        file_id="file-1",
        file_name="doc.pdf",
        knowledge_base_id="kb-1",
        page_number=1,
        chunk_index=0,
        vector=vector,
    )


def test_rerank_without_vectors_falls_back_to_score_order():
    chunks = [_chunk("a", None, 0.5), _chunk("b", None, 0.9)]
    reranker = Reranker(lambda_param=0.5)

    ranked = reranker.rerank(query_vector=[1.0, 0.0], chunks=chunks, top_k=2)

    assert [c.id for c in ranked] == ["b", "a"]


def test_rerank_prefers_diverse_chunks_over_near_duplicates():
    # "a" and "b" point in nearly the same direction (near-duplicates of
    # each other and both highly relevant); "c" is orthogonal to "a" and
    # less relevant on its own, but carries zero redundancy.
    query_vector = [1.0, 0.0]
    chunks = [
        _chunk("a", [0.8, 0.6], score=0.99),
        _chunk("b", [0.78, 0.62], score=0.95),
        _chunk("c", [0.6, -0.8], score=0.4),
    ]
    reranker = Reranker(lambda_param=0.5)

    ranked = reranker.rerank(query_vector=query_vector, chunks=chunks, top_k=2)

    # "a" wins first (highest pure relevance). For the second slot, MMR
    # should favor "c" over the near-duplicate "b" once redundancy with
    # the already-selected "a" is penalized.
    assert ranked[0].id == "a"
    assert ranked[1].id == "c"


def test_rerank_respects_top_k():
    chunks = [_chunk(str(i), [1.0, 0.0], score=1.0 - i * 0.1) for i in range(5)]
    reranker = Reranker(lambda_param=0.5)

    ranked = reranker.rerank(query_vector=[1.0, 0.0], chunks=chunks, top_k=2)

    assert len(ranked) == 2