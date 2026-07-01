from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import Principal
from app.db.models import public_dict
from app.db.repositories import repository
from app.dependencies import get_principal

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}")
def get_job(job_id: str, principal: Principal = Depends(get_principal)) -> dict:
    return public_dict(repository.get_job(principal.tenant_id, job_id))


@router.get("")
def list_jobs(
    status: str | None = None,
    principal: Principal = Depends(get_principal),
) -> list[dict]:
    return [public_dict(job) for job in repository.list_jobs(principal.tenant_id, status)]
