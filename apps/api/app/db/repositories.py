from __future__ import annotations

from dataclasses import replace
from threading import RLock
from typing import Iterable

from app.core.config import settings
from app.core.errors import NotFoundError, PermissionDeniedError
from app.db.models import (
    ChatMessage,
    ChatSession,
    Dataset,
    Document,
    DocumentChunk,
    DocumentStatus,
    IngestionJob,
    JobStatus,
    MessageCitation,
    MessageRole,
    Tenant,
    User,
    new_id,
    utcnow,
)


class InMemoryRepository:
    """Thread-safe in-memory repository used by the MVP and unit tests."""

    def __init__(self) -> None:
        self._lock = RLock()
        self.tenants: dict[str, Tenant] = {}
        self.users: dict[str, User] = {}
        self.datasets: dict[str, Dataset] = {}
        self.documents: dict[str, Document] = {}
        self.chunks: dict[str, DocumentChunk] = {}
        self.sessions: dict[str, ChatSession] = {}
        self.messages: dict[str, ChatMessage] = {}
        self.citations: dict[str, MessageCitation] = {}
        self.jobs: dict[str, IngestionJob] = {}

    @classmethod
    def seeded(cls) -> "InMemoryRepository":
        repo = cls()
        tenant = Tenant(id=settings.default_tenant_id, name="Demo Tenant")
        user = User(
            id=settings.default_user_id,
            tenant_id=tenant.id,
            email="demo@flowrag.local",
            role="owner",
        )
        dataset = Dataset(
            id=settings.default_dataset_id,
            tenant_id=tenant.id,
            name="Demo Knowledge Base",
            description="Upload documents here to try the local FlowRAG loop.",
        )
        repo.tenants[tenant.id] = tenant
        repo.users[user.id] = user
        repo.datasets[dataset.id] = dataset
        return repo

    def ensure_tenant(self, tenant_id: str) -> None:
        if tenant_id not in self.tenants:
            raise PermissionDeniedError(f"Unknown tenant: {tenant_id}")

    def list_datasets(self, tenant_id: str) -> list[Dataset]:
        with self._lock:
            return [dataset for dataset in self.datasets.values() if dataset.tenant_id == tenant_id]

    def create_dataset(
        self,
        tenant_id: str,
        name: str,
        description: str = "",
        dataset_id: str | None = None,
    ) -> Dataset:
        with self._lock:
            self.ensure_tenant(tenant_id)
            dataset = Dataset(
                id=dataset_id or new_id("dataset"),
                tenant_id=tenant_id,
                name=name,
                description=description,
            )
            self.datasets[dataset.id] = dataset
            return dataset

    def get_dataset(self, tenant_id: str, dataset_id: str) -> Dataset:
        with self._lock:
            dataset = self.datasets.get(dataset_id)
            if not dataset or dataset.tenant_id != tenant_id:
                raise NotFoundError(f"Dataset not found: {dataset_id}")
            return dataset

    def update_dataset(
        self,
        tenant_id: str,
        dataset_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> Dataset:
        with self._lock:
            dataset = self.get_dataset(tenant_id, dataset_id)
            updated = replace(
                dataset,
                name=name if name is not None else dataset.name,
                description=description if description is not None else dataset.description,
            )
            self.datasets[dataset_id] = updated
            return updated

    def delete_dataset(self, tenant_id: str, dataset_id: str) -> None:
        with self._lock:
            self.get_dataset(tenant_id, dataset_id)
            self.datasets.pop(dataset_id, None)

    def create_document(
        self,
        tenant_id: str,
        dataset_id: str,
        filename: str,
        mime_type: str,
        content_hash: str,
        metadata: dict,
    ) -> Document:
        with self._lock:
            self.get_dataset(tenant_id, dataset_id)
            document = Document(
                id=new_id("doc"),
                tenant_id=tenant_id,
                dataset_id=dataset_id,
                filename=filename,
                mime_type=mime_type,
                storage_uri=f"memory://{tenant_id}/{dataset_id}/{filename}",
                status=DocumentStatus.UPLOADED,
                content_hash=content_hash,
                metadata=metadata,
            )
            self.documents[document.id] = document
            return document

    def update_document_status(
        self,
        tenant_id: str,
        document_id: str,
        status: DocumentStatus,
    ) -> Document:
        with self._lock:
            document = self.get_document(tenant_id, document_id)
            updated = replace(document, status=status)
            self.documents[document_id] = updated
            return updated

    def get_document(self, tenant_id: str, document_id: str) -> Document:
        with self._lock:
            document = self.documents.get(document_id)
            if not document or document.tenant_id != tenant_id:
                raise NotFoundError(f"Document not found: {document_id}")
            return document

    def list_documents(self, tenant_id: str, dataset_id: str | None = None) -> list[Document]:
        with self._lock:
            documents = [
                document for document in self.documents.values() if document.tenant_id == tenant_id
            ]
            if dataset_id:
                documents = [document for document in documents if document.dataset_id == dataset_id]
            return sorted(documents, key=lambda document: document.created_at, reverse=True)

    def delete_document(self, tenant_id: str, document_id: str) -> None:
        with self._lock:
            self.get_document(tenant_id, document_id)
            self.documents.pop(document_id, None)
            for chunk_id, chunk in list(self.chunks.items()):
                if chunk.document_id == document_id and chunk.tenant_id == tenant_id:
                    self.chunks.pop(chunk_id, None)

    def add_chunks(self, chunks: Iterable[DocumentChunk]) -> list[DocumentChunk]:
        with self._lock:
            saved = list(chunks)
            for chunk in saved:
                self.chunks[chunk.id] = chunk
            return saved

    def list_chunks(
        self,
        tenant_id: str,
        dataset_ids: list[str] | None = None,
        document_id: str | None = None,
    ) -> list[DocumentChunk]:
        with self._lock:
            chunks = [chunk for chunk in self.chunks.values() if chunk.tenant_id == tenant_id]
            if dataset_ids:
                allowed = set(dataset_ids)
                chunks = [chunk for chunk in chunks if chunk.dataset_id in allowed]
            if document_id:
                chunks = [chunk for chunk in chunks if chunk.document_id == document_id]
            return sorted(chunks, key=lambda chunk: (chunk.document_id, chunk.chunk_index))

    def create_job(self, tenant_id: str, document_id: str) -> IngestionJob:
        with self._lock:
            job = IngestionJob(id=new_id("job"), tenant_id=tenant_id, document_id=document_id, status=JobStatus.QUEUED)
            self.jobs[job.id] = job
            return job

    def update_job(
        self,
        tenant_id: str,
        job_id: str,
        status: JobStatus,
        stage: str,
        progress: float,
        error: str | None = None,
        stats: dict | None = None,
    ) -> IngestionJob:
        with self._lock:
            job = self.get_job(tenant_id, job_id)
            updated = replace(
                job,
                status=status,
                stage=stage,
                progress=progress,
                error=error,
                stats=stats if stats is not None else job.stats,
                updated_at=utcnow(),
            )
            self.jobs[job_id] = updated
            return updated

    def get_job(self, tenant_id: str, job_id: str) -> IngestionJob:
        with self._lock:
            job = self.jobs.get(job_id)
            if not job or job.tenant_id != tenant_id:
                raise NotFoundError(f"Job not found: {job_id}")
            return job

    def list_jobs(self, tenant_id: str, status: str | None = None) -> list[IngestionJob]:
        with self._lock:
            jobs = [job for job in self.jobs.values() if job.tenant_id == tenant_id]
            if status:
                jobs = [job for job in jobs if job.status == status]
            return sorted(jobs, key=lambda job: job.created_at, reverse=True)

    def create_session(self, tenant_id: str, user_id: str, title: str = "New chat") -> ChatSession:
        with self._lock:
            session = ChatSession(id=new_id("session"), tenant_id=tenant_id, user_id=user_id, title=title)
            self.sessions[session.id] = session
            return session

    def list_sessions(self, tenant_id: str, user_id: str) -> list[ChatSession]:
        with self._lock:
            sessions = [
                session
                for session in self.sessions.values()
                if session.tenant_id == tenant_id and session.user_id == user_id
            ]
            return sorted(sessions, key=lambda session: session.created_at, reverse=True)

    def get_session(self, tenant_id: str, session_id: str) -> ChatSession:
        with self._lock:
            session = self.sessions.get(session_id)
            if not session or session.tenant_id != tenant_id:
                raise NotFoundError(f"Chat session not found: {session_id}")
            return session

    def add_message(
        self,
        tenant_id: str,
        session_id: str,
        role: MessageRole,
        content: str,
        trace: dict | None = None,
    ) -> ChatMessage:
        with self._lock:
            self.get_session(tenant_id, session_id)
            message = ChatMessage(
                id=new_id("msg"),
                tenant_id=tenant_id,
                session_id=session_id,
                role=role,
                content=content,
                trace=trace or {},
            )
            self.messages[message.id] = message
            return message

    def list_messages(self, tenant_id: str, session_id: str) -> list[ChatMessage]:
        with self._lock:
            self.get_session(tenant_id, session_id)
            messages = [
                message
                for message in self.messages.values()
                if message.tenant_id == tenant_id and message.session_id == session_id
            ]
            return sorted(messages, key=lambda message: message.created_at)

    def add_citations(self, citations: Iterable[MessageCitation]) -> list[MessageCitation]:
        with self._lock:
            saved = list(citations)
            for citation in saved:
                self.citations[citation.id] = citation
            return saved

    def list_citations(self, tenant_id: str, message_id: str) -> list[MessageCitation]:
        with self._lock:
            citations = [
                citation
                for citation in self.citations.values()
                if citation.tenant_id == tenant_id and citation.message_id == message_id
            ]
            return sorted(citations, key=lambda citation: citation.score, reverse=True)


repository = InMemoryRepository.seeded()
