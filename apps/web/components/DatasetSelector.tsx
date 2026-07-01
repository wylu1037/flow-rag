"use client";

import type { Dataset } from "@/lib/types";
import { Select } from "@/components/ui/select";

export function DatasetSelector({
  datasets,
  selectedIds,
  onChange
}: {
  datasets: Dataset[];
  selectedIds: string[];
  onChange: (ids: string[]) => void;
}) {
  return (
    <label className="grid gap-2 text-sm">
      <span className="font-medium text-foreground">Knowledge base</span>
      <Select
        value={selectedIds[0] ?? ""}
        onChange={(event) => onChange(event.target.value ? [event.target.value] : [])}
        className="min-w-[220px]"
      >
        {datasets.map((dataset) => (
          <option key={dataset.id} value={dataset.id}>
            {dataset.name}
          </option>
        ))}
      </Select>
    </label>
  );
}
