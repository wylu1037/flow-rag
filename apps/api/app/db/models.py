from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class DocumentStatus(StrEnum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXED = "indexed"
    FAILED = "failed"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class Tenant:
    id: str
    name: str
    plan: str = "developer"
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class User:
    id: str
    tenant_id: str
    email: str
    role: str = "owner"
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class Dataset:
    id: str
    tenant_id: str
    name: str
    description: str = ""
    settings: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class Document:
    id: str
    tenant_id: str
    dataset_id: str
    filename: str
    mime_type: str
    storage_uri: str
    status: DocumentStatus
    content_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class DocumentChunk:
    id: str
    tenant_id: str
    dataset_id: str
    document_id: str
    chunk_index: int
    content: str
    metadata: dict[str, Any]
    embedding: list[float]
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class ChatSession:
    id: str
    tenant_id: str
    user_id: str
    title: str
    settings: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class ChatMessage:
    id: str
    tenant_id: str
    session_id: str
    role: MessageRole
    content: str
    trace: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class MessageCitation:
    id: str
    tenant_id: str
    message_id: str
    chunk_id: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionJob:
    id: str
    tenant_id: str
    document_id: str
    status: JobStatus
    stage: str = "queued"
    progress: float = 0.0
    error: str | None = None
    stats: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


def public_dict(value: Any) -> dict[str, Any]:
    data = asdict(value)
    for key, item in list(data.items()):
        if isinstance(item, datetime):
            data[key] = item.isoformat()
        elif isinstance(item, StrEnum):
            data[key] = str(item)
    return data
