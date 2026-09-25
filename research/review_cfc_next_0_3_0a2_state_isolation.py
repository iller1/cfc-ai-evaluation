from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from cfc_next_candidate_0_3_0a2 import Controller as CandidateController
from demonstrator.custom_case_runner import ASOF, VALID_FROM, VALID_TO

from cfc_anchor import (
    Controller as FrozenController,
    DecisionGenericDependencyAccountingAttestation,
)
import cfc_anchor._engine as engine

from research import review_minimal_blocker_accounting_taxonomy as taxonomy
from research import review_cfc_next_negative_control_baseline as negative
from research.review_decision_generic_accounting_reachability import (
    _mapping_to_draft,
)

RELATIONS = tuple(taxonomy.BLOCKERS)


def _result_signature(result):
    if result is None:
        return None
    claims = result.claims if hasattr(result, "claims") else []
    claim = claims[0] if claims else {}
    return {
        "claim_state": claim.get("status"),
        "control_closure": bool(result.control_closure),
        "decision_support_closure_valid": bool(
            result.gates.get("decision_support_closure_valid")
        ),
        "false_gates": sorted(
            k for k, v in result.gates.items() if not v
        ),
    }


def _capture(fn):
    try:
        return {
            "ok": True,
            "error": None,
            "value": _result_signature(fn()),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "value": None,
        }


def run_relation(blocker: str) -> dict:
    verifier = negative.DecisionVerifier(
        verifier_id=f"a2-state-isolation:{blocker}:v1"
    )
    trust = negative._trust_policy(verifier)

    tag = "a2-state-" + blocker.replace(":", "-")
    candidate = CandidateController(trust_policy=trust)
    identity_id = taxonomy._install_identity(candidate, tag)
    taxonomy._install_topology(candidate, tag)

    records = [
        taxonomy._build_record(
            candidate,
            tag=tag,
            identity_id=identity_id,
            blocker=blocker,
            idx=1,
            validity="CURRENT",
        ),
        taxonomy._build_record(
            candidate,
            tag=tag,
            identity_id=identity_id,
            blocker=blocker,
            idx=2,
            validity="STALE",
        ),
    ]
    snapshot = taxonomy._install_snapshot(
        candidate,
        tag=tag,
        label="evaluated",
        records=records,
    )

    text = "DemoSubject is safe."
    claim_map = {"c1": identity_id}
    req = {"c1": {"required_independent_supports": 1}}

    candidate_before = candidate.evaluate_snapshot(
        snapshot,
        text,
        records,
        claim_map,
        as_of=ASOF,
        requirements=req,
    )

    frozen_preexisting = FrozenController(trust_policy=trust)
    frozen_before = _capture(
        lambda: frozen_preexisting.evaluate_snapshot(
            snapshot,
            text,
            records,
            claim_map,
            as_of=ASOF,
            requirements=req,
        )
    )

    assessments = candidate_before.raw.get(
        "decision_level_generic_dependency_assessments",
        (),
    )
    required = [
        row
        for row in assessments
        if isinstance(row, dict)
        and row.get("decision_level_required")
    ]
    if len(required) != 1:
        raise AssertionError(
            f"{blocker}: expected one required obligation"
        )
    obligation = required[0]

    graph = (
        candidate_before.raw.get("decision_support_dependency_graph")
        or {}
    )
    selected_map = {
        cid: list(vals)
        for cid, vals in (graph.get("selected_support_map") or ())
    }
    decision_evidence = [
        _mapping_to_draft(candidate, row)
        for row in records
    ]

    accounting_id = (
        "acct:a2-state:" + blocker.replace(":", "-")
    )
    draft = candidate.draft_decision_generic_dependency_accounting(
        accounting_id=accounting_id,
        retrieval_scope_id=snapshot.scope_id,
        claim_ids=["c1"],
        selected_support_map=selected_map,
        generic_dependency_node=obligation[
            "generic_dependency_node"
        ],
        evidence_ids=obligation["evidence_ids"],
        reason="0.3.0a2 state-isolation probe.",
        text=text,
        evidence=decision_evidence,
        claim_identity_map=claim_map,
        as_of=ASOF,
        requirements=req,
    )

    commitment = (
        candidate.decision_generic_dependency_accounting_commitment(
            draft,
            decision_evidence,
        )
    )
    attestation = DecisionGenericDependencyAccountingAttestation(
        f"att:{accounting_id}",
        negative.DECISION_AUTHORITY,
        commitment,
        ASOF,
        VALID_FROM,
        VALID_TO,
    )
    candidate.install_verified_decision_generic_dependency_accounting(
        draft,
        decision_evidence,
        attestation,
        verifier,
        text=text,
        claim_identity_map=claim_map,
        as_of=ASOF,
        requirements=req,
    )
    candidate.finalize_verified_decision_dependency_accountings_for_prepare(
        text,
        decision_evidence,
        claim_map,
        as_of=ASOF,
        retrieval_scope=snapshot.scope_id,
        requirements=req,
    )

    candidate_after = candidate.evaluate_snapshot(
        snapshot,
        text,
        records,
        claim_map,
        as_of=ASOF,
        requirements=req,
    )

    frozen_same_instance_after = _capture(
        lambda: frozen_preexisting.evaluate_snapshot(
            snapshot,
            text,
            records,
            claim_map,
            as_of=ASOF,
            requirements=req,
        )
    )

    frozen_fresh = FrozenController(trust_policy=trust)
    frozen_fresh_after = _capture(
        lambda: frozen_fresh.evaluate_snapshot(
            snapshot,
            text,
            records,
            claim_map,
            as_of=ASOF,
            requirements=req,
        )
    )

    row = engine.SUPPORT_SELECTION_REGISTRY.get(accounting_id)

    before_closure = (
        frozen_before["value"]["control_closure"]
        if frozen_before["ok"]
        else None
    )
    same_after_closure = (
        frozen_same_instance_after["value"]["control_closure"]
        if frozen_same_instance_after["ok"]
        else None
    )
    fresh_after_closure = (
        frozen_fresh_after["value"]["control_closure"]
        if frozen_fresh_after["ok"]
        else None
    )

    semantic_visibility = (
        before_closure is False
        and (
            same_after_closure is True
            or fresh_after_closure is True
        )
    )

    return {
        "blocker": blocker,
        "candidate_before": _result_signature(candidate_before),
        "frozen_before_candidate_accounting": frozen_before,
        "registry_after_candidate_finalize": {
            "present": isinstance(row, dict),
            "binding_state": (
                row.get("binding_state")
                if isinstance(row, dict)
                else None
            ),
            "record_type": (
                row.get("record_type")
                if isinstance(row, dict)
                else None
            ),
        },
        "candidate_after": _result_signature(candidate_after),
        "frozen_same_instance_after_candidate_accounting": (
            frozen_same_instance_after
        ),
        "frozen_fresh_instance_after_candidate_accounting": (
            frozen_fresh_after
        ),
        "candidate_authorization_visible_to_frozen_evaluation": (
            semantic_visibility
        ),
    }


def run_isolated(blocker: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_cfc_next_0_3_0a2_state_isolation",
            "--single",
            blocker,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"{blocker}: {cp.stderr.strip() or cp.stdout.strip()}"
        )
    return json.loads(cp.stdout)


def main():
    rows = [run_isolated(blocker) for blocker in RELATIONS]

    visible = [
        row["blocker"]
        for row in rows
        if row[
            "candidate_authorization_visible_to_frozen_evaluation"
        ]
    ]

    result = {
        "test": "CFC_NEXT_0_3_0A2_STATE_ISOLATION_REVIEW",
        "candidate_version": "0.3.0a2",
        "frozen_reference": "CFC Anchor 0.2.90rc1",
        "relations_tested": list(RELATIONS),
        "candidate_authorization_visible_to_frozen_relations": visible,
        "shared_registry_state_detected": any(
            row["registry_after_candidate_finalize"]["present"]
            for row in rows
        ),
        "promotion_status": (
            "NOT_FREEZE_READY_SHARED_STATE_AUTHORIZATION"
            if visible
            else "STATE_ISOLATION_GATE_PASS"
        ),
        "historical_rescore_performed": False,
        "frozen_wheel_modified": False,
        "rows": rows,
    }

    Path("cfc_next_0_3_0a2_state_isolation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--single", choices=RELATIONS)
    args = parser.parse_args()
    if args.single:
        print(json.dumps(run_relation(args.single), sort_keys=True))
    else:
        main()
