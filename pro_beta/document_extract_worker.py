"""Isolated resource-bounded one-document worker. Does not write customer document bytes."""
from __future__ import annotations

import json
import resource
import sys

from pro_beta.document_extract import (
    DocumentError, MAX_DOCUMENT_BYTES, _decode_document_payload, extract_raw_document
)


def main() -> int:
    # Apply limits before importing a third-party document parser.
    try:
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_CPU, (6, 6))
        resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    except (ValueError, OSError):
        print(json.dumps({"error": "DOCUMENT_RESOURCE_LIMIT_UNAVAILABLE"}), flush=True)
        return 0
    try:
        raw_request = sys.stdin.buffer.read((MAX_DOCUMENT_BYTES * 4 // 3) + 8192)
        if len(raw_request) > (MAX_DOCUMENT_BYTES * 4 // 3) + 4096:
            raise DocumentError("DOCUMENT_BYTE_LIMIT")
        payload = json.loads(raw_request.decode("utf-8"))
        if not isinstance(payload, dict):
            raise DocumentError("DOCUMENT_PAYLOAD_REQUIRED")
        filename, raw = _decode_document_payload(payload)
        result = extract_raw_document(filename, raw)
        sys.stdout.write(json.dumps(result, ensure_ascii=False))
    except DocumentError as exc:
        sys.stdout.write(json.dumps({"error": str(exc)}))
    except Exception:
        # Fail closed without leaking parser stack traces or document content.
        sys.stdout.write(json.dumps({"error": "DOCUMENT_PARSE_FAILED"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
