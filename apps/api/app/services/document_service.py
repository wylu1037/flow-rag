from __future__ import annotations

from app.db.models import Document
from app.db.repositories import InMemoryRepository
from app.services.ingestion_service import IngestionResult, IngestionService


class DocumentService:
    def __init__(
        self,
        repository: InMemoryRepository,
        ingestion_service: IngestionService,
    ) -> None:
        self.repository = repository
        self.ingestion_service = ingestion_service

    def upload_text(
        self,
        tenant_id: str,
        dataset_id: str,
        filename: str,
        content: str,
        mime_type: str,
    ) -> IngestionResult:
        return self.ingestion_service.ingest_text(
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            filename=filename,
            content=content,
            mime_type=mime_type,
        )

    def list_documents(self, tenant_id: str, dataset_id: str | None = None) -> list[Document]:
        return self.repository.list_documents(tenant_id, dataset_id)

    def get_document(self, tenant_id: str, document_id: str) -> Document:
        return self.repository.get_document(tenant_id, document_id)

    def delete_document(self, tenant_id: str, document_id: str) -> None:
        self.repository.delete_document(tenant_id, document_id)
