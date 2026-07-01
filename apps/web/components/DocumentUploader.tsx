"use client";

import { useEffect, useRef, useState } from "react";
import { ReloadIcon, UploadIcon } from "@radix-ui/react-icons";
import { api } from "@/lib/api";
import type { Dataset, UploadResponse } from "@/lib/types";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
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
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-[18px]">Upload</CardTitle>
        <CardDescription>Text is indexed immediately in the local MVP.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4">
        <label className="grid gap-2 text-sm">
          <span className="font-medium text-foreground">Dataset</span>
          <Select
            value={datasetId || selectedDatasetId}
            onChange={(event) => setDatasetId(event.target.value)}
          >
            {datasets.map((dataset) => (
              <option key={dataset.id} value={dataset.id}>
                {dataset.name}
              </option>
            ))}
          </Select>
        </label>
        <label className="grid gap-2 text-sm">
          <span className="font-medium text-foreground">File</span>
          <Input
            ref={inputRef}
            type="file"
            accept=".txt,.md,.markdown,text/plain,text/markdown"
            className="h-auto py-2"
          />
        </label>
        {error ? <Alert variant="destructive">{error}</Alert> : null}
        <Button
          onClick={submit}
          disabled={busy || datasets.length === 0}
          className="w-full"
        >
          {busy ? <ReloadIcon className="h-4 w-4 animate-spin" /> : <UploadIcon className="h-4 w-4" />}
          Upload
        </Button>
      </CardContent>
    </Card>
  );
}
