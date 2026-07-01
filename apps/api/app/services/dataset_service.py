from __future__ import annotations

from app.db.models import Dataset
from app.db.repositories import InMemoryRepository


class DatasetService:
    def __init__(self, repository: InMemoryRepository) -> None:
        self.repository = repository

    def list_datasets(self, tenant_id: str) -> list[Dataset]:
        return self.repository.list_datasets(tenant_id)

    def create_dataset(self, tenant_id: str, name: str, description: str = "") -> Dataset:
        return self.repository.create_dataset(tenant_id, name, description)

    def get_dataset(self, tenant_id: str, dataset_id: str) -> Dataset:
        return self.repository.get_dataset(tenant_id, dataset_id)

    def update_dataset(
        self,
        tenant_id: str,
        dataset_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> Dataset:
        return self.repository.update_dataset(tenant_id, dataset_id, name, description)

    def delete_dataset(self, tenant_id: str, dataset_id: str) -> None:
        self.repository.delete_dataset(tenant_id, dataset_id)
