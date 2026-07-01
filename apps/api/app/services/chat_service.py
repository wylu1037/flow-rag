from __future__ import annotations

import json
from dataclasses import dataclass

from app.agent.flows.rag_flow import AgenticRAGFlow, RAGResult
from app.db.models import ChatMessage, ChatSession, MessageRole, public_dict
from app.db.repositories import InMemoryRepository
from app.services.citation_service import CitationService


@dataclass(frozen=True)
class ChatTurn:
    user_message: ChatMessage
    assistant_message: ChatMessage
    rag_result: RAGResult
    stream_url: str


class ChatService:
    def __init__(
        self,
        repository: InMemoryRepository,
        rag_flow: AgenticRAGFlow,
        citation_service: CitationService,
    ) -> None:
        self.repository = repository
        self.rag_flow = rag_flow
        self.citation_service = citation_service
        self._stream_events: dict[str, list[dict]] = {}

    def create_session(self, tenant_id: str, user_id: str, title: str = "New chat") -> ChatSession:
        return self.repository.create_session(tenant_id, user_id, title)

    def list_sessions(self, tenant_id: str, user_id: str) -> list[ChatSession]:
        return self.repository.list_sessions(tenant_id, user_id)

    def get_session(self, tenant_id: str, session_id: str) -> ChatSession:
        return self.repository.get_session(tenant_id, session_id)

    def list_messages(self, tenant_id: str, session_id: str) -> list[ChatMessage]:
        return self.repository.list_messages(tenant_id, session_id)

    def create_message(
        self,
        tenant_id: str,
        user_id: str,
        session_id: str,
        content: str,
        dataset_ids: list[str],
        options: dict | None = None,
    ) -> ChatTurn:
        user_message = self.repository.add_message(
            tenant_id=tenant_id,
            session_id=session_id,
            role=MessageRole.USER,
            content=content,
        )
        result = self.rag_flow.run(
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session_id,
            query=content,
            dataset_ids=dataset_ids,
            options=options or {},
        )
        assistant_message = self.repository.add_message(
            tenant_id=tenant_id,
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=result.answer,
            trace=result.trace,
        )
        self.citation_service.create_message_citations(
            tenant_id=tenant_id,
            message_id=assistant_message.id,
            evidence=result.evidence,
        )
        stream_url = f"/api/chat/sessions/{session_id}/stream?message_id={assistant_message.id}"
        self._stream_events[assistant_message.id] = self._build_stream_events(assistant_message, result)
        return ChatTurn(
            user_message=user_message,
            assistant_message=assistant_message,
            rag_result=result,
            stream_url=stream_url,
        )

    def stream_events(self, message_id: str) -> list[dict]:
        return self._stream_events.get(message_id, [])

    def _build_stream_events(self, message: ChatMessage, result: RAGResult) -> list[dict]:
        events: list[dict] = []
        for token in self._token_chunks(result.answer):
            events.append({"event": "token", "data": {"text": token}})
        for citation in result.citations:
            events.append({"event": "citation", "data": citation})
        events.append(
            {
                "event": "trace",
                "data": {
                    "trace_id": result.trace.get("trace_id"),
                    "flow_steps": result.trace.get("flow_steps", []),
                    "confidence": result.confidence,
                },
            }
        )
        events.append({"event": "done", "data": {"message_id": message.id}})
        return events

    def _token_chunks(self, answer: str, chunk_size: int = 32) -> list[str]:
        if not answer:
            return []
        return [answer[index : index + chunk_size] for index in range(0, len(answer), chunk_size)]


def sse_format(event: dict) -> str:
    return f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"


def session_payload(session: ChatSession, messages: list[ChatMessage] | None = None) -> dict:
    payload = public_dict(session)
    if messages is not None:
        payload["messages"] = [public_dict(message) for message in messages]
    return payload
