from __future__ import annotations


class FlowRAGError(Exception):
    """Base domain error for predictable API failures."""

    code = "FLOWRAG_ERROR"


class NotFoundError(FlowRAGError):
    code = "NOT_FOUND"


class PermissionDeniedError(FlowRAGError):
    code = "PERMISSION_DENIED"


class ValidationError(FlowRAGError):
    code = "VALIDATION_ERROR"


class IngestionError(FlowRAGError):
    code = "INGESTION_ERROR"
