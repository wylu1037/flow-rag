"use client";

import { useEffect, useState } from "react";
import { PlusIcon, ReloadIcon } from "@radix-ui/react-icons";
import { AppFrame } from "@/components/AppFrame";
import { EmptyState } from "@/components/EmptyState";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api";
import type { Dataset } from "@/lib/types";

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setDatasets(await api.listDatasets());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load datasets");
    } finally {
      setLoading(false);
    }
  }

  async function create() {
    if (!name.trim()) {
      setError("Dataset name is required.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await api.createDataset({ name: name.trim(), description: description.trim() });
      setName("");
      setDescription("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create dataset");
    } finally {
      setSaving(false);
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
              <Badge variant="secondary" className="font-mono uppercase">
                Datasets
              </Badge>
              <h1 className="mt-3 font-display text-[40px] leading-[1.08] tracking-[-0.04em] text-ink md:text-[48px]">
                Knowledge bases
              </h1>
            </div>
            <Button variant="outline" onClick={() => void load()}>
              <ReloadIcon className="h-4 w-4" />
              Refresh
            </Button>
          </CardHeader>
          <CardContent>
            {error ? (
              <Alert variant="destructive" className="mb-4">
                {error}
              </Alert>
            ) : null}
            {loading ? (
              <div className="grid gap-3">
                <Skeleton className="h-20" />
                <Skeleton className="h-20" />
              </div>
            ) : datasets.length === 0 ? (
              <EmptyState
                title="No datasets"
                detail="Create a knowledge base to scope document retrieval."
              />
            ) : (
              <div className="grid gap-3">
                {datasets.map((dataset) => (
                  <article
                    key={dataset.id}
                    className="rounded-lg border border-border bg-background p-5"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0">
                        <h2 className="truncate text-[18px] font-medium text-ink">
                          {dataset.name}
                        </h2>
                        <p className="mt-1 text-sm leading-6 text-muted-foreground">
                          {dataset.description || "No description"}
                        </p>
                      </div>
                      <span className="shrink-0 rounded-md border border-border px-2 py-1 font-mono text-xs text-muted-foreground">
                        {dataset.id}
                      </span>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
        <Card className="h-fit">
          <CardHeader>
            <CardTitle className="text-sm">New dataset</CardTitle>
            <CardDescription>Create a retrieval scope for related sources.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            <label className="grid gap-2 text-sm">
              <span className="font-medium text-foreground">Name</span>
              <Input value={name} onChange={(event) => setName(event.target.value)} />
            </label>
            <label className="grid gap-2 text-sm">
              <span className="font-medium text-foreground">Description</span>
              <Textarea
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                rows={4}
              />
            </label>
            <Button onClick={() => void create()} disabled={saving}>
              <PlusIcon className="h-4 w-4" />
              Create
            </Button>
          </CardContent>
        </Card>
      </div>
    </AppFrame>
  );
}
