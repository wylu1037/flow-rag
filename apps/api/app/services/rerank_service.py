from __future__ import annotations

from app.services.embedding_service import tokenize
from app.services.retrieval_service import RetrievedChunk


class RerankService:
    def rerank(self, query: str, candidates: list[RetrievedChunk], top_k: int = 10) -> list[RetrievedChunk]:
        query_terms = tokenize(query)
        query_phrase = " ".join(query_terms)
        for candidate in candidates:
            content_terms = tokenize(candidate.chunk.content)
            content_phrase = " ".join(content_terms)
            coverage = len(set(query_terms).intersection(content_terms)) / max(1, len(set(query_terms)))
            phrase_boost = 0.15 if query_phrase and query_phrase in content_phrase else 0.0
            candidate.rerank_score = min(1.0, coverage + phrase_boost)
            candidate.final_score = (
                0.55 * candidate.vector_score
                + 0.25 * candidate.keyword_score
                + 0.20 * candidate.rerank_score
            )
        return sorted(candidates, key=lambda item: item.final_score, reverse=True)[:top_k]
