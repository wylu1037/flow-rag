# FlowRAG API

Base URL in development:

```text
http://localhost:8000/api
```

## Health

```http
GET /api/health
GET /api/health/ready
GET /api/health/live
```

## Datasets

```http
GET    /api/datasets
POST   /api/datasets
GET    /api/datasets/{dataset_id}
PATCH  /api/datasets/{dataset_id}
DELETE /api/datasets/{dataset_id}
POST   /api/datasets/{dataset_id}/reindex
```

## Documents

```http
POST   /api/documents/upload
GET    /api/documents
GET    /api/documents/{document_id}
DELETE /api/documents/{document_id}
POST   /api/documents/{document_id}/reindex
```

The upload endpoint accepts `multipart/form-data` with `dataset_id` and `file`.

## Chat

```http
POST /api/chat/sessions
GET  /api/chat/sessions
GET  /api/chat/sessions/{session_id}
POST /api/chat/sessions/{session_id}/messages
GET  /api/chat/sessions/{session_id}/stream?message_id=...
```

Message creation returns the assistant answer, citations, trace, and an SSE URL.
