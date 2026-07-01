import type { ChatResponse, ChatSession, Dataset, Document, UploadResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json();
      message = payload.message ?? message;
    } catch {
      // Keep the HTTP status text.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export const api = {
  listDatasets: () => request<Dataset[]>("/datasets"),
  createDataset: (payload: { name: string; description?: string }) =>
    request<Dataset>("/datasets", { method: "POST", body: JSON.stringify(payload) }),
  listDocuments: () => request<Document[]>("/documents"),
  uploadDocument: (datasetId: string, file: File) => {
    const form = new FormData();
    form.append("dataset_id", datasetId);
    form.append("file", file);
    return request<UploadResponse>("/documents/upload", { method: "POST", body: form });
  },
  createSession: (title: string) =>
    request<ChatSession>("/chat/sessions", {
      method: "POST",
      body: JSON.stringify({ title })
    }),
  listSessions: () => request<ChatSession[]>("/chat/sessions"),
  getSession: (sessionId: string) => request<ChatSession>(`/chat/sessions/${sessionId}`),
  sendMessage: (sessionId: string, content: string, datasetIds: string[]) =>
    request<ChatResponse>(`/chat/sessions/${sessionId}/messages`, {
      method: "POST",
      body: JSON.stringify({
        content,
        dataset_ids: datasetIds,
        options: { stream: true, show_trace: true, top_k: 40 }
      })
    })
};

export { API_BASE };
