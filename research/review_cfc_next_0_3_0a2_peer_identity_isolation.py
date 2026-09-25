from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from cfc_next_candidate_0_3_0a2 import Controller
from cfc_anchor import (
    IdentityAuthorityAttestation,
    SourceSemanticsAuthorityAttestation,
    ProvenanceAuthorityAttestation,
    EvidenceAuthorityAttestation,
    EpistemicRoleAuthorityAttestation,
)

from demonstrator.custom_case_runner import ASOF, VALID_FROM, VALID_TO, STALE_TO
from research import review_minimal_blocker_accounting_taxonomy as taxonomy
from research.review_cfc_next_0_3_0a2_peer_controller_isolation import (
    RELATIONS,
    _build_context,
)


IDENTITY_MODES = (
    "SHARED_CANONICAL_IDENTITY",
    "TENANT_NAMESPACED_CANONICAL_IDENTITY",
)

ORDER_MODES = (
    "A_ONLY",
    "B_ONLY",
    "A_THEN_B",
    "B_THEN_A",
)


def _install_identity_namespaced(c: Controller, tag: str, tenant: str):
    surface_subject = f"DemoSubject{tenant}"
    entity_id = f"entity:demo-subject:{tenant}"
    event_id = f"event:current:{tenant}"
    identity_id = f"id:peer-isolation:{tag}:subject:v1"
    identity = c.draft_identity(
        registry_entry_id=identity_id,
        surface_subject=surface_subject,
        domain_id="GENERAL_ENTITY",
        entity_id=entity_id,
        event_id=event_id,
        version_id="v1",
    )
    c.install_verified_identity(
        identity,
        IdentityAuthorityAttestation(
            f"att:peer-isolation:{tag}:identity",
            taxonomy.AUTHORITIES["IDENTITY"],
            c.identity_commitment(identity),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        taxonomy.VERIFIERS["IDENTITY"],
        as_of=ASOF,
    )
    return {
        "identity_id": identity_id,
        "surface_subject": surface_subject,
        "entity_id": entity_id,
        "event_id": event_id,
    }


def _build_record(
    c: Controller,
    *,
    tag: str,
    tenant: str,
    identity: dict,
    blocker: str,
    idx: int,
    validity: str,
) -> dict:
    eid = f"E{idx}:{tag}"
    source_token = f"peer-identity:{tag}:e{idx}"

    sem_id = f"sem:{source_token}"
    semantics = c.draft_source_semantics(
        semantics_registry_entry_id=sem_id,
        source_id=f"general-record:{source_token}",
        repository_id=f"repo:iso:{tag}:e{idx}",
        producer_id=f"producer:iso:{tag}:e{idx}",
        process_id=f"process:iso:{tag}:e{idx}",
        failure_domain_id=f"fd:iso:{tag}:e{idx}",
        resolution_state="KNOWN",
    )
    c.install_verified_source_semantics(
        semantics,
        SourceSemanticsAuthorityAttestation(
            f"att:{source_token}:semantics",
            taxonomy.AUTHORITIES["SOURCE_SEMANTICS"],
            c.source_semantics_commitment(semantics),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        taxonomy.VERIFIERS["SOURCE_SEMANTICS"],
        as_of=ASOF,
    )

    root_origin_id = (
        f"general-record:root:shared:{tenant}"
        if blocker == "root_origin_shared"
        else f"general-record:root:iso:{tag}:e{idx}"
    )
    origin_id = (
        f"general-record:origin:shared:{tenant}"
        if blocker == "origin_shared"
        else f"general-record:origin:iso:{tag}:e{idx}"
    )
    extractor_id = (
        f"extractor:shared:{tenant}"
        if blocker == "extractor_shared"
        else f"extractor:iso:{tag}:e{idx}"
    )
    common_mode_group = (
        f"group:shared:{tenant}"
        if blocker == taxonomy.COMMON_MODE_BLOCKER
        else f"group:iso:{tag}:e{idx}"
    )
    dependencies = {}
    for key in taxonomy.DEPENDENCY_KEYS:
        prefix = taxonomy.DEPENDENCY_PREFIX[key]
        dep_id = (
            f"{prefix}:shared:{tenant}:{key}"
            if blocker == f"dependency:{key}"
            else f"{prefix}:iso:{tag}:e{idx}:{key}"
        )
        dependencies[key] = {"state": "KNOWN", "id": dep_id}

    provenance = {
        "source_id": f"general-record:{source_token}",
        "root_origin_id": root_origin_id,
        "origin_id": origin_id,
        "referent_entity_id": identity["entity_id"],
        "referent_event_id": identity["event_id"],
        "referent_version_id": "v1",
        "extractor_id": extractor_id,
        "common_mode_group": common_mode_group,
        "lineage": [root_origin_id, origin_id],
        "dependencies": dependencies,
    }

    observed_at = "2026-08-30" if validity == "STALE" else ASOF
    valid_to = STALE_TO if validity == "STALE" else VALID_TO

    evidence = c.draft_evidence_record(
        evidence_id=eid,
        subject=identity["surface_subject"],
        predicate="state",
        value="safe",
        source=f"display:{source_token}",
        identity_registry_entry_id=identity["identity_id"],
        authority_id="GENERAL_RECORD_V5",
        authority_record_entity_id=identity["entity_id"],
        authority_record_event_id=identity["event_id"],
        authority_record_version_id="v1",
        valid_from=VALID_FROM,
        valid_to=valid_to,
        observed_at=observed_at,
        available_at=observed_at,
        provenance=provenance,
        polarity="POSITIVE",
        source_semantics_id=sem_id,
    )
    c.verify_evidence_provenance(
        evidence,
        ProvenanceAuthorityAttestation(
            f"att:{source_token}:prov",
            taxonomy.AUTHORITIES["PROVENANCE"],
            eid,
            c.provenance_commitment(evidence),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        taxonomy.VERIFIERS["PROVENANCE"],
        as_of=ASOF,
    )
    c.verify_evidence_authority(
        evidence,
        EvidenceAuthorityAttestation(
            f"att:{source_token}:evidence",
            taxonomy.AUTHORITIES["EVIDENCE_AUTHORITY"],
            eid,
            "GENERAL_RECORD_V5",
            c.evidence_authority_commitment(evidence),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        taxonomy.VERIFIERS["EVIDENCE_AUTHORITY"],
        as_of=ASOF,
    )
    role = c.draft_epistemic_role(
        evidence,
        epistemic_role="DIRECT_WORLD_RECORD",
    )
    role_installation = c.install_verified_epistemic_role(
        evidence,
        role,
        EpistemicRoleAuthorityAttestation(
            f"att:{source_token}:role",
            taxonomy.AUTHORITIES["EPISTEMIC_ROLE"],
            eid,
            "DIRECT_WORLD_RECORD",
            role.role_commitment,
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        taxonomy.VERIFIERS["EPISTEMIC_ROLE"],
        as_of=ASOF,
    )
    evidence = c.evidence_with_epistemic_role(
        evidence,
        role_installation,
    )
    return c.evidence_record_mapping(evidence)


def _build_namespaced_context(blocker: str, tenant: str):
    tag = f"a2-peer-identity-{tenant.lower()}-" + blocker.replace(":", "-")
    c = Controller(trust_policy=taxonomy._trust_policy())
    identity = _install_identity_namespaced(c, tag, tenant)
    taxonomy._install_topology(c, tag)

    records = [
        _build_record(
            c,
            tag=tag,
            tenant=tenant,
            identity=identity,
            blocker=blocker,
            idx=1,
            validity="CURRENT",
        ),
        _build_record(
            c,
            tag=tag,
            tenant=tenant,
            identity=identity,
            blocker=blocker,
            idx=2,
            validity="STALE",
        ),
    ]
    snapshot = taxonomy._install_snapshot(
        c,
        tag=tag,
        label="evaluated",
        records=records,
    )
    text = f"{identity['surface_subject']} is safe."
    claim_map = {"c1": identity["identity_id"]}
    requirements = {"c1": {"required_independent_supports": 1}}
    result = c.evaluate_snapshot(
        snapshot,
        text,
        records,
        claim_map,
        as_of=ASOF,
        requirements=requirements,
    )
    return _signature(result)


def _signature(result):
    assessments = result.raw.get(
        "decision_level_generic_dependency_assessments",
        (),
    )
    required = [
        row for row in assessments
        if isinstance(row, dict)
        and row.get("decision_level_required")
    ]
    graph = result.raw.get("decision_support_dependency_graph") or {}
    return {
        "claim_state": (
            result.claims[0].get("status")
            if result.claims else None
        ),
        "control_closure": bool(result.control_closure),
        "decision_support_closure_valid": bool(
            result.gates.get("decision_support_closure_valid")
        ),
        "false_gates": sorted(
            key for key, value in result.gates.items()
            if not value
        ),
        "required_obligation_count": len(required),
        "selected_support_map": [
            [claim_id, list(evidence_ids)]
            for claim_id, evidence_ids
            in (graph.get("selected_support_map") or ())
        ],
    }


def _build(blocker: str, tenant: str, identity_mode: str):
    if identity_mode == "SHARED_CANONICAL_IDENTITY":
        ctx = _build_context(
            blocker,
            tenant,
            "TENANT_NAMESPACED_RELATION_ID",
        )
        return ctx["signature"]
    return _build_namespaced_context(blocker, tenant)


def _capture(blocker: str, tenant: str, identity_mode: str):
    try:
        return {
            "ok": True,
            "error": None,
            "signature": _build(blocker, tenant, identity_mode),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "signature": None,
        }


def run_scenario(blocker: str, identity_mode: str, order_mode: str):
    sequence = {
        "A_ONLY": ("A",),
        "B_ONLY": ("B",),
        "A_THEN_B": ("A", "B"),
        "B_THEN_A": ("B", "A"),
    }[order_mode]
    return {
        "blocker": blocker,
        "identity_mode": identity_mode,
        "order_mode": order_mode,
        "sequence": [
            {
                "tenant": tenant,
                **_capture(blocker, tenant, identity_mode),
            }
            for tenant in sequence
        ],
    }


def _run_isolated(blocker: str, identity_mode: str, order_mode: str):
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_cfc_next_0_3_0a2_peer_identity_isolation",
            "--single-blocker", blocker,
            "--identity-mode", identity_mode,
            "--order-mode", order_mode,
        ],
        capture_output=True,
        text=True,
        timeout=150,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"{blocker}/{identity_mode}/{order_mode}: "
            f"{cp.stderr.strip() or cp.stdout.strip()}"
        )
    return json.loads(cp.stdout)


def _last_signature(row):
    seq = row.get("sequence") or []
    if not seq:
        return None
    last = seq[-1]
    return last.get("signature") if last.get("ok") else None


def main():
    rows = [
        _run_isolated(blocker, identity_mode, order_mode)
        for blocker in RELATIONS
        for identity_mode in IDENTITY_MODES
        for order_mode in ORDER_MODES
    ]
    by_key = {
        (row["blocker"], row["identity_mode"], row["order_mode"]): row
        for row in rows
    }

    comparisons = []
    for blocker in RELATIONS:
        for identity_mode in IDENTITY_MODES:
            a_only = _last_signature(
                by_key[(blocker, identity_mode, "A_ONLY")]
            )
            b_only = _last_signature(
                by_key[(blocker, identity_mode, "B_ONLY")]
            )
            a_after_b = _last_signature(
                by_key[(blocker, identity_mode, "B_THEN_A")]
            )
            b_after_a = _last_signature(
                by_key[(blocker, identity_mode, "A_THEN_B")]
            )
            comparisons.append({
                "blocker": blocker,
                "identity_mode": identity_mode,
                "a_changed_after_b": (
                    a_only is not None
                    and a_after_b is not None
                    and a_only != a_after_b
                ),
                "b_changed_after_a": (
                    b_only is not None
                    and b_after_a is not None
                    and b_only != b_after_a
                ),
                "a_only": a_only,
                "a_after_b": a_after_b,
                "b_only": b_only,
                "b_after_a": b_after_a,
            })

    shared_identity_interference = sorted(set(
        row["blocker"]
        for row in comparisons
        if (
            row["identity_mode"] == "SHARED_CANONICAL_IDENTITY"
            and (row["a_changed_after_b"] or row["b_changed_after_a"])
        )
    ))
    namespaced_identity_interference = sorted(set(
        row["blocker"]
        for row in comparisons
        if (
            row["identity_mode"]
            == "TENANT_NAMESPACED_CANONICAL_IDENTITY"
            and (row["a_changed_after_b"] or row["b_changed_after_a"])
        )
    ))

    errors = [
        {
            "blocker": row["blocker"],
            "identity_mode": row["identity_mode"],
            "order_mode": row["order_mode"],
            "errors": [
                item["error"]
                for item in row["sequence"]
                if not item["ok"]
            ],
        }
        for row in rows
        if any(not item["ok"] for item in row["sequence"])
    ]

    if namespaced_identity_interference:
        classification = "PEER_CONTEXT_INTERFERENCE_BEYOND_IDENTITY"
    elif shared_identity_interference:
        classification = "SHARED_CANONICAL_IDENTITY_CROSS_CONTEXT_INTERFERENCE"
    elif errors:
        classification = "PEER_IDENTITY_DIAGNOSTIC_BUILD_ERROR"
    else:
        classification = "PEER_CANONICAL_IDENTITY_ISOLATION_PASS"

    result = {
        "test": "CFC_NEXT_0_3_0A2_PEER_IDENTITY_ISOLATION",
        "candidate_version": "0.3.0a2",
        "relations_tested": list(RELATIONS),
        "identity_modes": list(IDENTITY_MODES),
        "order_modes": list(ORDER_MODES),
        "scenario_count": len(rows),
        "shared_canonical_identity_interference": (
            shared_identity_interference
        ),
        "tenant_namespaced_canonical_identity_interference": (
            namespaced_identity_interference
        ),
        "scenario_errors": errors,
        "classification": classification,
        "accounting_authorization_installed": False,
        "frozen_candidate_modified": False,
        "frozen_reference_modified": False,
        "historical_rescore_performed": False,
        "comparisons": comparisons,
        "rows": rows,
    }
    Path(
        "cfc_next_0_3_0a2_peer_identity_isolation.json"
    ).write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--single-blocker",
        choices=RELATIONS,
    )
    parser.add_argument(
        "--identity-mode",
        choices=IDENTITY_MODES,
    )
    parser.add_argument(
        "--order-mode",
        choices=ORDER_MODES,
    )
    args = parser.parse_args()
    supplied = (
        args.single_blocker,
        args.identity_mode,
        args.order_mode,
    )
    if any(supplied):
        if not all(supplied):
            raise SystemExit(
                "--single-blocker, --identity-mode and --order-mode "
                "must be used together"
            )
        print(json.dumps(
            run_scenario(
                args.single_blocker,
                args.identity_mode,
                args.order_mode,
            ),
            sort_keys=True,
        ))
    else:
        main()
