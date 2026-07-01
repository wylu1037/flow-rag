from __future__ import annotations

from fastapi import Header, Request

from app.agent.flows.rag_flow import AgenticRAGFlow
from app.core.security import Principal, principal_from_headers
from app.db.repositories import repository
from app.services.chat_service import ChatService
from app.services.citation_service import CitationService
from app.services.dataset_service import DatasetService
from app.services.document_service import DocumentService
from app.services.embedding_service import HashEmbeddingService
from app.services.ingestion_service import IngestionService
from app.services.llm_service import LocalLLMService
from app.services.rerank_service import RerankService
from app.services.retrieval_service import RetrievalService

embedding_service = HashEmbeddingService()
ingestion_service = IngestionService(repository, embedding_service)
retrieval_service = RetrievalService(repository, embedding_service)
rerank_service = RerankService()
llm_service = LocalLLMService()
citation_service = CitationService(repository)
rag_flow = AgenticRAGFlow(
    repository=repository,
    retrieval_service=retrieval_service,
    rerank_service=rerank_service,
    llm_service=llm_service,
    citation_service=citation_service,
)
dataset_service = DatasetService(repository)
document_service = DocumentService(repository, ingestion_service)
chat_service = ChatService(repository, rag_flow, citation_service)


def get_principal(
    request: Request,
    x_tenant_id: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
    x_role: str | None = Header(default=None),
) -> Principal:
    principal = getattr(request.state, "principal", None)
    if principal is not None:
        return principal
    return principal_from_headers(x_tenant_id, x_user_id, x_role)
