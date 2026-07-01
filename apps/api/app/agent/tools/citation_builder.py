from __future__ import annotations

from app.agent.tools.base import ToolResult, ok
from app.services.citation_service import CitationService
from app.services.retrieval_service import RetrievedChunk


class CitationBuilderTool:
    def __init__(self, citation_service: CitationService) -> None:
        self.citation_service = citation_service

    def build_payloads(self, evidence: list[RetrievedChunk]) -> ToolResult:
        citations = [self.citation_service.payload_for(item) for item in evidence]
        return ok({"citations": citations}, {"citation_count": len(citations)})
