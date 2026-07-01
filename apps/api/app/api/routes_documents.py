from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.config import settings
from app.core.errors import ValidationError
from app.core.security import Principal
from app.db.models import public_dict
from app.dependencies import document_service, get_principal

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    dataset_id: str = Form(default=settings.default_dataset_id),
    principal: Principal = Depends(get_principal),
) -> dict:
    raw = await file.read()
    if len(raw) > settings.max_upload_bytes:
        raise ValidationError("Uploaded document exceeds the configured size limit.")
    text = raw.decode("utf-8", errors="ignore")
    result = document_service.upload_text(
        tenant_id=principal.tenant_id,
        dataset_id=dataset_id,
        filename=file.filename or "uploaded.txt",
        content=text,
        mime_type=file.content_type or "text/plain",
    )
    return {
        "document_id": result.document.id,
        "job_id": result.job.id,
        "status": result.job.status,
        "chunk_count": len(result.chunks),
    }


@router.get("")
def list_documents(
    dataset_id: str | None = None,
    principal: Principal = Depends(get_principal),
) -> list[dict]:
    return [
        public_dict(document)
        for document in document_service.list_documents(principal.tenant_id, dataset_id)
    ]


@router.get("/{document_id}")
def get_document(document_id: str, principal: Principal = Depends(get_principal)) -> dict:
    return public_dict(document_service.get_document(principal.tenant_id, document_id))


@router.delete("/{document_id}")
def delete_document(document_id: str, principal: Principal = Depends(get_principal)) -> dict:
    document_service.delete_document(principal.tenant_id, document_id)
    return {"deleted": True, "document_id": document_id}


@router.post("/{document_id}/reindex")
def reindex_document(document_id: str, principal: Principal = Depends(get_principal)) -> dict:
    document = document_service.get_document(principal.tenant_id, document_id)
    return {"document_id": document.id, "status": "queued"}
