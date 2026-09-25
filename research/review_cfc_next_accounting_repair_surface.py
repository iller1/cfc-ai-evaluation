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

ENGINE_SYMBOLS = (
    "dependency_nodes",
    "raw_generic_dependency_nodes",
    "generic_dependency_representation_records",
    "_semantic_identifier",
    "canonical_generic_dependency_node",
    "register_decision_generic_dependency_accounting",
    "bind_decision_generic_dependency_accountings_for_prepare",
    "_find_bound_decision_generic_dependency_accounting",
    "_decision_level_generic_dependency_assessments",
)

CONTROLLER_METHODS = (
    "draft_decision_generic_dependency_accounting",
    "install_verified_decision_generic_dependency_accounting",
    "finalize_verified_decision_dependency_accountings_for_prepare",
)


def _src(obj):
    if obj is None:
        return None
    try:
        return inspect.getsource(obj).splitlines()
    except Exception as exc:
        return [f"<source-error:{type(exc).__name__}:{exc}>"]


def _sig(obj):
    if obj is None:
        return None
    try:
        return str(inspect.signature(obj))
    except Exception as exc:
        return f"<signature-error:{type(exc).__name__}:{exc}>"


def main():
    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "CFC_NEXT_ACCOUNTING_REPAIR_SURFACE_INSPECTION",
        "policy": frozen_engine.SUPPORT_UNIVERSE_POLICY,
        "constants": {
            "SOURCE_SEMANTIC_NODE_TYPES": sorted(
                getattr(frozen_engine, "SOURCE_SEMANTIC_NODE_TYPES", ())
            ),
            "DEPENDENCY_PREFIX": getattr(
                frozen_engine, "DEPENDENCY_PREFIX", {}
            ),
        },
        "engine_symbols": [],
        "controller_methods": [],
        "non_mutation": (
            "Read-only source/policy inspection. Frozen source, policy, "
            "registries, and controller state are not modified."
        ),
    }

    for name in ENGINE_SYMBOLS:
        obj = getattr(frozen_engine, name, None)
        result["engine_symbols"].append({
            "name": name,
            "present": obj is not None,
            "signature": _sig(obj),
            "source": _src(obj),
        })

    for name in CONTROLLER_METHODS:
        obj = getattr(Controller, name, None)
        result["controller_methods"].append({
            "name": name,
            "present": obj is not None,
            "signature": _sig(obj),
            "source": _src(obj),
        })

    Path("cfc_next_accounting_repair_surface.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
