from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from cfc_next_candidate_0_3_0a2 import Controller, CANDIDATE_VERSION, FROZEN_REFERENCE
from demonstrator.custom_case_runner import ASOF, VALID_FROM, VALID_TO

from cfc_anchor import DecisionGenericDependencyAccountingAttestation
import cfc_anchor._engine as engine

from research import review_minimal_blocker_accounting_taxonomy as taxonomy
from research import review_cfc_next_negative_control_baseline as negative
from research.review_decision_generic_accounting_reachability import (
    _mapping_to_draft,
)


def _positive(blocker: str) -> dict:
    verifier = negative.DecisionVerifier(
        verifier_id=f"cfc-next-positive:{blocker}:v1"
    )

    original_controller = taxonomy.Controller
    original_trust = taxonomy._trust_policy
    taxonomy.Controller = Controller
    taxonomy._trust_policy = lambda: negative._trust_policy(verifier)
    try:
        c, identity_id, records, snapshot = taxonomy.build_fixture(blocker)
    finally:
        taxonomy.Controller = original_controller
        taxonomy._trust_policy = original_trust

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
    assessments = baseline.raw.get(
        "decision_level_generic_dependency_assessments", ()
    )
    required = [
        row
        for row in assessments
        if isinstance(row, dict) and row.get("decision_level_required")
    ]
    if len(required) != 1:
        raise AssertionError(
            f"{blocker}: expected one required obligation, got {len(required)}"
        )
    obligation = required[0]

    graph = baseline.raw.get("decision_support_dependency_graph") or {}
    selected_map = {
        cid: list(vals)
        for cid, vals in (graph.get("selected_support_map") or ())
    }
    decision_evidence = [_mapping_to_draft(c, row) for row in records]

    accounting_id = f"acct:cfc-next:{blocker.replace(':','-')}"
    draft = c.draft_decision_generic_dependency_accounting(
        accounting_id=accounting_id,
        retrieval_scope_id=snapshot.scope_id,
        claim_ids=["c1"],
        selected_support_map=selected_map,
        generic_dependency_node=obligation["generic_dependency_node"],
        evidence_ids=obligation["evidence_ids"],
        reason=f"CFC-next positive acceptance for {blocker}.",
        text=text,
        evidence=decision_evidence,
        claim_identity_map=claim_map,
        as_of=ASOF,
        requirements=req,
    )

    expected = c.decision_generic_dependency_accounting_commitment(
        draft,
        decision_evidence,
    )
    attestation = DecisionGenericDependencyAccountingAttestation(
        f"att:{accounting_id}",
        negative.DECISION_AUTHORITY,
        expected,
        ASOF,
        VALID_FROM,
        VALID_TO,
    )
    installation = c.install_verified_decision_generic_dependency_accounting(
        draft,
        decision_evidence,
        attestation,
        verifier,
        text=text,
        claim_identity_map=claim_map,
        as_of=ASOF,
        requirements=req,
    )
    c.finalize_verified_decision_dependency_accountings_for_prepare(
        text,
        decision_evidence,
        claim_map,
        as_of=ASOF,
        retrieval_scope=snapshot.scope_id,
        requirements=req,
    )

    after = c.evaluate_snapshot(
        snapshot,
        text,
        records,
        claim_map,
        as_of=ASOF,
        requirements=req,
    )
    claim = after.claims[0] if after.claims else {}
    registry = engine.SUPPORT_SELECTION_REGISTRY.get(accounting_id)

    return {
        "blocker": blocker,
        "baseline": {
            "claim_state": baseline.claims[0].get("status") if baseline.claims else None,
            "control_closure": bool(baseline.control_closure),
            "false_gates": sorted(k for k, v in baseline.gates.items() if not v),
        },
        "draft": {
            "node": list(draft.generic_dependency_node),
            "evidence_ids": list(draft.evidence_ids),
            "selected_support_map": [
                [cid, list(vals)] for cid, vals in draft.selected_support_map
            ],
        },
        "installation": {
            "type": type(installation).__name__,
            "repr": repr(installation),
        },
        "registry_binding_state": (
            registry.get("binding_state")
            if isinstance(registry, dict)
            else None
        ),
        "after": {
            "claim_state": claim.get("status"),
            "control_closure": bool(after.control_closure),
            "decision_support_closure_valid": bool(
                after.gates.get("decision_support_closure_valid")
            ),
            "decision_support_closure_certificate_present": (
                after.raw.get("decision_support_closure_certificate") is not None
            ),
            "false_gates": sorted(k for k, v in after.gates.items() if not v),
        },
    }


def _negative(control_id: str) -> dict:
    original = negative.Controller
    negative.Controller = Controller
    try:
        row = negative.run_control(control_id)
    finally:
        negative.Controller = original

    registry = row.get("registry")
    bound = (
        isinstance(registry, dict)
        and registry.get("binding_state") == "BOUND"
    )
    errors = [
        stage.get("error")
        for stage in row.get("stages", {}).values()
        if stage.get("error")
    ]
    return {
        "id": control_id,
        "passes_negative_contract": not bound and bool(errors),
        "bound": bound,
        "errors": errors,
        "stages": row.get("stages", {}),
        "registry": registry,
    }


def _run_isolated(mode: str, value: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_cfc_next_0_3_0a2_acceptance",
            f"--single-{mode}",
            value,
        ],
        capture_output=True,
        text=True,
        timeout=90,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"{mode}:{value}: {cp.stderr.strip() or cp.stdout.strip()}"
        )
    return json.loads(cp.stdout)


def main():
    positives = [
        _run_isolated("positive", blocker)
        for blocker in taxonomy.BLOCKERS
    ]
    negatives = [
        _run_isolated("negative", control_id)
        for control_id in negative.NEGATIVE_IDS
    ]

    for row in positives:
        assert row["baseline"]["claim_state"] == "VERIFIED"
        assert row["baseline"]["control_closure"] is False
        assert row["baseline"]["false_gates"] == [
            "decision_support_closure_valid"
        ]
        assert row["registry_binding_state"] == "BOUND"
        assert row["after"]["claim_state"] == "VERIFIED"
        assert row["after"]["control_closure"] is True
        assert row["after"]["decision_support_closure_valid"] is True
        assert row["after"]["decision_support_closure_certificate_present"] is True
        assert row["after"]["false_gates"] == []

    assert all(row["passes_negative_contract"] for row in negatives)
    assert not any(row["bound"] for row in negatives)

    result = {
        "test": "CFC_NEXT_0_3_0A2_DECISION_ACCOUNTING_ACCEPTANCE",
        "candidate_version": CANDIDATE_VERSION,
        "frozen_reference": FROZEN_REFERENCE,
        "positive_count": len(positives),
        "positive_pass_count": sum(
            row["after"]["control_closure"] is True
            for row in positives
        ),
        "negative_count": len(negatives),
        "negative_fail_closed_count": sum(
            row["passes_negative_contract"]
            for row in negatives
        ),
        "unexpected_bound_negative_paths": [
            row["id"] for row in negatives if row["bound"]
        ],
        "frozen_reference_modified": False,
        "historical_rescore_performed": False,
        "status": "PASS",
        "positives": positives,
        "negatives": negatives,
    }
    Path("cfc_next_0_3_0a2_acceptance.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-positive", choices=taxonomy.BLOCKERS)
    parser.add_argument("--single-negative", choices=negative.NEGATIVE_IDS)
    args = parser.parse_args()
    if args.single_positive:
        print(json.dumps(_positive(args.single_positive), sort_keys=True))
    elif args.single_negative:
        print(json.dumps(_negative(args.single_negative), sort_keys=True))
    else:
        main()
