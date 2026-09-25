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


TARGET_POLICY_KEYS = (
    "selection_does_not_delete_evidence_relations",
    "generic_dependency_selected_support_path_closure_required",
    "generic_dependency_path_through_excluded_supports_preserved",
    "excluded_excluded_relation_relevance_rule",
    "decision_dependency_accounting_resolution_type",
    "allowed_authorizers",
)

TARGET_ENGINE_SYMBOLS = (
    "support_universe_policy_valid",
    "_decision_level_generic_dependency_assessments",
    "make_decision_level_generic_dependency_universe",
    "_find_bound_decision_generic_dependency_accounting",
    "make_decision_support_closure_certificate",
    "register_decision_generic_dependency_accounting",
)

TARGET_CONTROLLER_METHODS = (
    "draft_decision_generic_dependency_accounting",
    "install_verified_decision_generic_dependency_accounting",
    "finalize_verified_decision_dependency_accountings_for_prepare",
)


def _src(obj, limit=420):
    try:
        lines = inspect.getsource(obj).splitlines()
    except Exception as exc:
        return [f"<source-error:{type(exc).__name__}:{exc}>"]
    return [f"{i}: {line}" for i, line in enumerate(lines[:limit], 1)]


def _sig(obj):
    try:
        return str(inspect.signature(obj))
    except Exception as exc:
        return f"<signature-error:{type(exc).__name__}:{exc}>"


def main():
    policy = frozen_engine.SUPPORT_UNIVERSE_POLICY
    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "DECISION_ACCOUNTING_NORMATIVE_CONTRACT_REVIEW",
        "support_universe_policy_selected": {
            key: policy.get(key)
            for key in TARGET_POLICY_KEYS
        },
        "support_universe_policy_full": policy,
        "engine_contract_sources": [],
        "controller_public_surface_sources": [],
        "non_mutation": (
            "Read-only source/policy introspection only. Frozen source, policy, "
            "registries, and controller state are not modified."
        ),
    }

    for name in TARGET_ENGINE_SYMBOLS:
        obj = getattr(frozen_engine, name, None)
        result["engine_contract_sources"].append({
            "name": name,
            "present": obj is not None,
            "signature": _sig(obj) if callable(obj) else None,
            "source": _src(obj) if callable(obj) else None,
        })

    for name in TARGET_CONTROLLER_METHODS:
        obj = getattr(Controller, name, None)
        result["controller_public_surface_sources"].append({
            "name": name,
            "present": obj is not None,
            "signature": _sig(obj) if callable(obj) else None,
            "source": _src(obj) if callable(obj) else None,
        })

    Path("decision_accounting_contract_review.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
