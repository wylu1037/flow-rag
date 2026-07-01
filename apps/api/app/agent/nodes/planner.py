from __future__ import annotations

from app.core.config import settings


class RetrievalPlannerNode:
    def run(self, shared: dict) -> dict:
        options = shared.get("options") or {}
        top_k = int(options.get("top_k") or settings.max_candidate_chunks)
        intent = shared.get("intent", "fact")
        shared["retrieval_plan"] = {
            "dataset_ids": shared.get("dataset_ids") or [settings.default_dataset_id],
            "top_k": min(top_k, settings.max_candidate_chunks),
            "evidence_top_k": min(int(options.get("evidence_top_k") or 8), settings.max_evidence_chunks),
            "max_rounds": settings.max_retrieval_rounds,
            "route": "fast_path" if intent in {"fact", "chat"} else "agentic_path",
        }
        return shared
