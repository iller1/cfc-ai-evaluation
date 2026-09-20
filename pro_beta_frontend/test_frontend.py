from __future__ import annotations

import json
import os
import threading
import unittest
import urllib.request
from unittest.mock import patch

from pro_beta_frontend.server import make_server


class FrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(host="127.0.0.1", port=0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get(self, path="/"):
        with urllib.request.urlopen(
            f"http://127.0.0.1:{self.port}{path}", timeout=2
        ) as response:
            return response.status, response.read().decode(), dict(response.headers)

    def test_healthz(self):
        status, body, _ = self.get("/healthz")
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["ok"])

    def test_homepage_allows_query_string(self):
        with patch.dict(os.environ, {}, clear=True):
            status, body, _ = self.get("/?utm_source=chatgpt.com")
        self.assertEqual(status, 200)
        self.assertIn("CFC + HAWM Pro Beta", body)

    def test_page_preserves_cfc_boundary(self):
        with patch.dict(os.environ, {}, clear=True):
            status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn("MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2", body)
        self.assertIn('src="/app.js"', body)

    def test_publishable_key_is_injected_when_configured(self):
        with patch.dict(
            os.environ,
            {"CLERK_PUBLISHABLE_KEY": "pk_test_example"},
            clear=True,
        ):
            status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn("pk_test_example", body)

    def test_app_js_receives_publishable_key(self):
        with patch.dict(
            os.environ,
            {"CLERK_PUBLISHABLE_KEY": "pk_test_example"},
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("pk_test_example", body)
        self.assertIn("PRO_BETA_CLERK_KEY", body)

    def test_security_headers_present(self):
        _, _, headers = self.get("/healthz")
        self.assertIn("Content-Security-Policy", headers)
        self.assertEqual(headers.get("Cache-Control"), "no-store")


if __name__ == "__main__":
    unittest.main(verbosity=2)
