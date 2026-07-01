from __future__ import annotations

from app.dependencies import ingestion_service


def ingest_text_task(
    tenant_id: str,
    dataset_id: str,
    filename: str,
    content: str,
    mime_type: str = "text/plain",
) -> dict:
    result = ingestion_service.ingest_text(tenant_id, dataset_id, filename, content, mime_type)
    return {
        "document_id": result.document.id,
        "job_id": result.job.id,
        "chunk_count": len(result.chunks),
    }
