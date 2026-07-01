"use client";

import { useEffect, useMemo, useState } from "react";
import { ReloadIcon } from "@radix-ui/react-icons";
import { api, API_BASE } from "@/lib/api";
import type { ChatMessage, ChatSession, Citation, Dataset, Document, TracePayload } from "@/lib/types";
import { ChatComposer } from "./ChatComposer";
import { CitationList } from "./CitationList";
import { DatasetSelector } from "./DatasetSelector";
import { DocumentUploader } from "./DocumentUploader";
import { EmptyState } from "./EmptyState";
import { StreamingAnswer } from "./StreamingAnswer";
import { TracePanel } from "./TracePanel";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function ChatShell() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedDatasetIds, setSelectedDatasetIds] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [trace, setTrace] = useState<TracePayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [datasetList, sessionList, documentList] = await Promise.all([
        api.listDatasets(),
        api.listSessions(),
        api.listDocuments()
      ]);
      const activeSession = sessionList[0] ?? (await api.createSession("FlowRAG workspace"));
      setDatasets(datasetList);
      setDocuments(documentList);
      setSession(activeSession);
      setSelectedDatasetIds((current) => current.length ? current : datasetList.slice(0, 1).map((item) => item.id));
      const hydrated = await api.getSession(activeSession.id);
      setMessages(hydrated.messages ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load workspace");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const selectedDatasetId = selectedDatasetIds[0] ?? datasets[0]?.id ?? "";
  const indexedCount = useMemo(
    () => documents.filter((document) => document.status === "indexed").length,
    [documents]
  );

  async function sendMessage() {
    if (!session || !input.trim() || selectedDatasetIds.length === 0) {
      return;
    }
    const content = input.trim();
    setInput("");
    setSending(true);
    setError(null);
    const optimistic: ChatMessage = {
      id: `local_${Date.now()}`,
      role: "user",
      content,
      created_at: new Date().toISOString()
    };
    setMessages((current) => [...current, optimistic]);
    try {
      const response = await api.sendMessage(session.id, content, selectedDatasetIds);
      setMessages((current) => [
        ...current,
        {
          id: response.assistant_message_id,
          role: "assistant",
          content: response.answer,
          trace: response.trace,
          created_at: new Date().toISOString()
        }
      ]);
      setCitations(response.citations);
      setTrace(response.trace);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Message failed");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="grid min-h-[calc(100dvh-9rem)] grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
      <section className="flex min-h-0 flex-col gap-4">
        <header className="grid gap-6 border-b border-border pb-8 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
            <div>
              <Badge variant="secondary" className="uppercase tracking-[0.12em]">Agentic RAG</Badge>
              <h1 className="font-display mt-4 text-[44px] leading-[1.05] tracking-[-0.04em] text-ink md:text-[56px]">
                FlowRAG workspace
              </h1>
              <p className="mt-4 max-w-[68ch] text-base leading-[1.55] text-body">
                {indexedCount} indexed documents / API {API_BASE}
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <DatasetSelector
                datasets={datasets}
                selectedIds={selectedDatasetIds}
                onChange={setSelectedDatasetIds}
              />
              <Button variant="outline" onClick={() => void load()}>
                <ReloadIcon className="h-4 w-4" />
                Refresh
              </Button>
            </div>
        </header>

        {error ? (
          <Alert variant="destructive">{error}</Alert>
        ) : null}

        {loading ? (
          <Card className="min-h-[420px] bg-surface-dark text-on-dark">
            <CardContent className="grid gap-3 p-6">
              <Skeleton className="h-5 w-40 bg-on-dark-soft/20" />
              <Skeleton className="h-24 bg-on-dark-soft/15" />
              <Skeleton className="h-24 bg-on-dark-soft/15" />
            </CardContent>
          </Card>
        ) : datasets.length === 0 ? (
          <EmptyState title="No datasets" detail="Create a dataset before starting a grounded chat." />
        ) : (
          <StreamingAnswer messages={messages} loading={sending} />
        )}

        <ChatComposer
          value={input}
          disabled={sending || loading || !selectedDatasetId}
          onChange={setInput}
          onSubmit={sendMessage}
        />
      </section>

      <aside className="grid content-start gap-5">
        <DocumentUploader
          datasets={datasets}
          selectedDatasetId={selectedDatasetId}
          onUploaded={() => void load()}
        />
        <CitationList citations={citations} />
        <TracePanel trace={trace} />
      </aside>
    </div>
  );
}
