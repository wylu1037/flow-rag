from __future__ import annotations

import json
import logging
import time
from contextvars import ContextVar
from dataclasses import dataclass
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.config import settings
from app.core.security import principal_from_headers

logger = logging.getLogger("flowrag.api")

trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)


def current_trace_id() -> str | None:
    return trace_id_var.get()


def new_trace_id() -> str:
    return f"trace_{uuid4().hex}"


def _safe_header_value(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = "".join(char for char in value.strip() if char.isalnum() or char in "-_:.")
    return cleaned[:128] or None


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Create request-scoped trace context and expose it via response headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = (
            _safe_header_value(request.headers.get("x-trace-id"))
            or _safe_header_value(request.headers.get("x-request-id"))
            or new_trace_id()
        )
        token = trace_id_var.set(trace_id)
        request.state.trace_id = trace_id
        try:
            response = await call_next(request)
        finally:
            trace_id_var.reset(token)
        response.headers["X-Trace-Id"] = trace_id
        response.headers["X-Request-Id"] = trace_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add conservative browser-facing security headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )
        return response


class PrincipalContextMiddleware(BaseHTTPMiddleware):
    """Resolve tenant/user context once and attach it to request.state."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        principal = principal_from_headers(
            tenant_id=request.headers.get("x-tenant-id"),
            user_id=request.headers.get("x-user-id"),
            role=request.headers.get("x-role"),
        )
        request.state.principal = principal
        return await call_next(request)


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Emit structured access logs without request or response bodies."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            payload = {
                "trace_id": getattr(request.state, "trace_id", None),
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "tenant_id": request.headers.get("x-tenant-id"),
                "user_id": request.headers.get("x-user-id"),
                "client": request.client.host if request.client else None,
            }
            logger.info("api.access %s", json.dumps(payload, separators=(",", ":")))


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject oversized requests before FastAPI reads/parses the body."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                request_size = int(content_length)
            except ValueError:
                request_size = 0
            if settings.max_request_bytes > 0 and request_size > settings.max_request_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "code": "REQUEST_TOO_LARGE",
                        "message": "Request body exceeds the configured size limit.",
                        "trace_id": getattr(request.state, "trace_id", None),
                    },
                )
        return await call_next(request)


@dataclass
class _RateBucket:
    window_started_at: float
    count: int


class InMemoryRateLimiter:
    """MVP fixed-window limiter; replace with Redis for multi-process production."""

    def __init__(self) -> None:
        self._buckets: dict[str, _RateBucket] = {}

    def check(
        self,
        key: str,
        now: float,
        window_seconds: int,
        max_requests: int,
    ) -> tuple[bool, int, int]:
        bucket = self._buckets.get(key)
        if bucket is None or now - bucket.window_started_at >= window_seconds:
            bucket = _RateBucket(window_started_at=now, count=0)
            self._buckets[key] = bucket
        bucket.count += 1
        remaining = max(max_requests - bucket.count, 0)
        reset_in = max(1, int(window_seconds - (now - bucket.window_started_at)))
        return bucket.count <= max_requests, remaining, reset_in

    def clear(self) -> None:
        self._buckets.clear()


rate_limiter = InMemoryRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply coarse per-principal request limits for the local MVP."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if (
            request.method == "OPTIONS"
            or request.url.path.endswith("/health")
            or settings.rate_limit_max_requests <= 0
            or settings.rate_limit_window_seconds <= 0
        ):
            return await call_next(request)

        key = self._rate_key(request)
        allowed, remaining, reset_in = rate_limiter.check(
            key,
            time.monotonic(),
            settings.rate_limit_window_seconds,
            settings.rate_limit_max_requests,
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "code": "RATE_LIMITED",
                    "message": "Too many requests. Please retry after the rate limit resets.",
                    "trace_id": getattr(request.state, "trace_id", None),
                },
                headers={
                    "Retry-After": str(reset_in),
                    "X-RateLimit-Limit": str(settings.rate_limit_max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_in),
                },
            )

        response = await call_next(request)
        response.headers.setdefault("X-RateLimit-Limit", str(settings.rate_limit_max_requests))
        response.headers.setdefault("X-RateLimit-Remaining", str(remaining))
        response.headers.setdefault("X-RateLimit-Reset", str(reset_in))
        return response

    @staticmethod
    def _rate_key(request: Request) -> str:
        tenant_id = request.headers.get("x-tenant-id")
        user_id = request.headers.get("x-user-id")
        if tenant_id or user_id:
            return f"principal:{tenant_id or '-'}:{user_id or '-'}"
        client_host = request.client.host if request.client else "unknown"
        return f"client:{client_host}"
