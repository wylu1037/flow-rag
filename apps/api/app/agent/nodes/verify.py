from __future__ import annotations

from app.agent.tools.llm import LLMTool


class VerifierNode:
    def __init__(self, llm_tool: LLMTool) -> None:
        self.llm_tool = llm_tool

    def run(self, shared: dict) -> dict:
        result = self.llm_tool.verify(shared.get("draft_answer", ""), shared.get("evidence", []))
        shared["verification"] = result["data"]["verification"]
        return shared
