"use client";

import { useEffect, useState } from "react";
import { ReloadIcon } from "@radix-ui/react-icons";
import { AppFrame } from "@/components/AppFrame";
import { DocumentTable } from "@/components/DocumentTable";
import { DocumentUploader } from "@/components/DocumentUploader";
import { EmptyState } from "@/components/EmptyState";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import type { Dataset, Document } from "@/lib/types";

export default function DocumentsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [datasetList, documentList] = await Promise.all([api.listDatasets(), api.listDocuments()]);
      setDatasets(datasetList);
      setDocuments(documentList);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load documents");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <AppFrame>
      <div className="grid min-h-[calc(100dvh-9rem)] grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <Card>
          <CardHeader className="gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <Badge variant="secondary" className="font-mono uppercase">Documents</Badge>
              <h1 className="font-display mt-3 text-[40px] leading-[1.08] tracking-[-0.04em] text-ink md:text-[48px]">
                Ingestion queue
              </h1>
            </div>
            <Button variant="outline" onClick={() => void load()}>
              <ReloadIcon className="h-4 w-4" />
              Refresh
            </Button>
          </CardHeader>
          <CardContent>
          {error ? (
            <Alert variant="destructive" className="mb-4">{error}</Alert>
          ) : null}
          {loading ? (
            <div className="grid gap-2">
              <Skeleton className="h-14" />
              <Skeleton className="h-14" />
              <Skeleton className="h-14" />
            </div>
          ) : documents.length === 0 ? (
            <EmptyState title="No indexed documents" detail="Upload a text or markdown source to create retrievable chunks." />
          ) : (
            <DocumentTable documents={documents} />
          )}
          </CardContent>
        </Card>
        <aside>
          <DocumentUploader
            datasets={datasets}
            selectedDatasetId={datasets[0]?.id ?? ""}
            onUploaded={() => void load()}
          />
        </aside>
      </div>
    </AppFrame>
  );
}
