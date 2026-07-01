from __future__ import annotations

import unittest

from app.agent.flows.rag_flow import AgenticRAGFlow
from app.db.repositories import InMemoryRepository
from app.services.citation_service import CitationService
from app.services.embedding_service import HashEmbeddingService
from app.services.ingestion_service import IngestionService
from app.services.llm_service import LocalLLMService
from app.services.rerank_service import RerankService
from app.services.retrieval_service import RetrievalService


def build_flow() -> tuple[InMemoryRepository, IngestionService, AgenticRAGFlow]:
    repo = InMemoryRepository.seeded()
    embedding = HashEmbeddingService()
    ingestion = IngestionService(repo, embedding)
    citation = CitationService(repo)
    flow = AgenticRAGFlow(
        repository=repo,
        retrieval_service=RetrievalService(repo, embedding),
        rerank_service=RerankService(),
        llm_service=LocalLLMService(),
        citation_service=citation,
    )
    return repo, ingestion, flow


class RAGFlowTest(unittest.TestCase):
    def test_ingestion_and_agentic_rag_flow_returns_grounded_answer(self) -> None:
        repo, ingestion, flow = build_flow()
        tenant_id = "tenant_demo"
        user_id = "user_demo"
        dataset_id = "dataset_demo"
        session = repo.create_session(tenant_id, user_id, "Contract review")

        result = ingestion.ingest_text(
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            filename="contract.md",
            mime_type="text/markdown",
            content=(
                "# Payment Terms\n"
                "The customer pays invoices within 30 days after receiving the invoice. "
                "Late payments accrue a 1.5 percent monthly fee.\n\n"
                "# Liability\n"
                "The supplier is liable for direct damages caused by gross negligence."
            ),
        )

        self.assertEqual(result.document.status, "indexed")
        self.assertEqual(result.job.status, "succeeded")
        self.assertTrue(result.chunks)

        answer = flow.run(
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session.id,
            query="What are the payment terms?",
            dataset_ids=[dataset_id],
            options={"top_k": 20},
        )

        self.assertIn("30 days", answer.answer)
        self.assertTrue(answer.citations)
        self.assertGreater(answer.confidence, 0)
        self.assertTrue(answer.trace["trace_id"].startswith("trace_"))
        self.assertGreaterEqual(
            {step["node"] for step in answer.trace["flow_steps"]},
            {
                "IntentClassifierNode",
                "RetrievalPlannerNode",
                "QueryRewriteNode",
                "HybridRetrieveNode",
                "RerankNode",
                "EvidenceFilterNode",
                "AnswerDraftNode",
                "VerifierNode",
                "FinalAnswerNode",
            },
        )

    def test_agentic_rag_flow_handles_insufficient_evidence_without_hallucination(self) -> None:
        repo, ingestion, flow = build_flow()
        tenant_id = "tenant_demo"
        user_id = "user_demo"
        dataset_id = "dataset_demo"
        session = repo.create_session(tenant_id, user_id, "Unknown question")

        ingestion.ingest_text(
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            filename="ops.md",
            mime_type="text/markdown",
            content="# Support\nEscalations are reviewed every Tuesday by the support lead.",
        )

        answer = flow.run(
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session.id,
            query="What is the customer refund limit for enterprise contracts?",
            dataset_ids=[dataset_id],
            options={"top_k": 10},
        )

        self.assertIn("not contain enough evidence", answer.answer)
        self.assertEqual(answer.confidence, 0.0)
        self.assertFalse(answer.trace["verification"]["grounded"])


if __name__ == "__main__":
    unittest.main()
