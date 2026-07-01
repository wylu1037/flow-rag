from __future__ import annotations

from app.db.models import MessageCitation, new_id
from app.db.repositories import InMemoryRepository
from app.services.retrieval_service import RetrievedChunk


class CitationService:
    def __init__(self, repository: InMemoryRepository) -> None:
        self.repository = repository

    def create_message_citations(
        self,
        tenant_id: str,
        message_id: str,
        evidence: list[RetrievedChunk],
    ) -> list[MessageCitation]:
        citations = [
            MessageCitation(
                id=new_id("cite"),
                tenant_id=tenant_id,
                message_id=message_id,
                chunk_id=item.chunk.id,
                score=item.final_score,
                metadata=self.payload_for(item),
            )
            for item in evidence
        ]
        return self.repository.add_citations(citations)

    def payload_for(self, item: RetrievedChunk) -> dict:
        document = self.repository.documents.get(item.chunk.document_id)
        return {
            "document_id": item.chunk.document_id,
            "chunk_id": item.chunk.id,
            "dataset_id": item.chunk.dataset_id,
            "filename": document.filename if document else item.chunk.metadata.get("filename"),
            "section": item.chunk.metadata.get("section"),
            "chunk_index": item.chunk.chunk_index,
            "score": round(item.final_score, 4),
            "snippet": item.chunk.content[:360],
        }
