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
    IdentityAuthorityAttestation,
    SourceSemanticsAuthorityAttestation,
    ProvenanceAuthorityAttestation,
    EvidenceAuthorityAttestation,
    EpistemicRoleAuthorityAttestation,
    RetrievalAuthorityAttestation,
    FailureDomainTopologyAttestation,
)
from demonstrator.custom_case_runner import (
    ASOF,
    VALID_FROM,
    VALID_TO,
    STALE_TO,
    AUTHORITIES,
    VERIFIERS,
)

RELATION_MODES = (
    "DISTINCT",
    "COMMON_MODE",
    "ROOT_ORIGIN",
    "GENERIC_DEPENDENCY",
)
PLACEMENT_MODES = (
    "EVALUATED_SNAPSHOT",
    "OTHER_SNAPSHOT",
    "VERIFIED_ONLY",
)

DEPENDENCY_PREFIX = {
    "data_source": "data",
    "sensor_input": "sensor",
    "transform": "transform",
    "model": "model",
    "extractor": "extractor",
    "cache": "cache",
    "upstream_db": "db",
    "operator": "operator",
    "preprocessing": "prep",
    "runtime": "runtime",
}


def _trust_policy() -> HostTrustPolicy:
    return HostTrustPolicy(
        tuple(
            HostTrustRegistration(kind, AUTHORITIES[kind], VERIFIERS[kind])
            for kind in AUTHORITIES
            if kind != "SUPPORT_SET_INDEPENDENCE"
        )
    )


def _install_identity(c: Controller, tag: str) -> str:
    identity_id = f"id:snapshot-locality:{tag}:subject:v1"
    identity = c.draft_identity(
        registry_entry_id=identity_id,
        surface_subject="DemoSubject",
        domain_id="GENERAL_ENTITY",
        entity_id="entity:demo-subject",
        event_id="event:current",
        version_id="v1",
    )
    c.install_verified_identity(
        identity,
        IdentityAuthorityAttestation(
            f"att:snapshot-locality:{tag}:identity",
            AUTHORITIES["IDENTITY"],
            c.identity_commitment(identity),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["IDENTITY"],
        as_of=ASOF,
    )
    return identity_id


def _install_topology(c: Controller, tag: str) -> None:
    topology = c.draft_failure_domain_topology()
    c.install_verified_failure_domain_topology(
        topology,
        FailureDomainTopologyAttestation(
            f"att:snapshot-locality:{tag}:topology",
            AUTHORITIES["FAILURE_DOMAIN_TOPOLOGY"],
            c.failure_domain_topology_commitment(topology),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["FAILURE_DOMAIN_TOPOLOGY"],
        as_of=ASOF,
    )


def _build_record(
    c: Controller,
    *,
    tag: str,
    identity_id: str,
    relation_mode: str,
    idx: int,
    validity: str,
) -> dict:
    eid = f"E{idx}:{tag}"
    source_token = f"snapshot-locality:{tag}:e{idx}"

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
            AUTHORITIES["SOURCE_SEMANTICS"],
            c.source_semantics_commitment(semantics),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["SOURCE_SEMANTICS"],
        as_of=ASOF,
    )

    root_origin_id = (
        "general-record:root:shared"
        if relation_mode == "ROOT_ORIGIN"
        else f"general-record:root:{tag}:e{idx}"
    )
    origin_id = f"general-record:origin:{tag}:e{idx}"
    common_mode_group = (
        "group:shared"
        if relation_mode == "COMMON_MODE"
        else f"group:iso:{tag}:e{idx}"
    )

    dependencies = {}
    for key, prefix in DEPENDENCY_PREFIX.items():
        dep_id = (
            "data:shared"
            if relation_mode == "GENERIC_DEPENDENCY" and key == "data_source"
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
        "extractor_id": f"extractor:iso:{tag}:e{idx}",
        "common_mode_group": common_mode_group,
        "lineage": [root_origin_id, origin_id],
        "dependencies": dependencies,
    }

    valid_to = STALE_TO if validity == "STALE" else VALID_TO
    observed_at = "2026-08-30" if validity == "STALE" else ASOF

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
            AUTHORITIES["PROVENANCE"],
            eid,
            c.provenance_commitment(evidence),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["PROVENANCE"],
        as_of=ASOF,
    )
    c.verify_evidence_authority(
        evidence,
        EvidenceAuthorityAttestation(
            f"att:{source_token}:evidence",
            AUTHORITIES["EVIDENCE_AUTHORITY"],
            eid,
            "GENERAL_RECORD_V5",
            c.evidence_authority_commitment(evidence),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["EVIDENCE_AUTHORITY"],
        as_of=ASOF,
    )
    role = c.draft_epistemic_role(
        evidence, epistemic_role="DIRECT_WORLD_RECORD"
    )
    role_installation = c.install_verified_epistemic_role(
        evidence,
        role,
        EpistemicRoleAuthorityAttestation(
            f"att:{source_token}:role",
            AUTHORITIES["EPISTEMIC_ROLE"],
            eid,
            "DIRECT_WORLD_RECORD",
            role.role_commitment,
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["EPISTEMIC_ROLE"],
        as_of=ASOF,
    )
    evidence = c.evidence_with_epistemic_role(evidence, role_installation)
    return c.evidence_record_mapping(evidence)


def _install_snapshot(
    c: Controller,
    *,
    tag: str,
    label: str,
    records: list[dict],
) -> object:
    scope_id = f"scope:snapshot-locality:{tag}:{label}"
    snapshot = c.draft_snapshot(
        records,
        scope_id=scope_id,
        snapshot_id=f"snapshot:snapshot-locality:{tag}:{label}",
        snapshot_created_at=ASOF,
        snapshot_available_at=ASOF,
        valid_from=VALID_FROM,
        valid_to=VALID_TO,
    )
    c.install_verified_snapshot(
        snapshot,
        records,
        RetrievalAuthorityAttestation(
            f"att:snapshot-locality:{tag}:{label}:retrieval",
            AUTHORITIES["RETRIEVAL"],
            c.snapshot_commitment(snapshot),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["RETRIEVAL"],
        as_of=ASOF,
    )
    return snapshot


def build_case(relation_mode: str, placement_mode: str) -> dict:
    tag = f"{relation_mode.lower()}:{placement_mode.lower()}"
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

    if placement_mode == "EVALUATED_SNAPSHOT":
        eval_records = [e1, e2]
        eval_snapshot = _install_snapshot(
            c, tag=tag, label="evaluated", records=eval_records
        )
    elif placement_mode == "OTHER_SNAPSHOT":
        _install_snapshot(c, tag=tag, label="other", records=[e2])
        eval_records = [e1]
        eval_snapshot = _install_snapshot(
            c, tag=tag, label="evaluated", records=eval_records
        )
    elif placement_mode == "VERIFIED_ONLY":
        eval_records = [e1]
        eval_snapshot = _install_snapshot(
            c, tag=tag, label="evaluated", records=eval_records
        )
    else:
        raise ValueError(placement_mode)

    result = c.evaluate_snapshot(
        eval_snapshot,
        "DemoSubject is safe.",
        eval_records,
        {"c1": identity_id},
        as_of=ASOF,
        requirements={"c1": {"required_independent_supports": 1}},
    )

    claim = result.claims[0] if result.claims else {}
    return {
        "relation_mode": relation_mode,
        "placement_mode": placement_mode,
        "evaluated_record_ids": [r.get("evidence_id") for r in eval_records],
        "claim_state": claim.get("status"),
        "claim_reason": claim.get("reason"),
        "claim_record": claim,
        "stop_type": result.stop_type,
        "control_closure": bool(result.control_closure),
        "gates": result.gates,
        "false_gates": sorted(k for k, v in result.gates.items() if not v),
        "decision_support_closure_valid": bool(
            result.gates.get("decision_support_closure_valid")
        ),
        "claim_support_policy_violations": result.raw.get(
            "claim_support_policy_violations", []
        ),
        "critical_unresolved": result.raw.get("critical_unresolved", []),
        "global_consistency_violations": result.raw.get(
            "global_consistency_violations", []
        ),
        "evidence_errors": result.raw.get("evidence_errors", []),
        "identity_errors": result.raw.get("identity_errors", []),
        "integration_errors": result.raw.get("integration_errors", []),
    }


def run_isolated(relation_mode: str, placement_mode: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_stale_relation_snapshot_locality",
            "--single-relation",
            relation_mode,
            "--single-placement-mode",
            placement_mode,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip())
    return json.loads(cp.stdout)


def main() -> dict:
    rows = []
    for relation in RELATION_MODES:
        for placement in PLACEMENT_MODES:
            rows.append(run_isolated(relation, placement))

    comparisons = {}
    for relation in RELATION_MODES:
        rel_rows = {
            r["placement_mode"]: r
            for r in rows
            if r["relation_mode"] == relation
        }
        comparisons[relation] = {
            mode.lower(): {
                "claim_state": rel_rows[mode]["claim_state"],
                "control_closure": rel_rows[mode]["control_closure"],
                "false_gates": rel_rows[mode]["false_gates"],
                "global_consistency_violations": rel_rows[mode][
                    "global_consistency_violations"
                ],
            }
            for mode in PLACEMENT_MODES
        }

    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "STALE_RELATION_SNAPSHOT_LOCALITY",
        "state_count": len(rows),
        "relations": list(RELATION_MODES),
        "placement_modes": list(PLACEMENT_MODES),
        "comparisons": comparisons,
        "rows": rows,
        "interpretation_boundary": (
            "E1 is POSITIVE/CURRENT and alone satisfies required supports=1. "
            "E2 is POSITIVE/STALE. Relation shape is DISTINCT or exactly one tested "
            "shared provenance/dependency relation. E2 is either included in the evaluated snapshot, "
            "installed in a separate verified retrieval snapshot before evaluation, "
            "or fully verified but not installed in any snapshot. Every state runs in "
            "a fresh subprocess."
        ),
    }
    Path("stale_relation_snapshot_locality.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-relation", choices=RELATION_MODES)
    parser.add_argument("--single-placement-mode", choices=PLACEMENT_MODES)
    args = parser.parse_args()
    if args.single_relation:
        if args.single_placement_mode is None:
            raise SystemExit("--single-placement-mode is required")
        print(json.dumps(
            build_case(args.single_relation, args.single_placement_mode),
            sort_keys=True,
        ))
    else:
        main()
