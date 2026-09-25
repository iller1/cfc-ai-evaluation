from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

from demonstrator import server as demo_server

demo_server.ensure_runtime()
sys.path.insert(0, str(demo_server.RUNTIME))

from cfc_anchor import Controller
import cfc_anchor._engine as frozen_engine


TOKENS = (
    "decision_support",
    "support_closure",
    "claim_support",
    "support_relation",
    "selected_support",
    "support_universe",
    "dependency_relation",
    "generic_dependency_accounting",
    "decision_dependency_accounting",
    "accounting",
)


def _signature(obj):
    try:
        return str(inspect.signature(obj))
    except Exception as exc:
        return f"<signature-error:{type(exc).__name__}:{exc}>"


def _source(obj, limit=420):
    try:
        lines = inspect.getsource(obj).splitlines()
    except Exception as exc:
        return [f"<source-error:{type(exc).__name__}:{exc}>"]
    return [f"{i}: {line}" for i, line in enumerate(lines[:limit], 1)]


def _relevant_controller_lines():
    out = {}
    for name in ("evaluate", "evaluate_snapshot"):
        obj = getattr(Controller, name)
        lines = _source(obj, 520)
        out[name] = [
            line for line in lines
            if any(tok in line.lower() for tok in (
                "decision_support",
                "support",
                "relation",
                "dependency",
                "stale",
                "current",
                "closure",
                "gate",
            ))
        ]
    return out


def main():
    objects = []
    for name in dir(frozen_engine):
        lname = name.lower()
        if not any(tok in lname for tok in TOKENS):
            continue
        obj = getattr(frozen_engine, name)
        objects.append({
            "name": name,
            "callable": callable(obj),
            "signature": _signature(obj) if callable(obj) else None,
            "source": _source(obj) if callable(obj) else None,
            "repr": None if callable(obj) else repr(obj)[:2000],
        })

    # Also capture functions whose *source* mentions the gate even if their
    # symbol name does not.
    source_mentions = []
    for name in dir(frozen_engine):
        if name.startswith("__"):
            continue
        obj = getattr(frozen_engine, name)
        if not callable(obj):
            continue
        try:
            src = inspect.getsource(obj)
        except Exception:
            continue
        low = src.lower()
        if (
            "decision_support_closure_valid" in low
            or "decision support closure" in low
            or "decision_support_closure" in low
        ):
            source_mentions.append({
                "name": name,
                "signature": _signature(obj),
                "source": _source(obj),
            })

    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "DECISION_SUPPORT_CLOSURE_PATH_INSPECTION",
        "engine_objects": objects,
        "source_mentions": source_mentions,
        "controller_relevant_lines": _relevant_controller_lines(),
        "controller_evaluate_source": _source(Controller.evaluate, 360),
        "controller_evaluate_snapshot_source": _source(Controller.evaluate_snapshot, 220),
        "controller_decision_dependency_accounting_integration_source": _source(Controller._decision_dependency_accounting_integration_errors, 320),
        "non_mutation": (
            "Read-only runtime introspection only. No frozen controller state, "
            "source, registry, or policy is modified."
        ),
    }
    Path("decision_support_closure_path.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
