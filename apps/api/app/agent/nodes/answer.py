from __future__ import annotations

from app.agent.tools.citation_builder import CitationBuilderTool
from app.agent.tools.llm import LLMTool


class AnswerDraftNode:
    def __init__(self, llm_tool: LLMTool) -> None:
        self.llm_tool = llm_tool

    def run(self, shared: dict) -> dict:
        result = self.llm_tool.draft_answer(shared["query"], shared.get("evidence", []))
        shared["draft_answer"] = result["data"]["answer"]
        return shared


class AnswerRepairNode:
    def __init__(self, llm_tool: LLMTool) -> None:
        self.llm_tool = llm_tool

    def run(self, shared: dict) -> dict:
        result = self.llm_tool.repair(
            shared.get("draft_answer", ""),
            shared.get("verification", {}),
            shared.get("evidence", []),
        )
        shared["draft_answer"] = result["data"]["answer"]
        return shared


class FinalAnswerNode:
    def __init__(self, citation_builder: CitationBuilderTool) -> None:
        self.citation_builder = citation_builder

    def run(self, shared: dict) -> dict:
        citation_result = self.citation_builder.build_payloads(shared.get("evidence", []))
        shared["citations"] = citation_result["data"]["citations"]
        shared["final_answer"] = shared.get("draft_answer", "")
        return shared
