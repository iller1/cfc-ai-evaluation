from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from cfc_next_candidate_0_3_0a2 import Controller
from cfc_anchor import (
    SourceSemanticsAuthorityAttestation,
    ProvenanceAuthorityAttestation,
    EvidenceAuthorityAttestation,
    EpistemicRoleAuthorityAttestation,
)

from demonstrator.custom_case_runner import ASOF, VALID_FROM, VALID_TO, STALE_TO
from research import review_minimal_blocker_accounting_taxonomy as taxonomy


REPRESENTATIVE_RELATIONS = (
    "root_origin_shared",
    "extractor_shared",
    "dependency:data_source",
)

NAMESPACE_MODES = (
    "GLOBAL_SHARED_RELATION_ID",
    "TENANT_NAMESPACED_RELATION_ID",
)

ORDER_MODES = (
    "A_ONLY",
    "B_ONLY",
    "A_THEN_B",
    "B_THEN_A",
)


def _build_record_namespaced(
    c: Controller,
    *,
    tag: str,
    tenant: str,
    identity_id: str,
    blocker: str,
    idx: int,
    validity: str,
) -> dict:
    """Keep the relation shared within a tenant, but not across tenants."""
    eid = f"E{idx}:{tag}"
    source_token = f"peer-isolation:{tag}:e{idx}"

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
        "referent_entity_id": "entity:demo-subject",
        "referent_event_id": "event:current",
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
        subject="DemoSubject",
        predicate="state",
        value="safe",
        source=f"display:{source_token}",
        identity_registry_entry_id=identity_id,
        authority_id="GENERAL_RECORD_V5",
        authority_record_entity_id="entity:demo-subject",
        authority_record_event_id="event:current",
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


def _build_context(
    blocker: str,
    tenant: str,
    namespace_mode: str,
) -> dict:
    tag = f"a2-peer-{tenant.lower()}-" + blocker.replace(":", "-")
    c = Controller(trust_policy=taxonomy._trust_policy())
    identity_id = taxonomy._install_identity(c, tag)
    taxonomy._install_topology(c, tag)

    builder = (
        taxonomy._build_record
        if namespace_mode == "GLOBAL_SHARED_RELATION_ID"
        else None
    )

    records = []
    for idx, validity in ((1, "CURRENT"), (2, "STALE")):
        if builder is not None:
            record = builder(
                c,
                tag=tag,
                identity_id=identity_id,
                blocker=blocker,
                idx=idx,
                validity=validity,
            )
        else:
            record = _build_record_namespaced(
                c,
                tag=tag,
                tenant=tenant,
                identity_id=identity_id,
                blocker=blocker,
                idx=idx,
                validity=validity,
            )
        records.append(record)

    snapshot = taxonomy._install_snapshot(
        c,
        tag=tag,
        label="evaluated",
        records=records,
    )

    text = "DemoSubject is safe."
    claim_map = {"c1": identity_id}
    requirements = {"c1": {"required_independent_supports": 1}}

    result = c.evaluate_snapshot(
        snapshot,
        text,
        records,
        claim_map,
        as_of=ASOF,
        requirements=requirements,
    )

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
        "tenant": tenant,
        "namespace_mode": namespace_mode,
        "controller": c,
        "identity_id": identity_id,
        "records": records,
        "snapshot": snapshot,
        "result": result,
        "signature": {
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
            "required_obligations": [
                {
                    "generic_dependency_node": list(
                        row.get("generic_dependency_node") or ()
                    ),
                    "evidence_ids": list(
                        row.get("evidence_ids") or ()
                    ),
                    "decision_level_required": row.get(
                        "decision_level_required"
                    ),
                }
                for row in required
            ],
            "selected_support_map": [
                [claim_id, list(evidence_ids)]
                for claim_id, evidence_ids
                in (graph.get("selected_support_map") or ())
            ],
        },
    }


def _capture_build(blocker: str, tenant: str, namespace_mode: str):
    try:
        ctx = _build_context(blocker, tenant, namespace_mode)
        return {
            "ok": True,
            "error": None,
            "signature": ctx["signature"],
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "signature": None,
        }


def run_scenario(
    blocker: str,
    namespace_mode: str,
    order_mode: str,
) -> dict:
    sequence = {
        "A_ONLY": ("A",),
        "B_ONLY": ("B",),
        "A_THEN_B": ("A", "B"),
        "B_THEN_A": ("B", "A"),
    }[order_mode]

    rows = []
    for tenant in sequence:
        rows.append({
            "tenant": tenant,
            **_capture_build(blocker, tenant, namespace_mode),
        })

    return {
        "blocker": blocker,
        "namespace_mode": namespace_mode,
        "order_mode": order_mode,
        "sequence": rows,
    }


def _run_isolated(
    blocker: str,
    namespace_mode: str,
    order_mode: str,
) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_cfc_next_0_3_0a2_peer_controller_isolation",
            "--single-blocker", blocker,
            "--namespace-mode", namespace_mode,
            "--order-mode", order_mode,
        ],
        capture_output=True,
        text=True,
        timeout=150,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"{blocker}/{namespace_mode}/{order_mode}: "
            f"{cp.stderr.strip() or cp.stdout.strip()}"
        )
    return json.loads(cp.stdout)


def _last_signature(row: dict):
    seq = row.get("sequence") or []
    if not seq:
        return None
    last = seq[-1]
    return last.get("signature") if last.get("ok") else None


def main():
    rows = [
        _run_isolated(blocker, namespace_mode, order_mode)
        for blocker in REPRESENTATIVE_RELATIONS
        for namespace_mode in NAMESPACE_MODES
        for order_mode in ORDER_MODES
    ]

    by_key = {
        (
            row["blocker"],
            row["namespace_mode"],
            row["order_mode"],
        ): row
        for row in rows
    }

    comparisons = []
    for blocker in REPRESENTATIVE_RELATIONS:
        for namespace_mode in NAMESPACE_MODES:
            a_only = _last_signature(
                by_key[(blocker, namespace_mode, "A_ONLY")]
            )
            b_only = _last_signature(
                by_key[(blocker, namespace_mode, "B_ONLY")]
            )
            a_then_b = _last_signature(
                by_key[(blocker, namespace_mode, "A_THEN_B")]
            )
            b_then_a = _last_signature(
                by_key[(blocker, namespace_mode, "B_THEN_A")]
            )

            comparisons.append({
                "blocker": blocker,
                "namespace_mode": namespace_mode,
                "a_changed_after_b": (
                    a_only is not None
                    and b_then_a is not None
                    and a_only != b_then_a
                ),
                "b_changed_after_a": (
                    b_only is not None
                    and a_then_b is not None
                    and b_only != a_then_b
                ),
                "a_only": a_only,
                "a_after_b": b_then_a,
                "b_only": b_only,
                "b_after_a": a_then_b,
            })

    global_interference = [
        row["blocker"]
        for row in comparisons
        if (
            row["namespace_mode"] == "GLOBAL_SHARED_RELATION_ID"
            and (
                row["a_changed_after_b"]
                or row["b_changed_after_a"]
            )
        )
    ]
    namespaced_interference = [
        row["blocker"]
        for row in comparisons
        if (
            row["namespace_mode"]
            == "TENANT_NAMESPACED_RELATION_ID"
            and (
                row["a_changed_after_b"]
                or row["b_changed_after_a"]
            )
        )
    ]

    scenario_errors = [
        {
            "blocker": row["blocker"],
            "namespace_mode": row["namespace_mode"],
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

    if namespaced_interference:
        classification = (
            "PEER_CONTROLLER_CONTEXT_ISOLATION_FINDING"
        )
    elif global_interference:
        classification = (
            "SHARED_RELATION_ID_CROSS_CONTEXT_INTERFERENCE"
        )
    elif scenario_errors:
        classification = "PEER_DIAGNOSTIC_BUILD_ERROR"
    else:
        classification = "PEER_CONTEXT_CONSTRUCTION_ISOLATION_PASS"

    result = {
        "test": "CFC_NEXT_0_3_0A2_PEER_CONTEXT_DIAGNOSTIC",
        "candidate_version": "0.3.0a2",
        "relations_tested": list(REPRESENTATIVE_RELATIONS),
        "namespace_modes": list(NAMESPACE_MODES),
        "order_modes": list(ORDER_MODES),
        "scenario_count": len(rows),
        "global_shared_relation_id_interference": sorted(
            set(global_interference)
        ),
        "tenant_namespaced_relation_id_interference": sorted(
            set(namespaced_interference)
        ),
        "scenario_errors": scenario_errors,
        "classification": classification,
        "accounting_authorization_installed": False,
        "frozen_candidate_modified": False,
        "frozen_reference_modified": False,
        "historical_rescore_performed": False,
        "comparisons": comparisons,
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
        "--single-blocker",
        choices=REPRESENTATIVE_RELATIONS,
    )
    parser.add_argument(
        "--namespace-mode",
        choices=NAMESPACE_MODES,
    )
    parser.add_argument(
        "--order-mode",
        choices=ORDER_MODES,
    )
    args = parser.parse_args()

    supplied = (
        args.single_blocker,
        args.namespace_mode,
        args.order_mode,
    )
    if any(supplied):
        if not all(supplied):
            raise SystemExit(
                "--single-blocker, --namespace-mode and "
                "--order-mode must be used together"
            )
        print(json.dumps(
            run_scenario(
                args.single_blocker,
                args.namespace_mode,
                args.order_mode,
            ),
            sort_keys=True,
        ))
    else:
        main()
