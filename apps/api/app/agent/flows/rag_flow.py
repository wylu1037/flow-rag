from __future__ import annotations

import time
from dataclasses import dataclass

from app.agent.nodes.answer import AnswerDraftNode, AnswerRepairNode, FinalAnswerNode
from app.agent.nodes.intent import IntentClassifierNode
from app.agent.nodes.planner import RetrievalPlannerNode
from app.agent.nodes.rerank import RerankNode
from app.agent.nodes.retrieve import EvidenceFilterNode, HybridRetrieveNode
from app.agent.nodes.rewrite import QueryRewriteNode, SubQuestionNode
from app.agent.nodes.verify import VerifierNode
from app.agent.tools.citation_builder import CitationBuilderTool
from app.agent.tools.llm import LLMTool
from app.agent.tools.metadata_filter import MetadataFilterTool
from app.agent.tools.reranker import RerankerTool
from app.agent.tools.vector_search import VectorSearchTool
from app.db.models import new_id
from app.db.repositories import InMemoryRepository
from app.services.citation_service import CitationService
from app.services.llm_service import LocalLLMService
from app.services.rerank_service import RerankService
from app.services.retrieval_service import RetrievalService, RetrievedChunk


@dataclass(frozen=True)
class RAGResult:
    answer: str
    citations: list[dict]
    evidence: list[RetrievedChunk]
    trace: dict
    confidence: float


class AgenticRAGFlow:
    def __init__(
        self,
        repository: InMemoryRepository,
        retrieval_service: RetrievalService,
        rerank_service: RerankService,
        llm_service: LocalLLMService,
        citation_service: CitationService,
    ) -> None:
        llm_tool = LLMTool(llm_service)
        self.nodes = {
            "IntentClassifierNode": IntentClassifierNode(),
            "RetrievalPlannerNode": RetrievalPlannerNode(),
            "QueryRewriteNode": QueryRewriteNode(llm_tool),
            "SubQuestionNode": SubQuestionNode(),
            "HybridRetrieveNode": HybridRetrieveNode(
                MetadataFilterTool(repository),
                VectorSearchTool(retrieval_service),
            ),
            "RerankNode": RerankNode(RerankerTool(rerank_service)),
            "EvidenceFilterNode": EvidenceFilterNode(),
            "AnswerDraftNode": AnswerDraftNode(llm_tool),
            "VerifierNode": VerifierNode(llm_tool),
            "AnswerRepairNode": AnswerRepairNode(llm_tool),
            "FinalAnswerNode": FinalAnswerNode(CitationBuilderTool(citation_service)),
        }

    def run(
        self,
        tenant_id: str,
        user_id: str,
        session_id: str,
        query: str,
        dataset_ids: list[str],
        options: dict | None = None,
    ) -> RAGResult:
        trace_id = new_id("trace")
        started = time.perf_counter()
        shared = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "conversation_id": session_id,
            "message_id": None,
            "query": query,
            "dataset_ids": dataset_ids,
            "options": options or {},
            "intent": None,
            "retrieval_plan": {},
            "rewritten_queries": [],
            "sub_questions": [],
            "retrieved_chunks": [],
            "reranked_chunks": [],
            "evidence": [],
            "draft_answer": "",
            "final_answer": "",
            "citations": [],
            "verification": {},
            "tool_errors": [],
            "trace": {
                "trace_id": trace_id,
                "tenant_id": tenant_id,
                "session_id": session_id,
                "flow_steps": [],
            },
        }

        for name in [
            "IntentClassifierNode",
            "RetrievalPlannerNode",
            "QueryRewriteNode",
            "HybridRetrieveNode",
            "RerankNode",
            "EvidenceFilterNode",
        ]:
            self._run_node(name, shared)

        if not shared["evidence"] and shared["retrieval_plan"].get("route") == "agentic_path":
            self._run_node("SubQuestionNode", shared)
            self._run_node("HybridRetrieveNode", shared)
            self._run_node("RerankNode", shared)
            self._run_node("EvidenceFilterNode", shared)

        self._run_node("AnswerDraftNode", shared)
        self._run_node("VerifierNode", shared)
        if not shared.get("verification", {}).get("grounded"):
            self._run_node("AnswerRepairNode", shared)
            self._run_node("VerifierNode", shared)
        self._run_node("FinalAnswerNode", shared)

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        evidence = shared.get("evidence", [])
        avg_score = sum(item.final_score for item in evidence) / max(1, len(evidence))
        verification_score = float(shared.get("verification", {}).get("groundedness_score") or 0.0)
        confidence = round((avg_score + verification_score) / 2, 4) if evidence else 0.0
        shared["trace"].update(
            {
                "latency_ms": elapsed_ms,
                "intent": shared.get("intent"),
                "retrieval_plan": shared.get("retrieval_plan"),
                "rewritten_queries": shared.get("rewritten_queries"),
                "sub_questions": shared.get("sub_questions"),
                "retrieval_top_k": shared.get("retrieval_plan", {}).get("top_k"),
                "rerank_top_k": len(shared.get("reranked_chunks", [])),
                "selected_chunks": [item.chunk.id for item in evidence],
                "verification": shared.get("verification"),
                "tool_error_count": len(shared.get("tool_errors", [])),
            }
        )

        return RAGResult(
            answer=shared.get("final_answer", ""),
            citations=shared.get("citations", []),
            evidence=evidence,
            trace=shared["trace"],
            confidence=confidence,
        )

    def _run_node(self, name: str, shared: dict) -> None:
        started = time.perf_counter()
        status = "ok"
        try:
            self.nodes[name].run(shared)
        except Exception as exc:  # pragma: no cover - defensive trace capture
            status = "error"
            shared["tool_errors"].append({"node": name, "message": str(exc)})
            raise
        finally:
            shared["trace"]["flow_steps"].append(
                {
                    "node": name,
                    "latency_ms": int((time.perf_counter() - started) * 1000),
                    "status": status,
                }
            )
