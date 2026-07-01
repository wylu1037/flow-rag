from __future__ import annotations

from app.agent.tools.base import ToolResult, failed, ok
from app.db.repositories import InMemoryRepository


class DocumentLookupTool:
    def __init__(self, repository: InMemoryRepository) -> None:
        self.repository = repository

    def lookup_chunk(self, tenant_id: str, chunk_id: str) -> ToolResult:
        chunk = self.repository.chunks.get(chunk_id)
        if not chunk or chunk.tenant_id != tenant_id:
            return failed("CHUNK_NOT_FOUND", f"Chunk not found: {chunk_id}")
        return ok({"chunk": chunk}, {"chunk_id": chunk.id, "document_id": chunk.document_id})
