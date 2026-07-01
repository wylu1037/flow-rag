from __future__ import annotations

import importlib.util
import unittest


@unittest.skipIf(importlib.util.find_spec("fastapi") is None, "FastAPI is not installed")
class APISmokeTest(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        response = client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_chat_session_endpoint(self) -> None:
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        response = client.post("/api/chat/sessions", json={"title": "API smoke"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["id"].startswith("session_"))


if __name__ == "__main__":
    unittest.main()
