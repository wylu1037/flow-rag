from __future__ import annotations

from app.agent.tools.base import ToolResult, ok
from app.services.llm_service import LocalLLMService
from app.services.retrieval_service import RetrievedChunk


class LLMTool:
    def __init__(self, llm_service: LocalLLMService) -> None:
        self.llm_service = llm_service

    def rewrite(self, query: str, max_queries: int) -> ToolResult:
        queries = self.llm_service.rewrite_queries(query, max_queries)
        return ok({"queries": queries}, {"tool": "query_rewrite", "query_count": len(queries)})

    def draft_answer(self, query: str, evidence: list[RetrievedChunk]) -> ToolResult:
        answer = self.llm_service.draft_answer(query, evidence)
        return ok({"answer": answer}, {"tool": "answer_draft", "evidence_count": len(evidence)})

    def verify(self, answer: str, evidence: list[RetrievedChunk]) -> ToolResult:
        verification = self.llm_service.verify_answer(answer, evidence)
        return ok({"verification": verification}, {"tool": "verify"})

    def repair(self, answer: str, verification: dict, evidence: list[RetrievedChunk]) -> ToolResult:
        repaired = self.llm_service.repair_answer(answer, verification, evidence)
        return ok({"answer": repaired}, {"tool": "answer_repair"})
