from __future__ import annotations

import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, build_opener

from web_demo import app


class WebAlphaRegressionTests(unittest.TestCase):
    """Regression coverage for the public Web Alpha boundary and session behavior."""

    @classmethod
    def setUpClass(cls):
        cls._orig_gemini_call = app.gemini_call
        cls._orig_run_case = app.cfc_demo.run_case
        cls.server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        app.gemini_call = cls._orig_gemini_call
        app.cfc_demo.run_case = cls._orig_run_case
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        with app.LOCK:
            app.SESSIONS.clear()
        # The production cookie is intentionally Secure. urllib's CookieJar
        # correctly refuses to resend a Secure cookie over this test harness's
        # plain HTTP loopback connection, so the harness preserves only the
        # returned SID pair and replays it explicitly on later loopback calls.
        # Production cookie attributes are asserted separately below.
        self.sid_cookie = None
        self.opener = build_opener()

    def _capture_sid(self, headers):
        raw = headers.get("Set-Cookie")
        if raw:
            self.sid_cookie = raw.split(";", 1)[0]

    def _request(self, path, method="GET", body=None):
        data = None
        headers = {}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.sid_cookie:
            headers["Cookie"] = self.sid_cookie
        req = Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with self.opener.open(req, timeout=5) as response:
                self._capture_sid(response.headers)
                raw = response.read().decode("utf-8")
                return response.status, response.headers, raw
        except HTTPError as exc:
            self._capture_sid(exc.headers)
            raw = exc.read().decode("utf-8")
            return exc.code, exc.headers, raw

    def _json(self, path, method="GET", body=None):
        status, headers, raw = self._request(path, method, body)
        return status, headers, json.loads(raw)

    def test_homepage_exposes_boundary_and_current_version(self):
        status, headers, raw = self._request("/")
        self.assertEqual(status, 200)
        self.assertIn("Public Web Alpha · web 1.0.4", raw)
        self.assertIn("MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2", raw)
        self.assertIn("Disconnect", raw)
        self.assertIn("Get Gemini API key", raw)
        self.assertEqual(headers.get("Cache-Control"), "no-store")

        cookie = headers.get("Set-Cookie") or ""
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=Lax", cookie)
        self.assertIn("Secure", cookie)

    def test_status_starts_disconnected_and_preserves_cfc_boundary(self):
        status, _, payload = self._json("/api/status")
        self.assertEqual(status, 200)
        self.assertFalse(payload["connected"])
        self.assertEqual(payload["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(payload["cfc_status"], "NOT_CONNECTED_C2")
        self.assertEqual(payload["frozen_cfc"]["anchor"], "0.2.90rc1")

    def test_connection_survives_new_chat(self):
        status, _, payload = self._json(
            "/api/connect",
            "POST",
            {"provider": "gemini", "model": "gemini-test", "api_key": "test-key"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["provider"], "gemini")

        status, _, payload = self._json("/api/new", "POST", {})
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])

        status, _, payload = self._json("/api/status")
        self.assertEqual(status, 200)
        self.assertTrue(payload["connected"])
        self.assertEqual(payload["provider"], "gemini")
        self.assertEqual(payload["model"], "gemini-test")
        self.assertEqual(payload["history_messages"], 0)
        self.assertEqual(payload["hawm"]["LAST_VERIFIED_STATE"], "new_conversation")

    def test_disconnect_clears_server_connection(self):
        self._json(
            "/api/connect",
            "POST",
            {"provider": "gemini", "model": "gemini-test", "api_key": "test-key"},
        )
        status, _, payload = self._json("/api/disconnect", "POST", {})
        self.assertEqual(status, 200)
        self.assertFalse(payload["connected"])

        status, _, payload = self._json("/api/status")
        self.assertEqual(status, 200)
        self.assertFalse(payload["connected"])
        self.assertIsNone(payload["provider"])

    def test_chat_without_key_is_explicit_401_not_runtime_dump(self):
        status, _, payload = self._json(
            "/api/chat", "POST", {"text": "hello", "mode": "STANDARD"}
        )
        self.assertEqual(status, 401)
        self.assertEqual(payload["code"], "API_KEY_REQUIRED")
        self.assertNotIn("RuntimeError", payload["error"])

    def test_ordinary_chat_remains_unchecked_and_updates_hawm(self):
        self._json(
            "/api/connect",
            "POST",
            {"provider": "gemini", "model": "gemini-test", "api_key": "test-key"},
        )

        seen = {}

        def fake_gemini_call(session, text):
            seen["mode"] = session.mode
            seen["text"] = text
            return "mock answer", "STOP"

        app.gemini_call = fake_gemini_call
        status, _, payload = self._json(
            "/api/chat", "POST", {"text": "test question", "mode": "MINIMUM"}
        )

        self.assertEqual(status, 200)
        self.assertEqual(payload["text"], "mock answer")
        self.assertEqual(payload["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(payload["cfc_status"], "NOT_CONNECTED_C2")
        self.assertEqual(payload["mode"], "MINIMUM")
        self.assertFalse(payload["truncated"])
        self.assertEqual(seen, {"mode": "MINIMUM", "text": "test question"})

        _, _, state = self._json("/api/status")
        self.assertEqual(state["history_messages"], 2)
        self.assertEqual(state["hawm"]["CURRENT_TASK"], "test question")
        self.assertEqual(
            state["hawm"]["LAST_VERIFIED_STATE"], "ordinary_model_reply_unchecked"
        )

    def test_max_tokens_is_exposed_as_truncation(self):
        self._json(
            "/api/connect",
            "POST",
            {"provider": "gemini", "model": "gemini-test", "api_key": "test-key"},
        )

        app.gemini_call = lambda session, text: ("partial answer", "MAX_TOKENS")
        status, _, payload = self._json(
            "/api/chat", "POST", {"text": "long question", "mode": "STANDARD"}
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["finish_reason"], "MAX_TOKENS")
        self.assertTrue(payload["truncated"])

    def test_prepared_cfc_path_is_separate_from_ordinary_chat(self):
        app.cfc_demo.run_case = lambda case_id: {
            "presentation": {
                "claim_state": "UNRESOLVED",
                "decision": "NO_CLOSURE",
                "reason": "insufficient evidence",
            },
            "case_id": case_id,
        }
        status, _, payload = self._json("/api/cfc", "POST", {})
        self.assertEqual(status, 200)
        self.assertEqual(payload["presentation"]["claim_state"], "UNRESOLVED")
        self.assertEqual(payload["presentation"]["decision"], "NO_CLOSURE")

        _, _, state = self._json("/api/status")
        self.assertEqual(state["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(state["cfc_status"], "NOT_CONNECTED_C2")


if __name__ == "__main__":
    unittest.main(verbosity=2)
