from __future__ import annotations

from app.agent.tools.reranker import RerankerTool


class RerankNode:
    def __init__(self, reranker: RerankerTool) -> None:
        self.reranker = reranker

    def run(self, shared: dict) -> dict:
        result = self.reranker.rerank(
            shared["query"],
            shared.get("retrieved_chunks", []),
            shared["retrieval_plan"]["evidence_top_k"] * 4,
        )
        shared["reranked_chunks"] = result["data"]["results"]
        return shared
