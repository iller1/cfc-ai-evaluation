from __future__ import annotations

import json
import sys
from pathlib import Path

from demonstrator import server as demo_server

demo_server.ensure_runtime()
sys.path.insert(0, str(demo_server.RUNTIME))

from cfc_anchor import Controller
import cfc_anchor._engine as frozen_engine

from demonstrator.custom_case_runner import ASOF
from research.review_stale_relation_snapshot_locality import (
    _trust_policy,
    _install_identity,
    _install_topology,
    _build_record,
    _install_snapshot,
)


def main():
    relation_mode = "GENERIC_DEPENDENCY"
    tag = "core-bindability:generic_dependency"

    c = Controller(trust_policy=_trust_policy())
    identity_id = _install_identity(c, tag)
    _install_topology(c, tag)

    e1 = _build_record(
        c,
        tag=tag,
        identity_id=identity_id,
        relation_mode=relation_mode,
        idx=1,
        validity="CURRENT",
    )
    e2 = _build_record(
        c,
        tag=tag,
        identity_id=identity_id,
        relation_mode=relation_mode,
        idx=2,
        validity="STALE",
    )
    records = [e1, e2]
    snapshot = _install_snapshot(
        c,
        tag=tag,
        label="evaluated",
        records=records,
    )

    text = "DemoSubject is safe."
    claim_map = {"c1": identity_id}
    req = {"c1": {"required_independent_supports": 1}}

    baseline = c.evaluate_snapshot(
        snapshot,
        text,
        records,
        claim_map,
        as_of=ASOF,
        requirements=req,
    )
    baseline_claim = baseline.claims[0] if baseline.claims else {}

    assessments = baseline.raw.get(
        "decision_level_generic_dependency_assessments", []
    )
    required = [
        row
        for row in assessments
        if isinstance(row, dict) and row.get("decision_level_required")
    ]
    if len(required) != 1:
        raise RuntimeError(
            f"expected one required generic obligation, got {len(required)}"
        )

    obligation = required[0]
    graph = baseline.raw.get("decision_support_dependency_graph") or {}
    selected_map = {
        cid: list(vals)
        for cid, vals in (graph.get("selected_support_map") or ())
    }

    accounting_id = "acct:core-bindability:exact-engine-state"
    resolution_type = frozen_engine.SUPPORT_UNIVERSE_POLICY[
        "decision_dependency_accounting_resolution_type"
    ]

    registered = frozen_engine.register_decision_generic_dependency_accounting(
        accounting_id=accounting_id,
        retrieval_scope_id=snapshot.scope_id,
        claim_ids=["c1"],
        selected_support_map=selected_map,
        generic_dependency_node=tuple(obligation["generic_dependency_node"]),
        evidence_ids=list(obligation["evidence_ids"]),
        resolution_type=resolution_type,
        reason=(
            "Core-bindability localization probe for the exact mixed "
            "selected/stale decision obligation."
        ),
    )

    bind_error = None
    try:
        frozen_engine.bind_decision_generic_dependency_accountings_for_prepare(
            text,
            records,
            claim_map,
            ASOF,
            c.scope,
            c.extraction,
            snapshot.scope_id,
            req,
            (accounting_id,),
        )
    except Exception as exc:
        bind_error = f"{type(exc).__name__}: {exc}"

    bound_row = frozen_engine.SUPPORT_SELECTION_REGISTRY.get(accounting_id)

    core_error = None
    core_result = None
    try:
        bundle = frozen_engine.prepare(
            text,
            records,
            claim_map,
            ASOF,
            c.scope,
            c.extraction,
            snapshot.scope_id,
            req,
            None,
        )
        core_result = frozen_engine.audit_text(
            text,
            records,
            claim_map,
            ASOF,
            c.scope,
            c.extraction,
            snapshot.scope_id,
            req,
            None,
            *bundle,
            resource_exhausted=False,
        )
    except Exception as exc:
        core_error = f"{type(exc).__name__}: {exc}"

    after = c.evaluate_snapshot(
        snapshot,
        text,
        records,
        claim_map,
        as_of=ASOF,
        requirements=req,
    )
    after_claim = after.claims[0] if after.claims else {}

    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "DECISION_ACCOUNTING_CORE_BINDABILITY",
        "relation_mode": relation_mode,
        "non_production_control": (
            "This probe directly uses frozen-engine registration/binding APIs "
            "to localize reachability. It does not modify frozen source or policy "
            "and is not an admissible public Controller workflow."
        ),
        "obligation": {
            "generic_dependency_node": list(obligation["generic_dependency_node"]),
            "evidence_ids": list(obligation["evidence_ids"]),
            "selected_support_map": selected_map,
            "endpoint_classifications": obligation.get("endpoint_classifications"),
            "endpoint_claim_ownership": obligation.get("endpoint_claim_ownership"),
        },
        "baseline": {
            "claim_state": baseline_claim.get("status"),
            "control_closure": bool(baseline.control_closure),
            "false_gates": sorted(k for k, v in baseline.gates.items() if not v),
            "decision_support_closure_valid": bool(
                baseline.gates.get("decision_support_closure_valid")
            ),
            "integration_errors": baseline.raw.get("integration_errors", []),
        },
        "registration": {
            "registered": isinstance(registered, dict),
            "binding_state_before_bind": (
                registered.get("binding_state")
                if isinstance(registered, dict)
                else None
            ),
            "bind_error": bind_error,
            "binding_state_after_bind": (
                bound_row.get("binding_state")
                if isinstance(bound_row, dict)
                else None
            ),
            "selected_support_map": (
                bound_row.get("selected_support_map")
                if isinstance(bound_row, dict)
                else None
            ),
            "evidence_ids": (
                bound_row.get("evidence_ids")
                if isinstance(bound_row, dict)
                else None
            ),
        },
        "direct_frozen_engine_after_bind": {
            "error": core_error,
            "claim_state": (
                (core_result.get("claims") or [{}])[0].get("status")
                if isinstance(core_result, dict)
                else None
            ),
            "control_closure": (
                bool(core_result.get("control_closure"))
                if isinstance(core_result, dict)
                else None
            ),
            "false_gates": (
                sorted(k for k, v in core_result.get("gates", {}).items() if not v)
                if isinstance(core_result, dict)
                else None
            ),
            "decision_support_closure_valid": (
                bool(core_result.get("gates", {}).get("decision_support_closure_valid"))
                if isinstance(core_result, dict)
                else None
            ),
            "decision_support_closure_certificate_present": (
                core_result.get("decision_support_closure_certificate") is not None
                if isinstance(core_result, dict)
                else None
            ),
        },
        "after_internal_bind": {
            "claim_state": after_claim.get("status"),
            "control_closure": bool(after.control_closure),
            "false_gates": sorted(k for k, v in after.gates.items() if not v),
            "decision_support_closure_valid": bool(
                after.gates.get("decision_support_closure_valid")
            ),
            "decision_support_closure_certificate_present": (
                after.raw.get("decision_support_closure_certificate") is not None
            ),
            "integration_errors": after.raw.get("integration_errors", []),
        },
    }

    Path("decision_accounting_core_bindability.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
