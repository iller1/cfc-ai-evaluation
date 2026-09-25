from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from demonstrator import server as demo_server

demo_server.ensure_runtime()
sys.path.insert(0, str(demo_server.RUNTIME))

from cfc_anchor import (
    Controller,
    HostTrustPolicy,
    HostTrustRegistration,
    DecisionGenericDependencyAccountingAttestation,
    DecisionGenericDependencyAccountingVerdict,
)
import cfc_anchor._engine as frozen_engine

from demonstrator.custom_case_runner import (
    ASOF,
    VALID_FROM,
    VALID_TO,
    AUTHORITIES,
    VERIFIERS,
)
from research.review_stale_relation_snapshot_locality import (
    _install_identity,
    _install_topology,
    _install_snapshot,
)
from research.review_minimal_blocker_accounting_taxonomy import (
    _build_record,
)
from research.review_decision_generic_accounting_reachability import (
    _mapping_to_draft,
)

NEGATIVE_IDS = (
    "NEG_WRONG_NODE_CORRECT_ENDPOINTS",
    "NEG_CORRECT_NODE_WRONG_ENDPOINT_SET",
    "NEG_NONSEL_ENDPOINT_OUTSIDE_EVALUATED_SNAPSHOT",
    "NEG_NONSEL_ENDPOINT_WITHOUT_REQUIRED_OBLIGATION",
    "NEG_WRONG_SELECTED_SUPPORT_MAP",
    "NEG_WRONG_RETRIEVAL_SCOPE_OR_SNAPSHOT",
    "NEG_WRONG_CLAIM_SET_OR_REQUIREMENTS",
    "NEG_STALE_DECISION_CONTEXT_COMMITMENT",
    "NEG_SOURCE_SEMANTIC_NODE_IN_GENERIC_CHANNEL",
    "NEG_INVALID_NODE_ARITY_TYPE_OR_BLANK_IDENTIFIER",
    "NEG_UNVERIFIED_OR_MISMATCHED_EXTERNAL_ATTESTATION",
    "NEG_ACCOUNTING_FAILS_EXACT_FRESH_UNIVERSE_BIND",
)

DECISION_KIND = "DECISION_GENERIC_DEPENDENCY_ACCOUNTING"
DECISION_AUTHORITY = "LOCAL_SUPPORT_UNIVERSE_AUTHORITY"


class DecisionVerifier:
    def __init__(
        self,
        *,
        approved: bool = True,
        verifier_id: str = "negative-control:decision-accounting:v1",
        force_accounting_id: str | None = None,
    ):
        self.approved = approved
        self.verifier_id = verifier_id
        self.force_accounting_id = force_accounting_id

    def verify(self, attestation, *, draft, evidence):
        return DecisionGenericDependencyAccountingVerdict(
            self.approved,
            self.verifier_id,
            attestation.attestation_id,
            attestation.authority_id,
            self.force_accounting_id or draft.accounting_id,
            "SYNTHETIC_NEGATIVE_CONTROL",
            "" if self.approved else "NEGATIVE_CONTROL_REJECTION",
        )


def _trust_policy(verifier: DecisionVerifier) -> HostTrustPolicy:
    registrations = [
        HostTrustRegistration(kind, AUTHORITIES[kind], VERIFIERS[kind])
        for kind in AUTHORITIES
    ]
    registrations.append(
        HostTrustRegistration(
            DECISION_KIND,
            DECISION_AUTHORITY,
            verifier,
        )
    )
    return HostTrustPolicy(tuple(registrations))


def _fixture(
    control_id: str,
    *,
    blocker: str = "dependency:data_source",
    include_extra_record: bool = False,
    extra_in_snapshot: bool = False,
):
    verifier = DecisionVerifier()
    c = Controller(trust_policy=_trust_policy(verifier))
    tag = f"negative-{control_id.lower().replace('_','-')}"
    identity_id = _install_identity(c, tag)
    _install_topology(c, tag)

    records = [
        _build_record(
            c,
            tag=tag,
            identity_id=identity_id,
            blocker=blocker,
            idx=1,
            validity="CURRENT",
        ),
        _build_record(
            c,
            tag=tag,
            identity_id=identity_id,
            blocker=blocker,
            idx=2,
            validity="STALE",
        ),
    ]
    extra = None
    if include_extra_record:
        extra = _build_record(
            c,
            tag=tag,
            identity_id=identity_id,
            blocker="dependency:runtime",
            idx=3,
            validity="STALE",
        )

    snapshot_records = records + ([extra] if extra_in_snapshot and extra else [])
    snapshot = _install_snapshot(
        c,
        tag=tag,
        label="evaluated",
        records=snapshot_records,
    )

    text = "DemoSubject is safe."
    claim_map = {"c1": identity_id}
    req = {"c1": {"required_independent_supports": 1}}

    baseline = c.evaluate_snapshot(
        snapshot,
        text,
        snapshot_records,
        claim_map,
        as_of=ASOF,
        requirements=req,
    )
    assessments = baseline.raw.get(
        "decision_level_generic_dependency_assessments", []
    )
    required = [
        row
        for row in assessments
        if isinstance(row, dict) and row.get("decision_level_required")
    ]
    graph = baseline.raw.get("decision_support_dependency_graph") or {}
    selected_map = {
        cid: list(vals)
        for cid, vals in (graph.get("selected_support_map") or ())
    }

    decision_records = records + ([extra] if extra else [])
    decision_evidence = [
        _mapping_to_draft(c, row)
        for row in decision_records
    ]

    exact = required[0] if required else None
    return {
        "controller": c,
        "verifier": verifier,
        "identity_id": identity_id,
        "records": records,
        "extra": extra,
        "snapshot_records": snapshot_records,
        "snapshot": snapshot,
        "text": text,
        "claim_map": claim_map,
        "requirements": req,
        "baseline": baseline,
        "required": required,
        "exact_obligation": exact,
        "selected_map": selected_map,
        "decision_evidence": decision_evidence,
    }


def _expanded_selected_map(fx, evidence_ids=None):
    values = set()
    for vals in fx["selected_map"].values():
        values.update(vals)
    if evidence_ids is None:
        evidence_ids = (
            fx["exact_obligation"]["evidence_ids"]
            if fx["exact_obligation"]
            else ()
        )
    values.update(evidence_ids)
    return {"c1": sorted(values)}


def _draft(
    fx,
    *,
    accounting_id,
    node,
    evidence_ids,
    selected_support_map=None,
    retrieval_scope_id=None,
    claim_ids=None,
    requirements=None,
):
    return fx["controller"].draft_decision_generic_dependency_accounting(
        accounting_id=accounting_id,
        retrieval_scope_id=(
            retrieval_scope_id
            if retrieval_scope_id is not None
            else fx["snapshot"].scope_id
        ),
        claim_ids=claim_ids if claim_ids is not None else ["c1"],
        selected_support_map=(
            selected_support_map
            if selected_support_map is not None
            else fx["selected_map"]
        ),
        generic_dependency_node=node,
        evidence_ids=evidence_ids,
        reason=f"Negative control {accounting_id}.",
        text=fx["text"],
        evidence=fx["decision_evidence"],
        claim_identity_map=fx["claim_map"],
        as_of=ASOF,
        requirements=(
            requirements
            if requirements is not None
            else fx["requirements"]
        ),
    )


def _attestation(fx, draft, *, commitment=None, authority_id=None):
    c = fx["controller"]
    expected = c.decision_generic_dependency_accounting_commitment(
        draft,
        fx["decision_evidence"],
    )
    return DecisionGenericDependencyAccountingAttestation(
        f"att:{draft.accounting_id}",
        authority_id or DECISION_AUTHORITY,
        commitment or expected,
        ASOF,
        VALID_FROM,
        VALID_TO,
    )


def _install(
    fx,
    draft,
    attestation,
    *,
    verifier=None,
    text=None,
    requirements=None,
    claim_map=None,
):
    return fx["controller"].install_verified_decision_generic_dependency_accounting(
        draft,
        fx["decision_evidence"],
        attestation,
        verifier or fx["verifier"],
        text=text if text is not None else fx["text"],
        claim_identity_map=claim_map if claim_map is not None else fx["claim_map"],
        as_of=ASOF,
        requirements=(
            requirements
            if requirements is not None
            else fx["requirements"]
        ),
    )


def _finalize(fx, *, text=None, requirements=None, claim_map=None):
    return fx["controller"].finalize_verified_decision_dependency_accountings_for_prepare(
        text if text is not None else fx["text"],
        fx["decision_evidence"],
        claim_map if claim_map is not None else fx["claim_map"],
        as_of=ASOF,
        retrieval_scope=fx["snapshot"].scope_id,
        requirements=(
            requirements
            if requirements is not None
            else fx["requirements"]
        ),
    )


def _capture(fn):
    try:
        value = fn()
        return {
            "succeeded": True,
            "error": None,
            "value_type": type(value).__name__,
            "value": repr(value),
        }
    except Exception as exc:
        return {
            "succeeded": False,
            "error": f"{type(exc).__name__}: {exc}",
            "value_type": None,
            "value": None,
        }


def _registry_state(accounting_id):
    row = frozen_engine.SUPPORT_SELECTION_REGISTRY.get(accounting_id)
    if not isinstance(row, dict):
        return None
    return {
        "record_type": row.get("record_type"),
        "binding_state": row.get("binding_state"),
        "selected_support_map": row.get("selected_support_map"),
        "generic_dependency_node": row.get("generic_dependency_node"),
        "evidence_ids": row.get("evidence_ids"),
    }


def run_control(control_id: str) -> dict:
    fx = _fixture(
        control_id,
        include_extra_record=(
            control_id
            in {
                "NEG_CORRECT_NODE_WRONG_ENDPOINT_SET",
                "NEG_NONSEL_ENDPOINT_OUTSIDE_EVALUATED_SNAPSHOT",
            }
        ),
        extra_in_snapshot=False,
    )
    exact = fx["exact_obligation"]
    node = tuple(exact["generic_dependency_node"])
    eids = list(exact["evidence_ids"])
    accounting_id = f"acct:{control_id.lower()}"

    result = {
        "id": control_id,
        "target": "REJECT_OR_NONAUTHORIZE",
        "baseline": {
            "claim_state": (
                fx["baseline"].claims[0].get("status")
                if fx["baseline"].claims
                else None
            ),
            "control_closure": bool(fx["baseline"].control_closure),
            "false_gates": sorted(
                k for k, v in fx["baseline"].gates.items() if not v
            ),
        },
        "exact_obligation": {
            "node": list(node),
            "evidence_ids": eids,
            "selected_support_map": fx["selected_map"],
        },
        "stages": {},
        "frozen_outcome": None,
        "masked_by_current_guard": False,
    }

    if control_id == "NEG_WRONG_NODE_CORRECT_ENDPOINTS":
        wrong_node = ("DEPENDENCY", "model", "not-the-required-node")
        result["stages"]["draft"] = _capture(
            lambda: _draft(
                fx,
                accounting_id=accounting_id,
                node=wrong_node,
                evidence_ids=eids,
            )
        )
        result["masked_by_current_guard"] = True

    elif control_id == "NEG_CORRECT_NODE_WRONG_ENDPOINT_SET":
        wrong_eids = [eids[0], fx["extra"]["evidence_id"]]
        result["stages"]["draft"] = _capture(
            lambda: _draft(
                fx,
                accounting_id=accounting_id,
                node=node,
                evidence_ids=wrong_eids,
                selected_support_map=_expanded_selected_map(fx, wrong_eids),
            )
        )

    elif control_id == "NEG_NONSEL_ENDPOINT_OUTSIDE_EVALUATED_SNAPSHOT":
        outside_eid = fx["extra"]["evidence_id"]
        result["stages"]["draft"] = _capture(
            lambda: _draft(
                fx,
                accounting_id=accounting_id,
                node=node,
                evidence_ids=[eids[0], outside_eid],
            )
        )
        result["masked_by_current_guard"] = True

    elif control_id == "NEG_NONSEL_ENDPOINT_WITHOUT_REQUIRED_OBLIGATION":
        result["stages"]["draft"] = _capture(
            lambda: _draft(
                fx,
                accounting_id=accounting_id,
                node=("DEPENDENCY", "runtime", "unrelated"),
                evidence_ids=eids,
            )
        )
        result["masked_by_current_guard"] = True

    elif control_id == "NEG_WRONG_SELECTED_SUPPORT_MAP":
        expanded = _expanded_selected_map(fx, eids)
        holder = {}
        result["stages"]["draft"] = _capture(
            lambda: holder.setdefault(
                "draft",
                _draft(
                    fx,
                    accounting_id=accounting_id,
                    node=node,
                    evidence_ids=eids,
                    selected_support_map=expanded,
                ),
            )
        )
        if "draft" in holder:
            att = _attestation(fx, holder["draft"])
            result["stages"]["install"] = _capture(
                lambda: _install(fx, holder["draft"], att)
            )
            result["stages"]["finalize"] = _capture(lambda: _finalize(fx))
            result["registry"] = _registry_state(accounting_id)

    elif control_id == "NEG_WRONG_RETRIEVAL_SCOPE_OR_SNAPSHOT":
        expanded = _expanded_selected_map(fx, eids)
        result["stages"]["draft"] = _capture(
            lambda: _draft(
                fx,
                accounting_id=accounting_id,
                node=node,
                evidence_ids=eids,
                selected_support_map=expanded,
                retrieval_scope_id="scope:negative:unknown",
            )
        )

    elif control_id == "NEG_WRONG_CLAIM_SET_OR_REQUIREMENTS":
        expanded = _expanded_selected_map(fx, eids)
        holder = {}
        result["stages"]["draft"] = _capture(
            lambda: holder.setdefault(
                "draft",
                _draft(
                    fx,
                    accounting_id=accounting_id,
                    node=node,
                    evidence_ids=eids,
                    selected_support_map=expanded,
                ),
            )
        )
        if "draft" in holder:
            att = _attestation(fx, holder["draft"])
            wrong_req = {"c1": {"required_independent_supports": 2}}
            result["stages"]["install_wrong_requirements"] = _capture(
                lambda: _install(
                    fx,
                    holder["draft"],
                    att,
                    requirements=wrong_req,
                )
            )

    elif control_id == "NEG_STALE_DECISION_CONTEXT_COMMITMENT":
        expanded = _expanded_selected_map(fx, eids)
        holder = {}
        result["stages"]["draft"] = _capture(
            lambda: holder.setdefault(
                "draft",
                _draft(
                    fx,
                    accounting_id=accounting_id,
                    node=node,
                    evidence_ids=eids,
                    selected_support_map=expanded,
                ),
            )
        )
        if "draft" in holder:
            att = _attestation(fx, holder["draft"])
            result["stages"]["install_changed_text"] = _capture(
                lambda: _install(
                    fx,
                    holder["draft"],
                    att,
                    text="DemoSubject is unsafe.",
                )
            )

    elif control_id == "NEG_SOURCE_SEMANTIC_NODE_IN_GENERIC_CHANNEL":
        expanded = _expanded_selected_map(fx, eids)
        holder = {}
        source_node = ("SOURCE", "repository", "repo:negative")
        result["stages"]["draft"] = _capture(
            lambda: holder.setdefault(
                "draft",
                _draft(
                    fx,
                    accounting_id=accounting_id,
                    node=source_node,
                    evidence_ids=eids,
                    selected_support_map=expanded,
                ),
            )
        )
        if "draft" in holder:
            att = _attestation(fx, holder["draft"])
            result["stages"]["install"] = _capture(
                lambda: _install(fx, holder["draft"], att)
            )
            result["stages"]["finalize"] = _capture(lambda: _finalize(fx))
            result["registry"] = _registry_state(accounting_id)

    elif control_id == "NEG_INVALID_NODE_ARITY_TYPE_OR_BLANK_IDENTIFIER":
        result["stages"]["draft"] = _capture(
            lambda: _draft(
                fx,
                accounting_id=accounting_id,
                node=("DEPENDENCY", "data_source", ""),
                evidence_ids=eids,
                selected_support_map=_expanded_selected_map(fx, eids),
            )
        )

    elif control_id == "NEG_UNVERIFIED_OR_MISMATCHED_EXTERNAL_ATTESTATION":
        expanded = _expanded_selected_map(fx, eids)
        holder = {}
        result["stages"]["draft"] = _capture(
            lambda: holder.setdefault(
                "draft",
                _draft(
                    fx,
                    accounting_id=accounting_id,
                    node=node,
                    evidence_ids=eids,
                    selected_support_map=expanded,
                ),
            )
        )
        if "draft" in holder:
            bad_att = _attestation(
                fx,
                holder["draft"],
                commitment="not-the-accounting-commitment",
            )
            result["stages"]["install_bad_attestation"] = _capture(
                lambda: _install(fx, holder["draft"], bad_att)
            )

    elif control_id == "NEG_ACCOUNTING_FAILS_EXACT_FRESH_UNIVERSE_BIND":
        expanded = _expanded_selected_map(fx, eids)
        holder = {}
        wrong_node = ("DEPENDENCY", "model", "not-the-required-node")
        result["stages"]["draft"] = _capture(
            lambda: holder.setdefault(
                "draft",
                _draft(
                    fx,
                    accounting_id=accounting_id,
                    node=wrong_node,
                    evidence_ids=eids,
                    selected_support_map=expanded,
                ),
            )
        )
        if "draft" in holder:
            att = _attestation(fx, holder["draft"])
            result["stages"]["install"] = _capture(
                lambda: _install(fx, holder["draft"], att)
            )
            result["stages"]["finalize"] = _capture(lambda: _finalize(fx))
            result["registry"] = _registry_state(accounting_id)

    stages = result["stages"]
    any_reject = any(
        not stage.get("succeeded", False)
        for stage in stages.values()
    )
    registry = result.get("registry")
    bound = isinstance(registry, dict) and registry.get("binding_state") == "BOUND"

    if any_reject:
        result["frozen_outcome"] = "REJECTED_OR_STOPPED_FAIL_CLOSED"
    elif not bound:
        result["frozen_outcome"] = "ACCEPTED_EARLY_BUT_NONAUTHORIZING"
    else:
        result["frozen_outcome"] = "UNEXPECTED_BOUND_AUTHORIZATION_PATH"

    result["passes_negative_contract"] = (
        result["frozen_outcome"]
        != "UNEXPECTED_BOUND_AUTHORIZATION_PATH"
    )
    return result


def run_isolated(control_id: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_cfc_next_negative_control_baseline",
            "--single-control",
            control_id,
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"{control_id}: {cp.stderr.strip() or cp.stdout.strip()}"
        )
    return json.loads(cp.stdout)


def main():
    manifest = json.loads(
        Path("research/cfc_next_accounting_acceptance_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    manifest_ids = tuple(row["id"] for row in manifest["negative_controls"])
    assert manifest_ids == NEGATIVE_IDS

    rows = [run_isolated(control_id) for control_id in NEGATIVE_IDS]
    assert all(row["passes_negative_contract"] for row in rows)

    unexpected = [
        row["id"]
        for row in rows
        if row["frozen_outcome"] == "UNEXPECTED_BOUND_AUTHORIZATION_PATH"
    ]
    assert unexpected == []

    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "CFC_NEXT_NEGATIVE_CONTROL_FROZEN_BASELINE",
        "control_count": len(rows),
        "all_reject_or_nonauthorize": True,
        "unexpected_bound_authorization_paths": unexpected,
        "masked_by_current_selected_support_guard": [
            row["id"]
            for row in rows
            if row.get("masked_by_current_guard")
        ],
        "rows": rows,
        "status": "PASS",
        "interpretation_boundary": (
            "This is a frozen-reference fail-closed baseline. Some controls are "
            "rejected by the current selected-support-only public guard before "
            "their future CFC-next exact-obligation condition can be exercised. "
            "Those cases are explicitly marked masked_by_current_guard and must "
            "be re-executed against a CFC-next candidate after Repair B."
        ),
    }

    Path("cfc_next_negative_control_baseline.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-control", choices=NEGATIVE_IDS)
    args = parser.parse_args()
    if args.single_control:
        print(json.dumps(run_control(args.single_control), sort_keys=True))
    else:
        main()
