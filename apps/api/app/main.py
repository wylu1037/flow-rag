from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import routes_chat, routes_datasets, routes_documents, routes_health, routes_jobs
from app.core.config import settings
from app.core.errors import FlowRAGError
from app.core.logging import configure_logging
from app.core.middleware import (
    AccessLogMiddleware,
    PrincipalContextMiddleware,
    RateLimitMiddleware,
    RequestContextMiddleware,
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
)

configure_logging()
logger = logging.getLogger("flowrag.api")

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(PrincipalContextMiddleware)
app.add_middleware(AccessLogMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestContextMiddleware)

app.include_router(routes_health.router, prefix=settings.api_prefix)
app.include_router(routes_datasets.router, prefix=settings.api_prefix)
app.include_router(routes_documents.router, prefix=settings.api_prefix)
app.include_router(routes_jobs.router, prefix=settings.api_prefix)
app.include_router(routes_chat.router, prefix=settings.api_prefix)


@app.exception_handler(FlowRAGError)
async def flowrag_error_handler(request: Request, exc: FlowRAGError) -> JSONResponse:
    status_code = {
        "NOT_FOUND": 404,
        "PERMISSION_DENIED": 403,
        "VALIDATION_ERROR": 400,
        "INGESTION_ERROR": 422,
    }.get(exc.code, 400)
    return JSONResponse(
        status_code=status_code,
        content=_error_payload(request, exc.code, str(exc)),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_error_payload(
            request,
            "VALIDATION_ERROR",
            "Request validation failed.",
            exc.errors(),
        ),
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(request, "HTTP_ERROR", str(exc.detail)),
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "api.unhandled_error trace_id=%s path=%s",
        getattr(request.state, "trace_id", None),
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content=_error_payload(request, "INTERNAL_ERROR", "Internal server error."),
    )


@app.get("/")
def root() -> dict:
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
    }


def _error_payload(
    request: Request,
    code: str,
    message: str,
    details: list[dict] | None = None,
) -> dict:
    payload = {
        "code": code,
        "message": message,
        "trace_id": getattr(request.state, "trace_id", None),
    }
    if details is not None:
        payload["details"] = details
    return payload
