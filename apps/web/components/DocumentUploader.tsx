"use client";

import { useEffect, useRef, useState } from "react";
import { ArchiveIcon, ChevronDownIcon, FileTextIcon, ReloadIcon, UploadIcon } from "@radix-ui/react-icons";
import { api } from "@/lib/api";
import type { Dataset, UploadResponse } from "@/lib/types";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";

export function DocumentUploader({
  datasets,
  selectedDatasetId,
  onUploaded
}: {
  datasets: Dataset[];
  selectedDatasetId: string;
  onUploaded: (result: UploadResponse) => void;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [datasetId, setDatasetId] = useState(selectedDatasetId);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedDatasetId) {
      setDatasetId(selectedDatasetId);
    }
  }, [selectedDatasetId]);

  async function submit() {
    const file = inputRef.current?.files?.[0];
    if (!file) {
      setError("Choose a text or markdown file.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const result = await api.uploadDocument(datasetId || selectedDatasetId, file);
      onUploaded(result);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
      setSelectedFileName("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card className="min-w-0">
      <CardHeader className="p-5">
        <CardTitle className="text-[16px]">Upload</CardTitle>
        <CardDescription>Text is indexed immediately in the local MVP.</CardDescription>
      </CardHeader>
      <CardContent className="grid min-w-0 gap-3 p-5 pt-0">
        <label className="grid min-w-0 gap-2 text-sm">
          <span className="font-medium text-foreground">Dataset</span>
          <span className="relative block w-full min-w-0 max-w-full">
            <ArchiveIcon className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Select
              value={datasetId || selectedDatasetId}
              onChange={(event) => setDatasetId(event.target.value)}
              className="max-w-full appearance-none truncate pl-10 pr-10"
            >
              {datasets.map((dataset) => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.name}
                </option>
              ))}
            </Select>
            <ChevronDownIcon className="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          </span>
        </label>
        <label className="grid min-w-0 gap-2 text-sm">
          <span className="font-medium text-foreground">File</span>
          <span className="group relative flex min-h-12 w-full min-w-0 max-w-full cursor-pointer items-center gap-3 rounded-md border border-dashed border-input bg-background px-3.5 py-3 text-sm outline-none transition-[background-color,border-color,box-shadow,transform] hover:border-primary/60 hover:bg-secondary focus-within:border-primary focus-within:ring-4 focus-within:ring-ring/15 active:translate-y-[1px]">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-border bg-surface-soft text-muted-foreground transition-colors group-hover:text-foreground">
              <FileTextIcon className="h-4 w-4" />
            </span>
            <span className="min-w-0 flex-1">
              <span
                className="block truncate font-medium text-foreground"
                title={selectedFileName || "Select a text or markdown source"}
              >
                {selectedFileName || "Select a text or markdown source"}
              </span>
              <span className="mt-0.5 block text-xs text-muted-foreground">TXT, MD, or Markdown</span>
            </span>
            <span className="hidden shrink-0 rounded-full border border-border bg-card px-2.5 py-1 text-xs font-medium text-muted-foreground min-[380px]:inline-flex">
              Browse
            </span>
            <input
              ref={inputRef}
              type="file"
              accept=".txt,.md,.markdown,text/plain,text/markdown"
              className="sr-only"
              onChange={(event) => setSelectedFileName(event.target.files?.[0]?.name ?? "")}
            />
          </span>
        </label>
        {error ? <Alert variant="destructive">{error}</Alert> : null}
        <Button
          onClick={submit}
          disabled={busy || datasets.length === 0}
          className="w-full max-w-full"
        >
          {busy ? <ReloadIcon className="h-4 w-4 animate-spin" /> : <UploadIcon className="h-4 w-4" />}
          Upload
        </Button>
      </CardContent>
    </Card>
  );
}
