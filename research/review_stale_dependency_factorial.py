from __future__ import annotations

import itertools
import json
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

FACTOR_NAMES = (
    "source_semantics_shared",
    "origin_lineage_shared",
    "common_mode_group_shared",
    "dependencies_shared",
)

PREFIX = {
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


def token(shared: bool, idx: int) -> str:
    return "shared" if shared else f"iso:e{idx}"


def build_case(mask: dict[str, bool]) -> dict:
    mask_bits = "".join("1" if mask[name] else "0" for name in FACTOR_NAMES)
    scope_id = f"scope:factorial:{mask_bits}"
    snapshot_id = f"snapshot:factorial:{mask_bits}"

    trust = HostTrustPolicy(
        tuple(
            HostTrustRegistration(kind, AUTHORITIES[kind], VERIFIERS[kind])
            for kind in AUTHORITIES
            if kind != "SUPPORT_SET_INDEPENDENCE"
        )
    )
    c = Controller(trust_policy=trust)

    identity = c.draft_identity(
        registry_entry_id="id:demo-subject:v1",
        surface_subject="DemoSubject",
        domain_id="GENERAL_ENTITY",
        entity_id="entity:demo-subject",
        event_id="event:current",
        version_id="v1",
    )
    c.install_verified_identity(
        identity,
        IdentityAuthorityAttestation(
            "att:factorial:identity",
            AUTHORITIES["IDENTITY"],
            c.identity_commitment(identity),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["IDENTITY"],
        as_of=ASOF,
    )

    topology = c.draft_failure_domain_topology()
    c.install_verified_failure_domain_topology(
        topology,
        FailureDomainTopologyAttestation(
            "att:factorial:topology",
            AUTHORITIES["FAILURE_DOMAIN_TOPOLOGY"],
            c.failure_domain_topology_commitment(topology),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["FAILURE_DOMAIN_TOPOLOGY"],
        as_of=ASOF,
    )

    records = []
    for idx, validity in ((1, "CURRENT"), (2, "STALE")):
        eid = f"E{idx}:{mask_bits}"
        source_token = f"factorial:{mask_bits}:e{idx}"
        semantic_token = token(mask["source_semantics_shared"], idx)
        lineage_token = token(mask["origin_lineage_shared"], idx)
        cm_token = token(mask["common_mode_group_shared"], idx)
        dep_token = token(mask["dependencies_shared"], idx)

        sem_id = f"sem:{source_token}"
        semantics = c.draft_source_semantics(
            semantics_registry_entry_id=sem_id,
            source_id=f"general-record:{source_token}",
            repository_id=f"repo:{semantic_token}",
            producer_id=f"producer:{semantic_token}",
            process_id=f"process:{semantic_token}",
            failure_domain_id=f"fd:{semantic_token}",
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

        dependencies = {
            k: {"state": "KNOWN", "id": f"{v}:{dep_token}"}
            for k, v in PREFIX.items()
        }
        provenance = {
            "source_id": f"general-record:{source_token}",
            "root_origin_id": f"general-record:root:{lineage_token}",
            "origin_id": f"general-record:origin:{lineage_token}",
            "referent_entity_id": "entity:demo-subject",
            "referent_event_id": "event:current",
            "referent_version_id": "v1",
            "extractor_id": f"extractor:{lineage_token}",
            "common_mode_group": f"group:{cm_token}",
            "lineage": [
                f"general-record:root:{lineage_token}",
                f"general-record:origin:{lineage_token}",
            ],
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
            identity_registry_entry_id="id:demo-subject:v1",
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
            evidence,
            epistemic_role="DIRECT_WORLD_RECORD",
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
        records.append(c.evidence_record_mapping(evidence))

    snapshot = c.draft_snapshot(
        records,
        scope_id=scope_id,
        snapshot_id=snapshot_id,
        snapshot_created_at=ASOF,
        snapshot_available_at=ASOF,
        valid_from=VALID_FROM,
        valid_to=VALID_TO,
    )
    c.install_verified_snapshot(
        snapshot,
        records,
        RetrievalAuthorityAttestation(
            "att:factorial:retrieval",
            AUTHORITIES["RETRIEVAL"],
            c.snapshot_commitment(snapshot),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["RETRIEVAL"],
        as_of=ASOF,
    )

    result = c.evaluate_snapshot(
        snapshot,
        "DemoSubject is safe.",
        records,
        {"c1": "id:demo-subject:v1"},
        as_of=ASOF,
        requirements={"c1": {"required_independent_supports": 1}},
    )

    claim = result.claims[0] if result.claims else {}
    false_gates = sorted(k for k, v in result.gates.items() if not v)

    return {
        "mask": mask,
        "mask_bits": mask_bits,
        "shared_factor_count": sum(1 for v in mask.values() if v),
        "claim_state": claim.get("status"),
        "claim_reason": claim.get("reason"),
        "control_closure": bool(result.control_closure),
        "false_gates": false_gates,
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
    }


def original_fixture_control() -> dict:
    payload = {
        "conclusion": "POSITIVE",
        "required_independent_supports": 1,
        "scope": "EXPECTED",
        "provenance_shape": "SHARED_LINEAGE",
        "independence_authority": "NONE",
        "evidence": [
            {"polarity": "POSITIVE", "validity": "CURRENT"},
            {"polarity": "POSITIVE", "validity": "STALE"},
        ],
    }
    out = demo_server.run_custom(payload)
    p = out["presentation"]
    r = out["result"]
    return {
        "decision": p.get("decision"),
        "claim_state": p.get("claim_state"),
        "reason": p.get("reason"),
        "control_closure": bool(r.get("control_closure")),
        "false_gates": p.get("false_gates") or [],
    }


def main() -> dict:
    rows = []
    for bits in itertools.product((False, True), repeat=len(FACTOR_NAMES)):
        mask = dict(zip(FACTOR_NAMES, bits))
        rows.append(build_case(mask))

    blockers = [r for r in rows if not r["control_closure"]]
    allowers = [r for r in rows if r["control_closure"]]

    minimal_blockers = []
    for row in blockers:
        shared = {k for k, v in row["mask"].items() if v}
        if not any(
            {k for k, v in other["mask"].items() if v} < shared
            for other in blockers
        ):
            minimal_blockers.append(row)

    original = original_fixture_control()
    full_shared = next(r for r in rows if r["mask_bits"] == "1111")
    equivalence = {
        "original_fixture": original,
        "factorial_1111": {
            "claim_state": full_shared["claim_state"],
            "control_closure": full_shared["control_closure"],
            "false_gates": full_shared["false_gates"],
        },
        "matches_claim_state": original["claim_state"] == full_shared["claim_state"],
        "matches_control_closure": original["control_closure"] == full_shared["control_closure"],
        "matches_false_gates": original["false_gates"] == full_shared["false_gates"],
    }

    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "STALE_E2_SHARED_DEPENDENCY_FACTORIAL_2X2X2X2",
        "factor_order": list(FACTOR_NAMES),
        "state_count": len(rows),
        "allow_count": len(allowers),
        "stop_count": len(blockers),
        "fixture_equivalence_control": equivalence,
        "minimal_blocking_masks": [
            {
                "mask_bits": r["mask_bits"],
                "mask": r["mask"],
                "claim_state": r["claim_state"],
                "false_gates": r["false_gates"],
            }
            for r in minimal_blockers
        ],
        "rows": rows,
        "interpretation_boundary": (
            "E1 is CURRENT, E2 is STALE, both support the claim, required supports=1. "
            "Only four shared-provenance factor groups vary. This is an external "
            "factorial fixture; frozen CFC is unchanged."
        ),
    }
    Path("stale_dependency_factorial.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
