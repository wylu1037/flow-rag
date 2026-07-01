from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "flowrag-api"}


@router.get("/health/ready")
def ready() -> dict:
    return {"status": "ready"}


@router.get("/health/live")
def live() -> dict:
    return {"status": "live"}
