from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import routes_chat, routes_datasets, routes_documents, routes_health, routes_jobs
from app.core.config import settings
from app.core.errors import FlowRAGError
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router, prefix=settings.api_prefix)
app.include_router(routes_datasets.router, prefix=settings.api_prefix)
app.include_router(routes_documents.router, prefix=settings.api_prefix)
app.include_router(routes_jobs.router, prefix=settings.api_prefix)
app.include_router(routes_chat.router, prefix=settings.api_prefix)


@app.exception_handler(FlowRAGError)
async def flowrag_error_handler(_: Request, exc: FlowRAGError) -> JSONResponse:
    status_code = 404 if exc.code == "NOT_FOUND" else 400
    return JSONResponse(status_code=status_code, content={"code": exc.code, "message": str(exc)})


@app.get("/")
def root() -> dict:
    return {"service": settings.app_name, "docs": "/docs", "health": f"{settings.api_prefix}/health"}
