from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "FlowRAG"
    app_env: str = os.getenv("APP_ENV", "development")
    api_prefix: str = "/api"
    default_tenant_id: str = os.getenv("FLOWRAG_DEFAULT_TENANT_ID", "tenant_demo")
    default_user_id: str = os.getenv("FLOWRAG_DEFAULT_USER_ID", "user_demo")
    default_dataset_id: str = os.getenv("FLOWRAG_DEFAULT_DATASET_ID", "dataset_demo")
    max_upload_bytes: int = int(os.getenv("FLOWRAG_MAX_UPLOAD_BYTES", "5242880"))
    max_retrieval_rounds: int = int(os.getenv("FLOWRAG_MAX_RETRIEVAL_ROUNDS", "3"))
    max_rewritten_queries: int = int(os.getenv("FLOWRAG_MAX_REWRITTEN_QUERIES", "3"))
    max_candidate_chunks: int = int(os.getenv("FLOWRAG_MAX_CANDIDATE_CHUNKS", "80"))
    max_evidence_chunks: int = int(os.getenv("FLOWRAG_MAX_EVIDENCE_CHUNKS", "10"))


settings = Settings()
