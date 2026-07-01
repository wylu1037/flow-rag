from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.schemas import DatasetCreate, DatasetUpdate
from app.core.security import Principal
from app.db.models import public_dict
from app.dependencies import dataset_service, get_principal

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("")
def list_datasets(principal: Principal = Depends(get_principal)) -> list[dict]:
    return [public_dict(dataset) for dataset in dataset_service.list_datasets(principal.tenant_id)]


@router.post("")
def create_dataset(
    payload: DatasetCreate,
    principal: Principal = Depends(get_principal),
) -> dict:
    dataset = dataset_service.create_dataset(
        principal.tenant_id,
        payload.name,
        payload.description,
    )
    return public_dict(dataset)


@router.get("/{dataset_id}")
def get_dataset(dataset_id: str, principal: Principal = Depends(get_principal)) -> dict:
    return public_dict(dataset_service.get_dataset(principal.tenant_id, dataset_id))


@router.patch("/{dataset_id}")
def update_dataset(
    dataset_id: str,
    payload: DatasetUpdate,
    principal: Principal = Depends(get_principal),
) -> dict:
    dataset = dataset_service.update_dataset(
        principal.tenant_id,
        dataset_id,
        payload.name,
        payload.description,
    )
    return public_dict(dataset)


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: str, principal: Principal = Depends(get_principal)) -> dict:
    dataset_service.delete_dataset(principal.tenant_id, dataset_id)
    return {"deleted": True, "dataset_id": dataset_id}


@router.post("/{dataset_id}/reindex")
def reindex_dataset(dataset_id: str, principal: Principal = Depends(get_principal)) -> dict:
    dataset_service.get_dataset(principal.tenant_id, dataset_id)
    return {"dataset_id": dataset_id, "status": "queued"}
