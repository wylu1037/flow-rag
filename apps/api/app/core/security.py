from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    user_id: str
    role: str = "owner"


def principal_from_headers(
    tenant_id: str | None = None,
    user_id: str | None = None,
    role: str | None = None,
) -> Principal:
    return Principal(
        tenant_id=tenant_id or settings.default_tenant_id,
        user_id=user_id or settings.default_user_id,
        role=role or "owner",
    )
