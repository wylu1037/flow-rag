from __future__ import annotations

import re

from app.services.embedding_service import tokenize
from app.services.retrieval_service import RetrievedChunk


class LocalLLMService:
    """Local deterministic stand-in for query rewrite, answer, and verification."""

    def rewrite_queries(self, query: str, max_queries: int = 3) -> list[str]:
        cleaned = re.sub(r"\s+", " ", query).strip()
        if not cleaned:
            return []
        variants = [cleaned]
        without_question_words = re.sub(
            r"\b(what|why|how|when|where|who|please|tell|show|summarize|compare)\b",
            " ",
            cleaned,
            flags=re.IGNORECASE,
        )
        without_question_words = re.sub(r"\s+", " ", without_question_words).strip()
        if without_question_words and without_question_words.lower() != cleaned.lower():
            variants.append(without_question_words)
        keywords = " ".join(tokenize(cleaned)[:12])
        if keywords and keywords.lower() not in {item.lower() for item in variants}:
            variants.append(keywords)
        return variants[:max_queries]

    def draft_answer(self, query: str, evidence: list[RetrievedChunk]) -> str:
        if not evidence:
            return (
                "I could not find enough evidence in the selected knowledge bases to answer "
                "this question reliably."
            )

        snippets = [self._best_sentence(query, item.chunk.content) for item in evidence[:4]]
        snippets = [snippet for snippet in snippets if snippet]
        if not snippets:
            snippets = [item.chunk.content[:240] for item in evidence[:3]]

        lines = ["Based on the indexed evidence:"]
        for index, snippet in enumerate(snippets, start=1):
            lines.append(f"{index}. {snippet}")
        lines.append("The citations identify the source chunks used for this answer.")
        return "\n".join(lines)

    def verify_answer(self, answer: str, evidence: list[RetrievedChunk]) -> dict:
        grounded = bool(evidence) and "could not find enough evidence" not in answer.lower()
        return {
            "grounded": grounded,
            "groundedness_score": 0.9 if grounded else 0.0,
            "unsupported_claims": [] if grounded else ["No supporting evidence was selected."],
            "missing_citations": [] if evidence else ["answer"],
            "conflicting_evidence": [],
            "needs_retrieval": not evidence,
        }

    def repair_answer(self, answer: str, verification: dict, evidence: list[RetrievedChunk]) -> str:
        if verification.get("grounded"):
            return answer
        if not evidence:
            return (
                "The selected knowledge bases do not contain enough evidence to answer this "
                "reliably. Try uploading more source material or broadening the dataset selection."
            )
        return answer

    def _best_sentence(self, query: str, content: str) -> str:
        query_terms = set(tokenize(query))
        sentences = re.split(r"(?<=[.!?。！？])\s+|\n+", content)
        scored: list[tuple[float, str]] = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            terms = set(tokenize(sentence))
            score = len(query_terms.intersection(terms)) / max(1, len(query_terms))
            scored.append((score, sentence))
        if not scored:
            return content[:260]
        scored.sort(key=lambda item: item[0], reverse=True)
        best = scored[0][1]
        if len(best) < 40:
            for _, sentence in scored[1:]:
                if len(sentence) >= 40:
                    return f"{best}. {sentence}"[:360]
        return best[:360]
