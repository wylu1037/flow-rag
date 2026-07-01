from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DatasetCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str = ""


class DatasetUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ChatSessionCreate(BaseModel):
    title: str = "New chat"


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1)
    dataset_ids: list[str] = Field(default_factory=list)
    options: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    code: str
    message: str
