# FlowRAG Architecture

FlowRAG is implemented as a monorepo with a FastAPI backend, a Next.js frontend, and infrastructure files for Postgres, Redis, API, worker, and web services.

Python dependencies for the API and worker are managed with `uv`. The backend project lives in `apps/api/pyproject.toml`, and Docker images run through `uv sync` plus `uv run`. In restricted local environments, use `uv --cache-dir .uv-cache ...` so uv does not need to write to the user-level cache directory.

## Current MVP

The current implementation is a local in-memory MVP:

1. Documents are uploaded through FastAPI.
2. Text is parsed, chunked, embedded with deterministic hash embeddings, and stored in memory.
3. Chat requests run through an Agentic RAG flow with intent, planning, rewrite, retrieval, rerank, evidence filtering, answer drafting, verification, repair, final answer, citations, and trace.
4. The Next.js UI provides chat, document upload, dataset management, citations, and trace inspection.

## Replacement Points

| Current component | Production replacement |
|---|---|
| In-memory repository | PostgreSQL models and repositories |
| Hash embeddings | OpenAI-compatible embedding provider or local embedding model |
| Local answerer | OpenAI-compatible LLM provider |
| Synchronous ingestion | Redis-backed worker queue |
| In-memory vector search | pgvector hybrid retrieval |

These replacement points preserve the README service boundaries.
