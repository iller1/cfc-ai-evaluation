from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

from demonstrator import server as demo_server

demo_server.ensure_runtime()
sys.path.insert(0, str(demo_server.RUNTIME))

from cfc_anchor import Controller


TARGETS = (
    "__init__",
    "draft_snapshot",
    "install_verified_snapshot",
    "evaluate_snapshot",
    "evaluate",
    "decision_context_commitment",
    "inspect_snapshot",
    "inspect_retrieval_authority",
)


def _signature(obj):
    try:
        return str(inspect.signature(obj))
    except Exception as exc:
        return f"<signature-error:{type(exc).__name__}:{exc}>"


def _doc(obj):
    try:
        return inspect.getdoc(obj)
    except Exception:
        return None


def _relevant_source_lines(obj):
    try:
        src = inspect.getsource(obj)
    except Exception as exc:
        return [f"<source-error:{type(exc).__name__}:{exc}>"]
    out = []
    for no, line in enumerate(src.splitlines(), 1):
        if any(token in line.lower() for token in (
            "scope",
            "snapshot",
            "retrieval",
            "audit",
            "context",
        )):
            out.append(f"{no}: {line}")
    return out[:120]


def main():
    methods = {}
    for name in TARGETS:
        obj = getattr(Controller, name)
        methods[name] = {
            "signature": _signature(obj),
            "doc": _doc(obj),
            "relevant_source_lines": _relevant_source_lines(obj),
        }

    all_public_methods = []
    relevant_public_methods = []
    for name in dir(Controller):
        if name.startswith("_"):
            continue
        obj = getattr(Controller, name)
        if callable(obj):
            all_public_methods.append({
                "name": name,
                "signature": _signature(obj),
                "doc": _doc(obj),
            })
        if any(token in name.lower() for token in (
            "scope",
            "snapshot",
            "retrieval",
            "audit",
            "context",
            "evaluate",
        )):
            relevant_public_methods.append({
                "name": name,
                "signature": _signature(obj) if callable(obj) else None,
                "doc": _doc(obj) if callable(obj) else None,
            })

    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "FROZEN_PUBLIC_API_MULTI_SCOPE_CONTRACT_INSPECTION",
        "controller_signature": _signature(Controller),
        "targets": methods,
        "relevant_public_methods": relevant_public_methods,
        "all_public_methods": all_public_methods,
    }
    Path("frozen_public_api_multi_scope_contract.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
