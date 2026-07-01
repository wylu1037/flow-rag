from __future__ import annotations

from app.agent.tools.base import ToolResult, ok
from app.services.rerank_service import RerankService
from app.services.retrieval_service import RetrievedChunk


class RerankerTool:
    def __init__(self, rerank_service: RerankService) -> None:
        self.rerank_service = rerank_service

    def rerank(self, query: str, candidates: list[RetrievedChunk], top_k: int) -> ToolResult:
        results = self.rerank_service.rerank(query, candidates, top_k)
        return ok(
            {"results": results},
            {"tool": "rerank", "candidate_count": len(candidates), "result_count": len(results)},
        )
