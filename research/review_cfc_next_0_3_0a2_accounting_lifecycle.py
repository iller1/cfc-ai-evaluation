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

MUTATIONS = (
    "EXACT_REPLAY",
    "AS_OF_SHIFT",
    "CLAIM_ID_CHANGE",
    "SCOPE_CHANGE",
    "REQUIREMENT_CHANGE",
)

SHIFTED_AS_OF = "2026-09-04"


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
        "decision_support_closure_certificate_present": (
            result.raw.get("decision_support_closure_certificate") is not None
        ),
        "false_gates": sorted(
            key for key, value in result.gates.items() if not value
        ),
    }


def _capture_eval(
    controller,
    snapshot,
    text,
    records,
    claim_map,
    as_of,
    requirements,
):
    try:
        result = controller.evaluate_snapshot(
            snapshot,
            text,
            records,
            claim_map,
            as_of=as_of,
            requirements=requirements,
        )
        return {
            "ok": True,
            "error": None,
            "value": _result_signature(result),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "value": None,
        }


def _build_bound_fixture(blocker: str):
    verifier = negative.DecisionVerifier(
        verifier_id=f"a2-accounting-lifecycle:{blocker}:v1"
    )
    trust = negative._trust_policy(verifier)

    tag = "a2-lifecycle-" + blocker.replace(":", "-")
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

    before = controller.evaluate_snapshot(
        snapshot,
        text,
        records,
        claim_map,
        as_of=ASOF,
        requirements=requirements,
    )

    assessments = before.raw.get(
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
            f"{blocker}: expected exactly one required accounting obligation"
        )
    obligation = required[0]

    graph = before.raw.get("decision_support_dependency_graph") or {}
    selected_map = {
        claim_id: list(evidence_ids)
        for claim_id, evidence_ids
        in (graph.get("selected_support_map") or ())
    }
    decision_evidence = [
        _mapping_to_draft(controller, row)
        for row in records
    ]

    accounting_id = (
        "acct:a2-lifecycle:" + blocker.replace(":", "-")
    )
    draft = controller.draft_decision_generic_dependency_accounting(
        accounting_id=accounting_id,
        retrieval_scope_id=snapshot.scope_id,
        claim_ids=["c1"],
        selected_support_map=selected_map,
        generic_dependency_node=obligation[
            "generic_dependency_node"
        ],
        evidence_ids=obligation["evidence_ids"],
        reason="0.3.0a2 accounting lifecycle mutation probe.",
        text=text,
        evidence=decision_evidence,
        claim_identity_map=claim_map,
        as_of=ASOF,
        requirements=requirements,
    )

    commitment = (
        controller.decision_generic_dependency_accounting_commitment(
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
    controller.install_verified_decision_generic_dependency_accounting(
        draft,
        decision_evidence,
        attestation,
        verifier,
        text=text,
        claim_identity_map=claim_map,
        as_of=ASOF,
        requirements=requirements,
    )
    controller.finalize_verified_decision_dependency_accountings_for_prepare(
        text,
        decision_evidence,
        claim_map,
        as_of=ASOF,
        retrieval_scope=snapshot.scope_id,
        requirements=requirements,
    )

    authorized = controller.evaluate_snapshot(
        snapshot,
        text,
        records,
        claim_map,
        as_of=ASOF,
        requirements=requirements,
    )
    if not authorized.control_closure:
        raise AssertionError(
            f"{blocker}: expected authorized baseline closure before mutation"
        )

    return {
        "controller": controller,
        "identity_id": identity_id,
        "tag": tag,
        "records": records,
        "decision_evidence": decision_evidence,
        "snapshot": snapshot,
        "text": text,
        "claim_map": claim_map,
        "requirements": requirements,
        "before": before,
        "authorized": authorized,
    }


def _mutation_context(fixture: dict, mutation: str):
    controller = fixture["controller"]
    snapshot = fixture["snapshot"]
    records = fixture["records"]
    decision_evidence = fixture["decision_evidence"]
    text = fixture["text"]
    claim_map = dict(fixture["claim_map"])
    requirements = {
        key: dict(value)
        for key, value in fixture["requirements"].items()
    }
    as_of = ASOF

    if mutation == "EXACT_REPLAY":
        pass
    elif mutation == "AS_OF_SHIFT":
        as_of = SHIFTED_AS_OF
    elif mutation == "CLAIM_ID_CHANGE":
        claim_map = {"c2": fixture["identity_id"]}
        requirements = {
            "c2": {"required_independent_supports": 1}
        }
    elif mutation == "SCOPE_CHANGE":
        snapshot = taxonomy._install_snapshot(
            controller,
            tag=fixture["tag"],
            label="alternate",
            records=records,
        )
    elif mutation == "REQUIREMENT_CHANGE":
        requirements = {
            "c1": {"required_independent_supports": 2}
        }
    else:
        raise ValueError(f"unknown mutation: {mutation}")

    return {
        "snapshot": snapshot,
        "records": records,
        "decision_evidence": decision_evidence,
        "text": text,
        "claim_map": claim_map,
        "requirements": requirements,
        "as_of": as_of,
    }


def run_case(blocker: str, mutation: str) -> dict:
    fixture = _build_bound_fixture(blocker)
    controller = fixture["controller"]
    mutated = _mutation_context(fixture, mutation)

    direct = _capture_eval(
        controller,
        mutated["snapshot"],
        mutated["text"],
        mutated["records"],
        mutated["claim_map"],
        mutated["as_of"],
        mutated["requirements"],
    )

    finalize = {
        "ok": False,
        "error": None,
    }
    after_refinalize = None

    try:
        controller.finalize_verified_decision_dependency_accountings_for_prepare(
            mutated["text"],
            mutated["decision_evidence"],
            mutated["claim_map"],
            as_of=mutated["as_of"],
            retrieval_scope=mutated["snapshot"].scope_id,
            requirements=mutated["requirements"],
        )
        finalize = {
            "ok": True,
            "error": None,
        }
        after_refinalize = _capture_eval(
            controller,
            mutated["snapshot"],
            mutated["text"],
            mutated["records"],
            mutated["claim_map"],
            mutated["as_of"],
            mutated["requirements"],
        )
    except Exception as exc:
        finalize = {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
        }

    direct_closure = (
        direct["value"]["control_closure"]
        if direct["ok"] and direct["value"] is not None
        else None
    )
    refinalized_closure = (
        after_refinalize["value"]["control_closure"]
        if (
            after_refinalize is not None
            and after_refinalize["ok"]
            and after_refinalize["value"] is not None
        )
        else None
    )

    exact_control = mutation == "EXACT_REPLAY"
    if exact_control:
        contract_pass = (
            direct_closure is True
            and finalize["ok"] is True
            and refinalized_closure is True
        )
    else:
        contract_pass = (
            finalize["ok"] is False
            or refinalized_closure is not True
        )

    return {
        "blocker": blocker,
        "mutation": mutation,
        "authorized_baseline": _result_signature(
            fixture["authorized"]
        ),
        "direct_evaluate_after_mutation": direct,
        "refinalize": finalize,
        "evaluate_after_refinalize": after_refinalize,
        "direct_evaluate_stale_authorization_visible": (
            not exact_control and direct_closure is True
        ),
        "refinalized_stale_authorization_visible": (
            not exact_control and refinalized_closure is True
        ),
        "contract_pass": contract_pass,
    }


def _run_isolated(blocker: str, mutation: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_cfc_next_0_3_0a2_accounting_lifecycle",
            "--single-blocker",
            blocker,
            "--single-mutation",
            mutation,
        ],
        capture_output=True,
        text=True,
        timeout=150,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"{blocker}/{mutation}: "
            f"{cp.stderr.strip() or cp.stdout.strip()}"
        )
    return json.loads(cp.stdout)


def main() -> None:
    rows = [
        _run_isolated(blocker, mutation)
        for blocker in REPRESENTATIVE_RELATIONS
        for mutation in MUTATIONS
    ]

    failed_contracts = [
        f"{row['blocker']}::{row['mutation']}"
        for row in rows
        if not row["contract_pass"]
    ]
    direct_visibility = [
        f"{row['blocker']}::{row['mutation']}"
        for row in rows
        if row["direct_evaluate_stale_authorization_visible"]
    ]
    refinalized_visibility = [
        f"{row['blocker']}::{row['mutation']}"
        for row in rows
        if row["refinalized_stale_authorization_visible"]
    ]

    exact_controls = [
        row for row in rows
        if row["mutation"] == "EXACT_REPLAY"
    ]

    if refinalized_visibility:
        classification = (
            "REFINALIZED_STALE_ACCOUNTING_AUTHORIZATION_PERSISTENCE"
        )
    elif direct_visibility:
        classification = (
            "DIRECT_EVALUATE_LIFECYCLE_BOUNDARY_FINDING"
        )
    elif failed_contracts:
        classification = "LIFECYCLE_CONTROL_FAILURE"
    else:
        classification = "ACCOUNTING_LIFECYCLE_REPRESENTATIVE_PASS"

    result = {
        "test": "CFC_NEXT_0_3_0A2_ACCOUNTING_LIFECYCLE_REVIEW",
        "candidate_version": "0.3.0a2",
        "frozen_reference": "CFC Anchor 0.2.90rc1",
        "relations_tested": list(REPRESENTATIVE_RELATIONS),
        "mutations_tested": list(MUTATIONS),
        "case_count": len(rows),
        "exact_replay_controls_pass": all(
            row["contract_pass"] for row in exact_controls
        ),
        "failed_contracts": failed_contracts,
        "direct_evaluate_stale_authorization_visible": (
            direct_visibility
        ),
        "refinalized_stale_authorization_visible": (
            refinalized_visibility
        ),
        "classification": classification,
        "frozen_candidate_modified": False,
        "frozen_reference_modified": False,
        "historical_rescore_performed": False,
        "rows": rows,
    }

    Path(
        "cfc_next_0_3_0a2_accounting_lifecycle.json"
    ).write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--single-blocker",
        choices=REPRESENTATIVE_RELATIONS,
    )
    parser.add_argument(
        "--single-mutation",
        choices=MUTATIONS,
    )
    args = parser.parse_args()
    if args.single_blocker and args.single_mutation:
        print(
            json.dumps(
                run_case(
                    args.single_blocker,
                    args.single_mutation,
                ),
                sort_keys=True,
            )
        )
    elif args.single_blocker or args.single_mutation:
        raise SystemExit(
            "--single-blocker and --single-mutation must be used together"
        )
    else:
        main()
