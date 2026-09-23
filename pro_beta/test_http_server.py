from __future__ import annotations

import json
import threading
import unittest
import urllib.error
import urllib.request

from pro_beta.http_server import make_server


class HTTPServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(host="127.0.0.1", port=0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True,
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, path: str, method: str = "GET"):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def test_healthz_is_available(self):
        status, payload = self.request("/healthz")
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["cfc_anchor"], "0.2.90rc1")
        self.assertEqual(
            payload["ordinary_model_boundary"],
            "MODEL_REPLY_UNCHECKED",
        )

    def test_api_get_requires_bearer(self):
        status, payload = self.request("/api/workspaces")
        self.assertEqual(status, 401)
        self.assertEqual(payload["error"], "AUTH_CREDENTIAL_REQUIRED")

    def test_api_post_requires_bearer(self):
        status, payload = self.request("/api/workspaces", method="POST")
        self.assertEqual(status, 401)
        self.assertEqual(payload["error"], "AUTH_CREDENTIAL_REQUIRED")

    def test_onboard_requires_bearer(self):
        status, payload = self.request("/api/onboard", method="POST")
        self.assertEqual(status, 401)
        self.assertEqual(payload["error"], "AUTH_CREDENTIAL_REQUIRED")

    def test_beta_cfc_check_route_requires_bearer(self):
        status, payload = self.request(
            "/api/workspaces/ws_test/beta-cfc-check",
            method="POST",
        )
        self.assertEqual(status, 401)
        self.assertEqual(payload["error"], "AUTH_CREDENTIAL_REQUIRED")

    def test_beta_measurement_routes_require_bearer(self):
        status, payload = self.request(
            "/api/workspaces/ws_test/beta-measurements",
            method="POST",
        )
        self.assertEqual(status, 401)
        self.assertEqual(payload["error"], "AUTH_CREDENTIAL_REQUIRED")

        status, payload = self.request(
            "/api/workspaces/ws_test/beta-measurements",
            method="GET",
        )
        self.assertEqual(status, 401)
        self.assertEqual(payload["error"], "AUTH_CREDENTIAL_REQUIRED")

    def test_benchmark_label_route_is_post_only(self):
        status, payload = self.request(
            "/api/benchmark-runs/bench_test/label",
            method="POST",
        )
        self.assertEqual(status, 401)
        self.assertEqual(payload["error"], "AUTH_CREDENTIAL_REQUIRED")

        status, payload = self.request(
            "/api/benchmark-runs/bench_test/label",
            method="GET",
        )
        self.assertEqual(status, 404)
        self.assertEqual(payload["error"], "NOT_FOUND")

    def test_unknown_route_is_404(self):
        status, payload = self.request("/unknown")
        self.assertEqual(status, 404)
        self.assertEqual(payload["error"], "NOT_FOUND")


if __name__ == "__main__":
    unittest.main(verbosity=2)
