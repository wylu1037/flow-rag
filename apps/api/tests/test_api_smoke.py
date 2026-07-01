from __future__ import annotations

import importlib.util
import unittest


def _testclient_available() -> bool:
    if importlib.util.find_spec("fastapi") is None:
        return False
    try:
        from fastapi.testclient import TestClient  # noqa: F401
    except Exception:
        return False
    return True


@unittest.skipIf(not _testclient_available(), "FastAPI TestClient is not installed")
class APISmokeTest(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        response = client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertTrue(response.headers["x-trace-id"].startswith("trace_"))
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertEqual(response.headers["x-frame-options"], "DENY")

    def test_chat_session_endpoint(self) -> None:
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        response = client.post("/api/chat/sessions", json={"title": "API smoke"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["id"].startswith("session_"))
        self.assertTrue(response.headers["x-trace-id"].startswith("trace_"))

    def test_trace_id_header_is_preserved(self) -> None:
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        response = client.get("/api/health", headers={"X-Trace-Id": "trace_test_123"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["x-trace-id"], "trace_test_123")

    def test_request_size_limit_rejects_oversized_body(self) -> None:
        from fastapi.testclient import TestClient

        from app.core.config import settings
        from app.main import app

        previous = settings.max_request_bytes
        object.__setattr__(settings, "max_request_bytes", 16)
        try:
            client = TestClient(app)
            response = client.post("/api/chat/sessions", json={"title": "body is too large"})
        finally:
            object.__setattr__(settings, "max_request_bytes", previous)

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json()["code"], "REQUEST_TOO_LARGE")

    def test_rate_limit_rejects_excess_requests(self) -> None:
        from fastapi.testclient import TestClient

        from app.core.config import settings
        from app.core.middleware import rate_limiter
        from app.main import app

        previous_limit = settings.rate_limit_max_requests
        previous_window = settings.rate_limit_window_seconds
        object.__setattr__(settings, "rate_limit_max_requests", 1)
        object.__setattr__(settings, "rate_limit_window_seconds", 60)
        rate_limiter.clear()
        try:
            client = TestClient(app)
            headers = {"X-Tenant-Id": "tenant_rate", "X-User-Id": "user_rate"}
            first = client.post("/api/chat/sessions", json={"title": "first"}, headers=headers)
            second = client.post("/api/chat/sessions", json={"title": "second"}, headers=headers)
        finally:
            rate_limiter.clear()
            object.__setattr__(settings, "rate_limit_max_requests", previous_limit)
            object.__setattr__(settings, "rate_limit_window_seconds", previous_window)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
        self.assertEqual(second.json()["code"], "RATE_LIMITED")


if __name__ == "__main__":
    unittest.main()
