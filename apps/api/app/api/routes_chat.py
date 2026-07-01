from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.api.schemas import ChatMessageCreate, ChatSessionCreate
from app.core.config import settings
from app.core.security import Principal
from app.db.models import public_dict
from app.dependencies import chat_service, get_principal
from app.services.chat_service import session_payload, sse_format

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions")
def create_session(
    payload: ChatSessionCreate,
    principal: Principal = Depends(get_principal),
) -> dict:
    session = chat_service.create_session(principal.tenant_id, principal.user_id, payload.title)
    return public_dict(session)


@router.get("/sessions")
def list_sessions(principal: Principal = Depends(get_principal)) -> list[dict]:
    return [
        public_dict(session)
        for session in chat_service.list_sessions(principal.tenant_id, principal.user_id)
    ]


@router.get("/sessions/{session_id}")
def get_session(session_id: str, principal: Principal = Depends(get_principal)) -> dict:
    session = chat_service.get_session(principal.tenant_id, session_id)
    messages = chat_service.list_messages(principal.tenant_id, session_id)
    return session_payload(session, messages)


@router.post("/sessions/{session_id}/messages")
def create_message(
    session_id: str,
    payload: ChatMessageCreate,
    principal: Principal = Depends(get_principal),
) -> dict:
    dataset_ids = payload.dataset_ids or [settings.default_dataset_id]
    turn = chat_service.create_message(
        tenant_id=principal.tenant_id,
        user_id=principal.user_id,
        session_id=session_id,
        content=payload.content,
        dataset_ids=dataset_ids,
        options=payload.options,
    )
    return {
        "message_id": turn.user_message.id,
        "assistant_message_id": turn.assistant_message.id,
        "stream_url": turn.stream_url,
        "answer": turn.rag_result.answer,
        "citations": turn.rag_result.citations,
        "trace": turn.rag_result.trace,
    }


@router.get("/sessions/{session_id}/stream")
async def stream_message(
    session_id: str,
    message_id: str = Query(...),
    principal: Principal = Depends(get_principal),
) -> StreamingResponse:
    chat_service.get_session(principal.tenant_id, session_id)
    events = chat_service.stream_events(message_id)

    async def iterator():
        for event in events:
            yield sse_format(event)
            await asyncio.sleep(0.01)

    return StreamingResponse(iterator(), media_type="text/event-stream")
