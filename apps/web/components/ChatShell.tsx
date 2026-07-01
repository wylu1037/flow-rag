"use client";

import { useEffect, useMemo, useState } from "react";
import { ReloadIcon } from "@radix-ui/react-icons";
import { api, API_BASE } from "@/lib/api";
import type {
  ChatMessage,
  ChatSession,
  Citation,
  Dataset,
  Document,
  TracePayload
} from "@/lib/types";
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
      setSelectedDatasetIds((current) =>
        current.length ? current : datasetList.slice(0, 1).map((item) => item.id)
      );
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
    <div className="grid min-h-[calc(100dvh-8rem)] grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
      <section className="grid min-h-[680px] grid-rows-[auto_minmax(0,1fr)] overflow-hidden rounded-lg border border-border bg-card xl:min-h-[calc(100dvh-8rem)]">
        <header className="grid gap-4 border-b border-border bg-card p-4 md:p-5 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="secondary" className="font-mono">
                Agentic RAG
              </Badge>
              <span className="font-mono text-xs text-muted-foreground">
                {indexedCount} indexed docs
              </span>
            </div>
            <h1 className="mt-3 text-[22px] font-semibold leading-tight text-ink md:text-[26px]">
              Chat workspace
            </h1>
            <p className="mt-1 truncate text-sm text-muted-foreground">API {API_BASE}</p>
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

        <div className="flex min-h-0 flex-col">
          {error ? (
            <div className="border-b border-border p-4">
              <Alert variant="destructive">{error}</Alert>
            </div>
          ) : null}

          {loading ? (
            <div className="grid min-h-0 flex-1 content-start gap-3 bg-surface-dark p-5 text-on-dark">
              <Skeleton className="h-5 w-40 bg-on-dark-soft/20" />
              <Skeleton className="h-24 bg-on-dark-soft/15" />
              <Skeleton className="h-24 bg-on-dark-soft/15" />
            </div>
          ) : datasets.length === 0 ? (
            <div className="min-h-0 flex-1 bg-background p-4">
              <EmptyState
                title="No datasets"
                detail="Create a dataset before starting a grounded chat."
              />
            </div>
          ) : (
            <StreamingAnswer
              messages={messages}
              loading={sending}
              className="h-auto min-h-0 flex-1 rounded-none md:h-auto"
            />
          )}

          <ChatComposer
            value={input}
            disabled={sending || loading || !selectedDatasetId}
            onChange={setInput}
            onSubmit={sendMessage}
            className="rounded-none border-x-0 border-b-0 border-t border-border bg-card"
          />
        </div>
      </section>

      <aside className="grid content-start gap-4 xl:sticky xl:top-20">
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
