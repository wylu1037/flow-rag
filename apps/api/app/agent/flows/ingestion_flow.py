from __future__ import annotations

from app.services.ingestion_service import IngestionResult, IngestionService


class IngestionFlow:
    def __init__(self, ingestion_service: IngestionService) -> None:
        self.ingestion_service = ingestion_service

    def run(
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
