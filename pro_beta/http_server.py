from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable


APP_NAME = "CFC + HAWM Pro Beta"
APP_VERSION = "0.1.0"


class ProBetaHTTPHandler(BaseHTTPRequestHandler):
    """Minimal transport layer.

    Only health metadata is unauthenticated. Product endpoints are deliberately
    not wired until a real external identity verifier is configured.
    """

    server_version = "CFC-HAWM-Pro-Beta/0.1"

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/healthz":
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

        if self.path.startswith("/api/"):
            self._json(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {
                    "error": "AUTH_PROVIDER_NOT_CONFIGURED",
                    "message": "Pro Beta API is fail-closed until external identity verification is configured.",
                },
            )
            return

        self._json(HTTPStatus.NOT_FOUND, {"error": "NOT_FOUND"})

    def do_POST(self) -> None:
        if self.path.startswith("/api/"):
            self._json(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {
                    "error": "AUTH_PROVIDER_NOT_CONFIGURED",
                    "message": "Pro Beta API is fail-closed until external identity verification is configured.",
                },
            )
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "NOT_FOUND"})

    def log_message(self, format: str, *args) -> None:
        # Keep default access logging out of unit tests and avoid leaking headers.
        return


def make_server(
    host: str = "0.0.0.0",
    port: int = 8080,
    handler: type[BaseHTTPRequestHandler] = ProBetaHTTPHandler,
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    from pro_beta.db_bootstrap import bootstrap_from_environment

    bootstrap_from_environment()
    port = int(os.environ.get("PORT", "8080"))
    server = make_server(port=port)
    server.serve_forever()


if __name__ == "__main__":
    main()
