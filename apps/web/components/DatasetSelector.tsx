"use client";

import { ArchiveIcon } from "@radix-ui/react-icons";
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
  const labelId = "chat-knowledge-base-label";

  return (
    <div className="grid gap-2 text-sm">
      <span id={labelId} className="font-medium text-foreground">
        Knowledge base
      </span>
      <Select
        value={selectedIds[0] ?? ""}
        onValueChange={(nextValue) => onChange(nextValue ? [nextValue] : [])}
        options={datasets.map((dataset) => ({ value: dataset.id, label: dataset.name }))}
        placeholder="Select knowledge base"
        aria-labelledby={labelId}
        leadingIcon={<ArchiveIcon className="h-4 w-4" />}
        className="min-w-[220px]"
      />
    </div>
  );
}
