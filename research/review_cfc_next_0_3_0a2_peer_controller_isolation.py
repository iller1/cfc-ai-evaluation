from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from cfc_next_candidate_0_3_0a2 import Controller
from cfc_anchor import DecisionGenericDependencyAccountingAttestation

from demonstrator.custom_case_runner import ASOF, VALID_FROM, VALID_TO
from research import review_minimal_blocker_accounting_taxonomy as taxonomy
from research import review_cfc_next_negative_control_baseline as negative
from research.review_decision_generic_accounting_reachability import (
    _mapping_to_draft,
)


REPRESENTATIVE_RELATIONS = (
    "root_origin_shared",
    "extractor_shared",
    "dependency:data_source",
)


def _sig(result):
    claims = result.claims if hasattr(result, "claims") else []
    claim = claims[0] if claims else {}
    return {
        "claim_state": claim.get("status"),
        "control_closure": bool(result.control_closure),
        "decision_support_closure_valid": bool(
            result.gates.get("decision_support_closure_valid")
        ),
        "false_gates": sorted(
            key for key, value in result.gates.items() if not value
        ),
    }


def _capture(fn):
    try:
        return {"ok": True, "error": None, "value": _sig(fn())}
    except Exception as exc:
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "value": None,
        }


def _build_fixture(blocker: str, tenant: str):
    verifier = negative.DecisionVerifier(
        verifier_id=f"a2-peer:{tenant}:{blocker}:v1"
    )
    trust = negative._trust_policy(verifier)
    tag = f"a2-peer-{tenant.lower()}-" + blocker.replace(":", "-")

    controller = Controller(trust_policy=trust)
    identity_id = taxonomy._install_identity(controller, tag)
    taxonomy._install_topology(controller, tag)

    records = [
        taxonomy._build_record(
            controller,
            tag=tag,
            identity_id=identity_id,
            blocker=blocker,
            idx=1,
            validity="CURRENT",
        ),
        taxonomy._build_record(
            controller,
            tag=tag,
            identity_id=identity_id,
            blocker=blocker,
            idx=2,
            validity="STALE",
        ),
    ]
    snapshot = taxonomy._install_snapshot(
        controller,
        tag=tag,
        label="evaluated",
        records=records,
    )

    text = "DemoSubject is safe."
    claim_map = {"c1": identity_id}
    requirements = {"c1": {"required_independent_supports": 1}}
    baseline = controller.evaluate_snapshot(
        snapshot,
        text,
        records,
        claim_map,
        as_of=ASOF,
        requirements=requirements,
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
            f"{tenant}/{blocker}: expected one required obligation"
        )

    graph = baseline.raw.get("decision_support_dependency_graph") or {}
    selected_map = {
        claim_id: list(evidence_ids)
        for claim_id, evidence_ids
        in (graph.get("selected_support_map") or ())
    }
    decision_evidence = [
        _mapping_to_draft(controller, row) for row in records
    ]

    return {
        "tenant": tenant,
        "controller": controller,
        "trust": trust,
        "verifier": verifier,
        "identity_id": identity_id,
        "records": records,
        "snapshot": snapshot,
        "text": text,
        "claim_map": claim_map,
        "requirements": requirements,
        "baseline": baseline,
        "obligation": required[0],
        "selected_map": selected_map,
        "decision_evidence": decision_evidence,
    }


def _install_accounting(fixture: dict, accounting_id: str):
    c = fixture["controller"]
    obligation = fixture["obligation"]
    draft = c.draft_decision_generic_dependency_accounting(
        accounting_id=accounting_id,
        retrieval_scope_id=fixture["snapshot"].scope_id,
        claim_ids=["c1"],
        selected_support_map=fixture["selected_map"],
        generic_dependency_node=obligation["generic_dependency_node"],
        evidence_ids=obligation["evidence_ids"],
        reason=f"Peer isolation accounting for {fixture['tenant']}.",
        text=fixture["text"],
        evidence=fixture["decision_evidence"],
        claim_identity_map=fixture["claim_map"],
        as_of=ASOF,
        requirements=fixture["requirements"],
    )
    commitment = c.decision_generic_dependency_accounting_commitment(
        draft, fixture["decision_evidence"]
    )
    attestation = DecisionGenericDependencyAccountingAttestation(
        f"att:{fixture['tenant']}:{accounting_id}",
        negative.DECISION_AUTHORITY,
        commitment,
        ASOF,
        VALID_FROM,
        VALID_TO,
    )
    installation = c.install_verified_decision_generic_dependency_accounting(
        draft,
        fixture["decision_evidence"],
        attestation,
        fixture["verifier"],
        text=fixture["text"],
        claim_identity_map=fixture["claim_map"],
        as_of=ASOF,
        requirements=fixture["requirements"],
    )
    c.finalize_verified_decision_dependency_accountings_for_prepare(
        fixture["text"],
        fixture["decision_evidence"],
        fixture["claim_map"],
        as_of=ASOF,
        retrieval_scope=fixture["snapshot"].scope_id,
        requirements=fixture["requirements"],
    )
    return draft, installation


def _evaluate_fixture(controller, fixture):
    return controller.evaluate_snapshot(
        fixture["snapshot"],
        fixture["text"],
        fixture["records"],
        fixture["claim_map"],
        as_of=ASOF,
        requirements=fixture["requirements"],
    )


def run_relation(blocker: str) -> dict:
    a = _build_fixture(blocker, "A")
    b = _build_fixture(blocker, "B")

    if a["baseline"].control_closure or b["baseline"].control_closure:
        raise AssertionError(
            f"{blocker}: peer-isolation baselines must both start blocked"
        )

    accounting_id = "acct:a2-peer:" + blocker.replace(":", "-")
    _install_accounting(a, accounting_id)

    a_after = _evaluate_fixture(a["controller"], a)
    if not a_after.control_closure:
        raise AssertionError(
            f"{blocker}: tenant A accounting did not authorize A"
        )

    b_same = _capture(lambda: _evaluate_fixture(b["controller"], b))

    b_fresh_controller = Controller(trust_policy=b["trust"])
    b_fresh = _capture(
        lambda: _evaluate_fixture(b_fresh_controller, b)
    )

    duplicate_error = None
    duplicate_installation = None
    try:
        _, duplicate_installation = _install_accounting(
            b, accounting_id
        )
    except Exception as exc:
        duplicate_error = f"{type(exc).__name__}: {exc}"

    b_after_duplicate_attempt = _capture(
        lambda: _evaluate_fixture(b["controller"], b)
    )

    b_same_closure = (
        b_same["value"]["control_closure"]
        if b_same["ok"] and b_same["value"] is not None
        else None
    )
    b_fresh_closure = (
        b_fresh["value"]["control_closure"]
        if b_fresh["ok"] and b_fresh["value"] is not None
        else None
    )
    b_after_duplicate_closure = (
        b_after_duplicate_attempt["value"]["control_closure"]
        if (
            b_after_duplicate_attempt["ok"]
            and b_after_duplicate_attempt["value"] is not None
        )
        else None
    )

    peer_visibility = (
        b_same_closure is True or b_fresh_closure is True
    )
    duplicate_collision_authorized = (
        duplicate_installation is not None
        or b_after_duplicate_closure is True
    )

    contract_pass = (
        peer_visibility is False
        and duplicate_error is not None
        and duplicate_collision_authorized is False
    )

    return {
        "blocker": blocker,
        "tenant_a_before": _sig(a["baseline"]),
        "tenant_b_before": _sig(b["baseline"]),
        "tenant_a_after_accounting": _sig(a_after),
        "tenant_b_same_controller_after_a_accounting": b_same,
        "tenant_b_fresh_controller_after_a_accounting": b_fresh,
        "peer_candidate_authorization_visible": peer_visibility,
        "duplicate_accounting_id_attempt": {
            "error": duplicate_error,
            "installation_created": duplicate_installation is not None,
            "tenant_b_after_attempt": b_after_duplicate_attempt,
            "authorized": duplicate_collision_authorized,
        },
        "contract_pass": contract_pass,
    }


def _run_isolated(blocker: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_cfc_next_0_3_0a2_peer_controller_isolation",
            "--single",
            blocker,
        ],
        capture_output=True,
        text=True,
        timeout=150,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"{blocker}: {cp.stderr.strip() or cp.stdout.strip()}"
        )
    return json.loads(cp.stdout)


def main():
    rows = [
        _run_isolated(blocker)
        for blocker in REPRESENTATIVE_RELATIONS
    ]

    leaks = [
        row["blocker"]
        for row in rows
        if row["peer_candidate_authorization_visible"]
    ]
    duplicate_failures = [
        row["blocker"]
        for row in rows
        if row["duplicate_accounting_id_attempt"]["authorized"]
        or row["duplicate_accounting_id_attempt"]["error"] is None
    ]
    failed = [
        row["blocker"] for row in rows if not row["contract_pass"]
    ]

    if leaks:
        classification = "PEER_CANDIDATE_AUTHORIZATION_LEAK"
    elif duplicate_failures:
        classification = "CROSS_CONTEXT_ACCOUNTING_ID_COLLISION"
    elif failed:
        classification = "PEER_CONTROLLER_ISOLATION_FAILURE"
    else:
        classification = "PEER_CONTROLLER_ISOLATION_REPRESENTATIVE_PASS"

    result = {
        "test": "CFC_NEXT_0_3_0A2_PEER_CONTROLLER_ISOLATION",
        "candidate_version": "0.3.0a2",
        "relations_tested": list(REPRESENTATIVE_RELATIONS),
        "case_count": len(rows),
        "peer_candidate_authorization_visible_relations": leaks,
        "duplicate_accounting_id_failures": duplicate_failures,
        "failed_contracts": failed,
        "classification": classification,
        "same_interpreter_stateful_concurrency_claimed": False,
        "frozen_candidate_modified": False,
        "frozen_reference_modified": False,
        "historical_rescore_performed": False,
        "rows": rows,
    }

    Path(
        "cfc_next_0_3_0a2_peer_controller_isolation.json"
    ).write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--single", choices=REPRESENTATIVE_RELATIONS
    )
    args = parser.parse_args()
    if args.single:
        print(json.dumps(run_relation(args.single), sort_keys=True))
    else:
        main()
