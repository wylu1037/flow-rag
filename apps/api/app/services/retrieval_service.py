from __future__ import annotations

from dataclasses import dataclass

from app.db.models import DocumentChunk
from app.db.repositories import InMemoryRepository
from app.services.embedding_service import HashEmbeddingService, tokenize


@dataclass
class RetrievedChunk:
    chunk: DocumentChunk
    vector_score: float
    keyword_score: float
    rerank_score: float
    final_score: float
    matched_terms: list[str]

    def to_trace(self) -> dict:
        return {
            "chunk_id": self.chunk.id,
            "document_id": self.chunk.document_id,
            "dataset_id": self.chunk.dataset_id,
            "score": round(self.final_score, 4),
            "vector_score": round(self.vector_score, 4),
            "keyword_score": round(self.keyword_score, 4),
            "rerank_score": round(self.rerank_score, 4),
            "matched_terms": self.matched_terms[:12],
            "section": self.chunk.metadata.get("section"),
        }


class RetrievalService:
    def __init__(
        self,
        repository: InMemoryRepository,
        embedding_service: HashEmbeddingService,
    ) -> None:
        self.repository = repository
        self.embedding_service = embedding_service

    def hybrid_retrieve(
        self,
        tenant_id: str,
        dataset_ids: list[str],
        queries: list[str],
        top_k: int = 40,
    ) -> list[RetrievedChunk]:
        query_text = " ".join(queries)
        query_vector = self.embedding_service.embed(query_text)
        query_terms = set(tokenize(query_text))
        candidates: dict[str, RetrievedChunk] = {}

        for chunk in self.repository.list_chunks(tenant_id, dataset_ids=dataset_ids):
            chunk_terms = set(tokenize(chunk.content))
            matched = sorted(query_terms.intersection(chunk_terms))
            keyword_score = len(matched) / max(1, len(query_terms))
            vector_score = self.embedding_service.cosine(query_vector, chunk.embedding)
            final_score = 0.65 * vector_score + 0.35 * keyword_score
            if final_score <= 0:
                continue
            existing = candidates.get(chunk.id)
            retrieved = RetrievedChunk(
                chunk=chunk,
                vector_score=vector_score,
                keyword_score=keyword_score,
                rerank_score=0.0,
                final_score=final_score,
                matched_terms=matched,
            )
            if existing is None or retrieved.final_score > existing.final_score:
                candidates[chunk.id] = retrieved

        ranked = sorted(candidates.values(), key=lambda item: item.final_score, reverse=True)
        return ranked[:top_k]
