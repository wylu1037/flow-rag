from __future__ import annotations

import re

from app.agent.tools.llm import LLMTool
from app.core.config import settings


class QueryRewriteNode:
    def __init__(self, llm_tool: LLMTool) -> None:
        self.llm_tool = llm_tool

    def run(self, shared: dict) -> dict:
        result = self.llm_tool.rewrite(shared["query"], settings.max_rewritten_queries)
        shared["rewritten_queries"] = result["data"]["queries"]
        return shared


class SubQuestionNode:
    def run(self, shared: dict) -> dict:
        query = shared["query"]
        pieces = re.split(r"\b(?:and|also|versus|vs|compare)\b|[?？;；]", query, flags=re.IGNORECASE)
        sub_questions = [piece.strip() for piece in pieces if piece.strip()]
        shared["sub_questions"] = sub_questions[:5]
        if shared["sub_questions"]:
            shared["rewritten_queries"] = list(
                dict.fromkeys(shared.get("rewritten_queries", []) + shared["sub_questions"])
            )
        return shared
