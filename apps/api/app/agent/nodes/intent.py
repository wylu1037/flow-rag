from __future__ import annotations


class IntentClassifierNode:
    def run(self, shared: dict) -> dict:
        query = shared["query"].lower()
        if not shared.get("dataset_ids"):
            intent = "needs_dataset"
        elif any(term in query for term in ["compare", "difference", "versus", "vs"]):
            intent = "comparison"
        elif any(term in query for term in ["summarize", "summary", "overview"]):
            intent = "summary"
        elif any(term in query for term in ["hello", "hi ", "thanks"]):
            intent = "chat"
        else:
            intent = "fact"
        shared["intent"] = intent
        return shared
