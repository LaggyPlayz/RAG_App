import numpy as np

from app.core.config import get_settings
from app.services.qdrant.search import ScoredChunk


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-8
    return float(np.dot(a, b) / denom)


class Reranker:
    """Reorders retrieved chunks using Maximal Marginal Relevance (MMR).

    MMR trades off pure similarity-to-query against redundancy between
    already-selected chunks, so the final context isn't N near-duplicate
    passages of the single most similar chunk. This is dependency-light
    (numpy only) and reuses the vectors already returned by Qdrant —
    no extra embedding calls or cross-encoder model needed.

    If you later want a cross-encoder reranker instead, swap the
    implementation of `rerank` behind this same interface; callers
    (chat.py, search.py) don't need to change.
    """

    def __init__(self, lambda_param: float | None = None):
        settings = get_settings()
        self.lambda_param = lambda_param if lambda_param is not None else settings.rerank_mmr_lambda

    def rerank(self, query_vector: list[float], chunks: list[ScoredChunk], top_k: int) -> list[ScoredChunk]:
        if not chunks:
            return []

        # Fall back to plain score order if vectors weren't fetched
        # (retrieve(..., with_vectors=False)).
        if any(c.vector is None for c in chunks):
            return sorted(chunks, key=lambda c: c.score, reverse=True)[:top_k]

        query_vec = np.array(query_vector)
        vectors = {c.id: np.array(c.vector) for c in chunks}
        relevance = {c.id: _cosine(query_vec, vectors[c.id]) for c in chunks}

        selected: list[ScoredChunk] = []
        remaining = list(chunks)

        while remaining and len(selected) < top_k:
            best_chunk, best_mmr = None, float("-inf")
            for candidate in remaining:
                sim_to_query = relevance[candidate.id]
                sim_to_selected = max(
                    (_cosine(vectors[candidate.id], vectors[s.id]) for s in selected),
                    default=0.0,
                )
                mmr_score = self.lambda_param * sim_to_query - (1 - self.lambda_param) * sim_to_selected
                if mmr_score > best_mmr:
                    best_mmr, best_chunk = mmr_score, candidate
            selected.append(best_chunk)
            remaining.remove(best_chunk)

        return selected

