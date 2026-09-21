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

    def test_app_js_receives_api_base(self):
        with patch.dict(
            os.environ,
            {
                "CLERK_PUBLISHABLE_KEY": "pk_test_example",
                "PRO_BETA_API_BASE": "https://api.example.test",
            },
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("https://api.example.test", body)
        self.assertIn("PRO_BETA_API_BASE", body)
        self.assertIn("/api/onboard", body)

    def test_workspace_ui_is_present(self):
        status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn('id="create-workspace"', body)
        self.assertIn('id="create-conversation"', body)
        self.assertIn('id="send-message"', body)

    def test_hawm_ui_is_present(self):
        status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn('id="hawm-panel"', body)
        self.assertIn('id="hawm-goal"', body)
        self.assertIn('id="hawm-unresolved"', body)
        self.assertIn('id="save-hawm"', body)

    def test_app_js_contains_hawm_route(self):
        with patch.dict(
            os.environ,
            {
                "CLERK_PUBLISHABLE_KEY": "pk_test_example",
                "PRO_BETA_API_BASE": "https://api.example.test",
            },
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("/hawm", body)
        self.assertIn("USER_WORKING_STATE", body)

    def test_app_js_contains_persistence_routes(self):
        with patch.dict(
            os.environ,
            {
                "CLERK_PUBLISHABLE_KEY": "pk_test_example",
                "PRO_BETA_API_BASE": "https://api.example.test",
            },
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("/api/workspaces", body)
        self.assertIn("/conversations", body)
        self.assertIn("/messages", body)

    def test_structured_hawm_cfc_ui_is_present(self):
        status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn('id="hawm-cfc-conclusion"', body)
        self.assertIn('id="hawm-cfc-required"', body)
        self.assertIn('id="hawm-cfc-e1-polarity"', body)
        self.assertIn('id="run-hawm-cfc"', body)
        self.assertIn("Free-text HAWM fields are not interpreted", body)

    def test_app_js_contains_hawm_cfc_bridge(self):
        with patch.dict(
            os.environ,
            {
                "CLERK_PUBLISHABLE_KEY": "pk_test_example",
                "PRO_BETA_API_BASE": "https://api.example.test",
            },
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("/cfc-from-hawm", body)
        self.assertIn("cfc_structured", body)
        self.assertIn("Structured HAWM", body)

    def test_byok_gemini_ui_is_present(self):
        status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn('id="gemini-panel"', body)
        self.assertIn('id="gemini-key"', body)
        self.assertIn('id="send-gemini"', body)
        self.assertIn("MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2", body)

    def test_app_js_contains_byok_gemini_route_and_session_only_key(self):
        with patch.dict(
            os.environ,
            {
                "CLERK_PUBLISHABLE_KEY": "pk_test_example",
                "PRO_BETA_API_BASE": "https://api.example.test",
            },
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("/gemini-chat", body)
        self.assertIn("sessionStorage", body)
        self.assertIn("pro_beta_gemini_key", body)
        self.assertIn("api_key_persisted", body)
        self.assertIn("MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2", body)

    def test_byok_claude_ui_is_present(self):
        status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn('id="claude-key"', body)
        self.assertIn('id="send-claude"', body)
        self.assertIn("Claude BYOK", body)

    def test_app_js_contains_byok_claude_route_and_session_only_key(self):
        with patch.dict(
            os.environ,
            {
                "CLERK_PUBLISHABLE_KEY": "pk_test_example",
                "PRO_BETA_API_BASE": "https://api.example.test",
            },
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("/claude-chat", body)
        self.assertIn("pro_beta_claude_key", body)
        self.assertIn("api_key_persisted", body)
        self.assertIn("MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2", body)

    def test_byok_openai_ui_is_present(self):
        status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn('id="openai-key"', body)
        self.assertIn('id="send-openai"', body)
        self.assertIn("OpenAI BYOK", body)

    def test_app_js_contains_byok_openai_route_and_session_only_key(self):
        with patch.dict(
            os.environ,
            {
                "CLERK_PUBLISHABLE_KEY": "pk_test_example",
                "PRO_BETA_API_BASE": "https://api.example.test",
            },
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("/openai-chat", body)
        self.assertIn("pro_beta_openai_key", body)
        self.assertIn("api_key_persisted", body)
        self.assertIn("MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2", body)

    def test_three_model_comparison_ui_is_present(self):
        status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn('id="compare-models"', body)
        self.assertIn('id="compare-status"', body)
        self.assertIn("same prompt", body.lower())
        self.assertIn("MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2", body)

    def test_app_js_contains_three_model_comparison_route(self):
        with patch.dict(
            os.environ,
            {
                "CLERK_PUBLISHABLE_KEY": "pk_test_example",
                "PRO_BETA_API_BASE": "https://api.example.test",
            },
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("/compare-models", body)
        self.assertIn("CONNECT_ALL_THREE_PROVIDER_KEYS_FIRST", body)
        self.assertIn("gemini_api_key", body)
        self.assertIn("claude_api_key", body)
        self.assertIn("openai_api_key", body)
        self.assertIn("benchmark_type", body)

    def test_fixed_benchmark_selector_is_present(self):
        status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn('id="benchmark-case"', body)
        self.assertIn('id="load-benchmark-case"', body)
        self.assertIn('id="benchmark-expected"', body)
        self.assertIn("natural-language behavior probes", body)

    def test_app_js_loads_and_binds_fixed_benchmark_cases(self):
        with patch.dict(
            os.environ,
            {
                "CLERK_PUBLISHABLE_KEY": "pk_test_example",
                "PRO_BETA_API_BASE": "https://api.example.test",
            },
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("/api/benchmark-cases", body)
        self.assertIn("benchmark_case_id", body)
        self.assertIn("benchmark_context_boundary", body)
        self.assertIn("Automatic semantic scoring: disabled in v1", body)

    def test_message_metadata_renders_provider_and_model(self):
        with patch.dict(
            os.environ,
            {
                "CLERK_PUBLISHABLE_KEY": "pk_test_example",
                "PRO_BETA_API_BASE": "https://api.example.test",
            },
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("row.provider", body)
        self.assertIn("row.model", body)
        self.assertIn("providerModel", body)

    def test_audit_report_export_ui_is_present(self):
        status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn('id="report-panel"', body)
        self.assertIn('id="export-report"', body)
        self.assertIn("Audit report export", body)

    def test_app_js_contains_audit_report_export_route(self):
        with patch.dict(
            os.environ,
            {
                "CLERK_PUBLISHABLE_KEY": "pk_test_example",
                "PRO_BETA_API_BASE": "https://api.example.test",
            },
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("/report", body)
        self.assertIn("text/markdown", body)
        self.assertIn("free-text HAWM and ordinary model replies are not CFC-verified", body)

    def test_cfc_prepared_ui_is_present(self):
        status, body, _ = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn('id="cfc-panel"', body)
        self.assertIn('id="run-cfc"', body)
        self.assertIn("does not analyze this conversation text", body)

    def test_app_js_contains_cfc_route_and_boundary(self):
        with patch.dict(
            os.environ,
            {
                "CLERK_PUBLISHABLE_KEY": "pk_test_example",
                "PRO_BETA_API_BASE": "https://api.example.test",
            },
            clear=True,
        ):
            status, body, _ = self.get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn("/cfc", body)
        self.assertIn("Prepared synthetic fixture", body)
        self.assertIn("run.controller_anchor", body)

    def test_csp_allows_clerk_captcha_hosts(self):
        _, _, headers = self.get("/")
        csp = headers.get("Content-Security-Policy", "")
        self.assertIn("https://challenges.cloudflare.com", csp)
        self.assertIn("https://*.protect.clerk.com", csp)
        self.assertIn("worker-src 'self' blob:", csp)

    def test_security_headers_present(self):
        _, _, headers = self.get("/healthz")
        self.assertIn("Content-Security-Policy", headers)
        self.assertEqual(headers.get("Cache-Control"), "no-store")


if __name__ == "__main__":
    unittest.main(verbosity=2)
