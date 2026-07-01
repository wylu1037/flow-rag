from __future__ import annotations

from app.agent.tools.metadata_filter import MetadataFilterTool
from app.agent.tools.vector_search import VectorSearchTool


class HybridRetrieveNode:
    def __init__(
        self,
        metadata_filter: MetadataFilterTool,
        vector_search: VectorSearchTool,
    ) -> None:
        self.metadata_filter = metadata_filter
        self.vector_search = vector_search

    def run(self, shared: dict) -> dict:
        plan = shared["retrieval_plan"]
        dataset_result = self.metadata_filter.validate_datasets(
            shared["tenant_id"], plan["dataset_ids"]
        )
        if not dataset_result["ok"]:
            shared["retrieved_chunks"] = []
            shared["tool_errors"].append(dataset_result)
            return shared

        result = self.vector_search.search(
            tenant_id=shared["tenant_id"],
            dataset_ids=dataset_result["data"]["dataset_ids"],
            queries=shared.get("rewritten_queries") or [shared["query"]],
            top_k=plan["top_k"],
        )
        shared["retrieved_chunks"] = result["data"]["results"]
        return shared


class EvidenceFilterNode:
    def run(self, shared: dict) -> dict:
        top_k = shared["retrieval_plan"]["evidence_top_k"]
        seen = set()
        evidence = []
        for item in shared.get("reranked_chunks", []):
            if item.chunk.id in seen:
                continue
            seen.add(item.chunk.id)
            if item.final_score >= 0.12 or item.keyword_score > 0:
                evidence.append(item)
            if len(evidence) >= top_k:
                break
        shared["evidence"] = evidence
        return shared
