from __future__ import annotations

import html
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
APP_JS = (ROOT / "app.js").read_text(encoding="utf-8")


class FrontendHandler(BaseHTTPRequestHandler):
    server_version = "CFC-HAWM-Pro-Beta-Frontend/0.1"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' https://*.clerk.accounts.dev https://challenges.cloudflare.com https://*.protect.clerk.com; "
            "connect-src 'self' https://*.clerk.accounts.dev https://*.protect.clerk.com https://cfc-hawm-pro-beta-api-production.up.railway.app; "
            "frame-src 'self' https://challenges.cloudflare.com https://*.protect.clerk.com; "
            "img-src 'self' data: https://img.clerk.com https:; "
            "worker-src 'self' blob:; "
            "style-src 'self' 'unsafe-inline'; "
            "font-src 'self' data: https:; "
            "base-uri 'self'; form-action 'self'"
        )
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path

        if path == "/healthz":
            self._send(
                HTTPStatus.OK,
                b'{"ok":true,"app":"CFC + HAWM Pro Beta Frontend","version":"0.1.0"}',
                "application/json; charset=utf-8",
            )
            return

        if path == "/":
            publishable_key = os.environ.get("CLERK_PUBLISHABLE_KEY", "").strip()
            body = INDEX.replace(
                "__CLERK_PUBLISHABLE_KEY__",
                html.escape(publishable_key, quote=True),
            ).encode("utf-8")
            self._send(HTTPStatus.OK, body, "text/html; charset=utf-8")
            return

        if path == "/app.js":
            publishable_key = os.environ.get("CLERK_PUBLISHABLE_KEY", "").strip()
            api_base = os.environ.get("PRO_BETA_API_BASE", "").strip()
            js = (
                'window.PRO_BETA_CLERK_KEY = '
                + repr(publishable_key)
                + ";\nwindow.PRO_BETA_API_BASE = "
                + repr(api_base)
                + ";\n"
                + APP_JS
            ).encode("utf-8")
            self._send(HTTPStatus.OK, js, "application/javascript; charset=utf-8")
            return

        self._send(
            HTTPStatus.NOT_FOUND,
            b'{"error":"NOT_FOUND"}',
            "application/json; charset=utf-8",
        )

    def log_message(self, format: str, *args) -> None:
        return


def make_server(host: str = "0.0.0.0", port: int = 8080) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), FrontendHandler)


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    make_server(port=port).serve_forever()


if __name__ == "__main__":
    main()
