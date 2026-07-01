export type Dataset = {
  id: string;
  tenant_id: string;
  name: string;
  description: string;
  created_at: string;
};

export type Document = {
  id: string;
  tenant_id: string;
  dataset_id: string;
  filename: string;
  mime_type: string;
  status: string;
  content_hash: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type ChatSession = {
  id: string;
  tenant_id: string;
  user_id: string;
  title: string;
  created_at: string;
  messages?: ChatMessage[];
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  trace?: TracePayload;
  created_at: string;
};

export type Citation = {
  document_id: string;
  chunk_id: string;
  dataset_id: string;
  filename: string;
  section?: string;
  chunk_index: number;
  score: number;
  snippet: string;
};

export type TraceStep = {
  node: string;
  latency_ms: number;
  status: string;
};

export type TracePayload = {
  trace_id?: string;
  latency_ms?: number;
  intent?: string;
  retrieval_plan?: Record<string, unknown>;
  rewritten_queries?: string[];
  selected_chunks?: string[];
  verification?: {
    grounded: boolean;
    groundedness_score: number;
    unsupported_claims: string[];
    missing_citations: string[];
  };
  flow_steps?: TraceStep[];
};

export type ChatResponse = {
  message_id: string;
  assistant_message_id: string;
  stream_url: string;
  answer: string;
  citations: Citation[];
  trace: TracePayload;
};

export type UploadResponse = {
  document_id: string;
  job_id: string;
  status: string;
  chunk_count: number;
};
