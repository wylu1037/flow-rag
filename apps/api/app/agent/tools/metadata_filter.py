from __future__ import annotations

from app.agent.tools.base import ToolResult, failed, ok
from app.db.repositories import InMemoryRepository


class MetadataFilterTool:
    def __init__(self, repository: InMemoryRepository) -> None:
        self.repository = repository

    def validate_datasets(self, tenant_id: str, dataset_ids: list[str]) -> ToolResult:
        try:
            valid = [self.repository.get_dataset(tenant_id, dataset_id).id for dataset_id in dataset_ids]
        except Exception as exc:
            return failed("DATASET_ACCESS_DENIED", str(exc))
        return ok({"dataset_ids": valid}, {"tenant_id": tenant_id, "dataset_count": len(valid)})
