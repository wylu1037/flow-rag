from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from app.core.errors import IngestionError, ValidationError
from app.db.models import Document, DocumentChunk, DocumentStatus, IngestionJob, JobStatus, new_id
from app.db.repositories import InMemoryRepository
from app.services.embedding_service import HashEmbeddingService, tokenize


@dataclass(frozen=True)
class IngestionResult:
    document: Document
    job: IngestionJob
    chunks: list[DocumentChunk]


class IngestionService:
    def __init__(
        self,
        repository: InMemoryRepository,
        embedding_service: HashEmbeddingService,
        chunk_size: int = 220,
        overlap: int = 40,
    ) -> None:
        self.repository = repository
        self.embedding_service = embedding_service
        self.chunk_size = chunk_size
        self.overlap = overlap

    def ingest_text(
        self,
        tenant_id: str,
        dataset_id: str,
        filename: str,
        content: str,
        mime_type: str = "text/plain",
        metadata: dict | None = None,
    ) -> IngestionResult:
        content = content.strip()
        if not content:
            raise ValidationError("Uploaded document is empty.")

        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        document = self.repository.create_document(
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            filename=filename,
            mime_type=mime_type,
            content_hash=f"sha256:{content_hash}",
            metadata=metadata or {},
        )
        job = self.repository.create_job(tenant_id, document.id)

        try:
            self.repository.update_job(tenant_id, job.id, JobStatus.RUNNING, "parsing", 0.15)
            self.repository.update_document_status(tenant_id, document.id, DocumentStatus.PARSING)
            sections = self._sections(content)

            self.repository.update_job(tenant_id, job.id, JobStatus.RUNNING, "chunking", 0.35)
            self.repository.update_document_status(tenant_id, document.id, DocumentStatus.CHUNKING)
            chunk_texts = self._chunk_sections(sections)

            self.repository.update_job(tenant_id, job.id, JobStatus.RUNNING, "embedding", 0.65)
            self.repository.update_document_status(tenant_id, document.id, DocumentStatus.EMBEDDING)
            chunks = [
                DocumentChunk(
                    id=new_id("chunk"),
                    tenant_id=tenant_id,
                    dataset_id=dataset_id,
                    document_id=document.id,
                    chunk_index=index,
                    content=self._searchable_content(item["section"], item["content"]),
                    metadata={
                        "filename": filename,
                        "mime_type": mime_type,
                        "section": item["section"],
                        "chunk_index": index,
                        "content_hash": f"sha256:{content_hash}",
                    },
                    embedding=self.embedding_service.embed(item["content"]),
                )
                for index, item in enumerate(chunk_texts)
            ]
            self.repository.add_chunks(chunks)
            document = self.repository.update_document_status(
                tenant_id, document.id, DocumentStatus.INDEXED
            )
            job = self.repository.update_job(
                tenant_id,
                job.id,
                JobStatus.SUCCEEDED,
                "indexed",
                1.0,
                stats={"chunk_count": len(chunks), "token_count": len(tokenize(content))},
            )
            return IngestionResult(document=document, job=job, chunks=chunks)
        except Exception as exc:  # pragma: no cover - defensive status update
            self.repository.update_document_status(tenant_id, document.id, DocumentStatus.FAILED)
            self.repository.update_job(
                tenant_id, job.id, JobStatus.FAILED, "failed", 1.0, error=str(exc)
            )
            if isinstance(exc, (ValidationError, IngestionError)):
                raise
            raise IngestionError(str(exc)) from exc

    def _sections(self, content: str) -> list[dict[str, str]]:
        current = "Document"
        sections: list[dict[str, str]] = []
        buffer: list[str] = []
        for raw_line in content.splitlines():
            line = raw_line.strip()
            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading and buffer:
                sections.append({"section": current, "content": "\n".join(buffer).strip()})
                buffer = []
            if heading:
                current = heading.group(2).strip()
            elif line:
                buffer.append(line)
        if buffer:
            sections.append({"section": current, "content": "\n".join(buffer).strip()})
        if not sections:
            sections.append({"section": current, "content": content})
        return sections

    def _chunk_sections(self, sections: list[dict[str, str]]) -> list[dict[str, str]]:
        chunks: list[dict[str, str]] = []
        step = max(1, self.chunk_size - self.overlap)
        for section in sections:
            words = section["content"].split()
            if len(words) <= self.chunk_size:
                chunks.append(section)
                continue
            for start in range(0, len(words), step):
                piece = " ".join(words[start : start + self.chunk_size]).strip()
                if piece:
                    chunks.append({"section": section["section"], "content": piece})
        return chunks

    def _searchable_content(self, section: str, content: str) -> str:
        if section == "Document":
            return content
        return f"{section}\n{content}"
