from __future__ import annotations

from typing import Any, TypedDict


class ToolResult(TypedDict):
    ok: bool
    data: dict[str, Any]
    error_code: str | None
    error_message: str | None
    trace: dict[str, Any]


def ok(data: dict[str, Any], trace: dict[str, Any] | None = None) -> ToolResult:
    return {
        "ok": True,
        "data": data,
        "error_code": None,
        "error_message": None,
        "trace": trace or {},
    }


def failed(error_code: str, error_message: str, trace: dict[str, Any] | None = None) -> ToolResult:
    return {
        "ok": False,
        "data": {},
        "error_code": error_code,
        "error_message": error_message,
        "trace": trace or {},
    }
