from __future__ import annotations

from app.agent.tools.base import ToolResult, ok
from app.services.retrieval_service import RetrievalService


class VectorSearchTool:
    def __init__(self, retrieval_service: RetrievalService) -> None:
        self.retrieval_service = retrieval_service

    def search(
        self,
        tenant_id: str,
        dataset_ids: list[str],
        queries: list[str],
        top_k: int,
    ) -> ToolResult:
        results = self.retrieval_service.hybrid_retrieve(tenant_id, dataset_ids, queries, top_k)
        return ok(
            {"results": results},
            {
                "tool": "hybrid_retrieve",
                "tenant_id": tenant_id,
                "dataset_ids": dataset_ids,
                "result_count": len(results),
            },
        )
