from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


APP_NAME = "CFC + HAWM Pro Beta"
APP_VERSION = "0.1.0"


def _bearer(headers) -> str:
    raw = headers.get("Authorization", "")
    if not raw.startswith("Bearer "):
        return ""
    return raw[7:].strip()


def _allowed_origin() -> str:
    return os.environ.get("PRO_BETA_FRONTEND_ORIGIN", "").strip()


def _build_api():
    import psycopg

    from pro_beta.api import ProBetaAPI
    from pro_beta.auth_boundary import AuthBoundary
    from pro_beta.postgres_persistence import PostgresPersistence
    from pro_beta.runtime_auth import build_identity_verifier_from_environment
    from pro_beta.service import ProBetaService

    database_url = os.environ["DATABASE_URL"]
    connection = psycopg.connect(database_url)
    persistence = PostgresPersistence(connection)
    issuer = os.environ.get("CLERK_ISSUER", "").strip()
    api = ProBetaAPI(
        verifier=build_identity_verifier_from_environment(),
        auth_boundary=AuthBoundary(
            persistence,
            expected_issuer=issuer,
            expected_audience="cfc-hawm-pro-beta",
        ),
        service=ProBetaService(persistence),
    )
    return api, connection


class ProBetaHTTPHandler(BaseHTTPRequestHandler):
    server_version = "CFC-HAWM-Pro-Beta/0.1"

    def _cors_headers(self) -> None:
        origin = self.headers.get("Origin", "")
        allowed = _allowed_origin()
        if allowed and origin == allowed:
            self.send_header("Access-Control-Allow-Origin", allowed)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def _json(self, status: int, payload) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _payload(self) -> dict:
        raw_len = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_len)
        except ValueError:
            length = 0
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {}
        return value if isinstance(value, dict) else {}

    def _api_call(self, fn):
        from pro_beta.api import APIError

        api = connection = None
        try:
            api, connection = _build_api()
            result = fn(api)
            self._json(HTTPStatus.OK, result)
        except APIError as exc:
            self._json(exc.status, {"error": exc.code})
        except KeyError as exc:
            self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": f"CONFIG_MISSING:{exc.args[0]}"})
        finally:
            if connection is not None:
                connection.close()

    def do_OPTIONS(self) -> None:
        if urlsplit(self.path).path.startswith("/api/"):
            self.send_response(HTTPStatus.NO_CONTENT)
            self._cors_headers()
            self.end_headers()
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "NOT_FOUND"})

    def do_GET(self) -> None:
        path = urlsplit(self.path).path

        if path == "/healthz":
            self._json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "app": APP_NAME,
                    "version": APP_VERSION,
                    "cfc_anchor": "0.2.90rc1",
                    "ordinary_model_boundary": "MODEL_REPLY_UNCHECKED",
                },
            )
            return

        if path == "/api/workspaces":
            credential = _bearer(self.headers)
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            self._api_call(lambda api: api.list_workspaces(credential))
            return

        parts = [part for part in path.split("/") if part]
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "workspaces" and parts[3] == "conversations":
            credential = _bearer(self.headers)
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            workspace_id = parts[2]
            self._api_call(lambda api: api.list_conversations(credential, workspace_id))
            return

        if len(parts) == 4 and parts[0] == "api" and parts[1] == "conversations" and parts[3] == "messages":
            credential = _bearer(self.headers)
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            conversation_id = parts[2]
            self._api_call(lambda api: api.list_messages(credential, conversation_id))
            return

        if len(parts) == 4 and parts[0] == "api" and parts[1] == "conversations" and parts[3] == "gemini-chat":
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            payload = self._payload()
            conversation_id = parts[2]
            self._api_call(
                lambda api: api.chat_with_gemini(
                    credential,
                    conversation_id,
                    payload,
                )
            )
            return

        if len(parts) == 4 and parts[0] == "api" and parts[1] == "conversations" and parts[3] == "hawm":
            credential = _bearer(self.headers)
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            conversation_id = parts[2]
            self._api_call(lambda api: api.latest_hawm_snapshot(credential, conversation_id))
            return

        if len(parts) == 4 and parts[0] == "api" and parts[1] == "conversations" and parts[3] == "cfc":
            credential = _bearer(self.headers)
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            conversation_id = parts[2]
            self._api_call(lambda api: api.latest_cfc_run(credential, conversation_id))
            return

        self._json(HTTPStatus.NOT_FOUND, {"error": "NOT_FOUND"})

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        credential = _bearer(self.headers)

        if path == "/api/onboard":
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            self._api_call(lambda api: api.provision_account(credential))
            return

        if path == "/api/workspaces":
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            payload = self._payload()
            self._api_call(lambda api: api.create_workspace(credential, payload))
            return

        parts = [part for part in path.split("/") if part]
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "workspaces" and parts[3] == "conversations":
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            payload = self._payload()
            workspace_id = parts[2]
            self._api_call(lambda api: api.create_conversation(credential, workspace_id, payload))
            return

        if len(parts) == 4 and parts[0] == "api" and parts[1] == "conversations" and parts[3] == "messages":
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            payload = self._payload()
            conversation_id = parts[2]
            content = str(payload.get("content") or "")
            mode = str(payload.get("mode") or "STANDARD")
            self._api_call(
                lambda api: api.persist_user_message(
                    credential,
                    conversation_id,
                    content=content,
                    mode=mode,
                )
            )
            return

        if len(parts) == 4 and parts[0] == "api" and parts[1] == "conversations" and parts[3] == "hawm":
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            payload = self._payload()
            conversation_id = parts[2]
            self._api_call(
                lambda api: api.save_hawm_snapshot(
                    credential,
                    conversation_id,
                    payload,
                )
            )
            return

        if len(parts) == 4 and parts[0] == "api" and parts[1] == "conversations" and parts[3] == "cfc":
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            payload = self._payload()
            conversation_id = parts[2]
            self._api_call(
                lambda api: api.run_prepared_cfc_case(
                    credential,
                    conversation_id,
                    payload,
                )
            )
            return

        if len(parts) == 4 and parts[0] == "api" and parts[1] == "conversations" and parts[3] == "cfc-from-hawm":
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            conversation_id = parts[2]
            self._api_call(
                lambda api: api.run_structured_hawm_cfc(
                    credential,
                    conversation_id,
                )
            )
            return

        if len(parts) == 4 and parts[0] == "api" and parts[1] == "conversations" and parts[3] == "report":
            if not credential:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "AUTH_CREDENTIAL_REQUIRED"})
                return
            conversation_id = parts[2]
            self._api_call(
                lambda api: api.create_audit_report(
                    credential,
                    conversation_id,
                )
            )
            return

        self._json(HTTPStatus.NOT_FOUND, {"error": "NOT_FOUND"})

    def log_message(self, format: str, *args) -> None:
        return


def make_server(
    host: str = "0.0.0.0",
    port: int = 8080,
    handler: type[BaseHTTPRequestHandler] = ProBetaHTTPHandler,
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    from pro_beta.db_bootstrap import bootstrap_from_environment

    tables = bootstrap_from_environment()
    print("PRO_BETA_DATABASE_READY tables=" + ",".join(tables), flush=True)
    port = int(os.environ.get("PORT", "8080"))
    make_server(port=port).serve_forever()


if __name__ == "__main__":
    main()
