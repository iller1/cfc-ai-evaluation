from __future__ import annotations

import json
from pathlib import Path

from cfc_anchor import (
    Controller, HostTrustPolicy, HostTrustRegistration,
    IdentityAuthorityAttestation, IdentityAuthorityVerdict,
    SourceSemanticsAuthorityAttestation, SourceSemanticsAuthorityVerdict,
    ProvenanceAuthorityAttestation, ProvenanceAuthorityVerdict,
    EvidenceAuthorityAttestation, EvidenceAuthorityVerdict,
    EpistemicRoleAuthorityAttestation, EpistemicRoleAuthorityVerdict,
    RetrievalAuthorityAttestation, RetrievalAuthorityVerdict,
    FailureDomainTopologyAttestation, FailureDomainTopologyVerdict,
)
from demonstrator.custom_case_runner import (
    ASOF, VALID_FROM, VALID_TO, AUTHORITIES,
    VIdentity, VSource, VProv, VEvidence, VRole, VRetrieval, VTopology,
)


def execute_single_shared_e1() -> dict:
    verifiers = {
        "IDENTITY": VIdentity(),
        "SOURCE_SEMANTICS": VSource(),
        "PROVENANCE": VProv(),
        "EVIDENCE_AUTHORITY": VEvidence(),
        "EPISTEMIC_ROLE": VRole(),
        "RETRIEVAL": VRetrieval(),
        "FAILURE_DOMAIN_TOPOLOGY": VTopology(),
    }
    trust = HostTrustPolicy(tuple(
        HostTrustRegistration(k, AUTHORITIES[k], verifiers[k])
        for k in verifiers
    ))
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
            "att:iso:identity", AUTHORITIES["IDENTITY"],
            c.identity_commitment(identity), ASOF, VALID_FROM, VALID_TO
        ),
        verifiers["IDENTITY"],
        as_of=ASOF,
    )

    topology = c.draft_failure_domain_topology()
    c.install_verified_failure_domain_topology(
        topology,
        FailureDomainTopologyAttestation(
            "att:iso:topology", AUTHORITIES["FAILURE_DOMAIN_TOPOLOGY"],
            c.failure_domain_topology_commitment(topology),
            ASOF, VALID_FROM, VALID_TO,
        ),
        verifiers["FAILURE_DOMAIN_TOPOLOGY"],
        as_of=ASOF,
    )

    sem_id = "sem:iso:e1"
    semantics = c.draft_source_semantics(
        semantics_registry_entry_id=sem_id,
        source_id="general-record:iso:e1",
        repository_id="repo:shared",
        producer_id="producer:shared",
        process_id="process:shared",
        failure_domain_id="fd:shared",
        resolution_state="KNOWN",
    )
    c.install_verified_source_semantics(
        semantics,
        SourceSemanticsAuthorityAttestation(
            "att:iso:semantics", AUTHORITIES["SOURCE_SEMANTICS"],
            c.source_semantics_commitment(semantics),
            ASOF, VALID_FROM, VALID_TO,
        ),
        verifiers["SOURCE_SEMANTICS"],
        as_of=ASOF,
    )

    prefix = {
        "data_source": "data", "sensor_input": "sensor", "transform": "transform",
        "model": "model", "extractor": "extractor", "cache": "cache",
        "upstream_db": "db", "operator": "operator", "preprocessing": "prep",
        "runtime": "runtime",
    }
    dependencies = {
        k: {"state": "KNOWN", "id": f"{v}:shared"} for k, v in prefix.items()
    }
    provenance = {
        "source_id": "general-record:iso:e1",
        "root_origin_id": "general-record:root:shared",
        "origin_id": "general-record:origin:shared",
        "referent_entity_id": "entity:demo-subject",
        "referent_event_id": "event:current",
        "referent_version_id": "v1",
        "extractor_id": "extractor:shared",
        "common_mode_group": "group:shared",
        "lineage": [
            "general-record:root:shared",
            "general-record:origin:shared",
        ],
        "dependencies": dependencies,
    }

    evidence = c.draft_evidence_record(
        evidence_id="E1",
        subject="DemoSubject",
        predicate="state",
        value="safe",
        source="display:iso:e1",
        identity_registry_entry_id="id:demo-subject:v1",
        authority_id="GENERAL_RECORD_V5",
        authority_record_entity_id="entity:demo-subject",
        authority_record_event_id="event:current",
        authority_record_version_id="v1",
        valid_from=VALID_FROM,
        valid_to=VALID_TO,
        observed_at=ASOF,
        available_at=ASOF,
        provenance=provenance,
        polarity="POSITIVE",
        source_semantics_id=sem_id,
    )
    c.verify_evidence_provenance(
        evidence,
        ProvenanceAuthorityAttestation(
            "att:iso:prov", AUTHORITIES["PROVENANCE"], "E1",
            c.provenance_commitment(evidence), ASOF, VALID_FROM, VALID_TO,
        ),
        verifiers["PROVENANCE"],
        as_of=ASOF,
    )
    c.verify_evidence_authority(
        evidence,
        EvidenceAuthorityAttestation(
            "att:iso:evidence", AUTHORITIES["EVIDENCE_AUTHORITY"], "E1",
            "GENERAL_RECORD_V5", c.evidence_authority_commitment(evidence),
            ASOF, VALID_FROM, VALID_TO,
        ),
        verifiers["EVIDENCE_AUTHORITY"],
        as_of=ASOF,
    )
    role = c.draft_epistemic_role(evidence, epistemic_role="DIRECT_WORLD_RECORD")
    role_installation = c.install_verified_epistemic_role(
        evidence,
        role,
        EpistemicRoleAuthorityAttestation(
            "att:iso:role", AUTHORITIES["EPISTEMIC_ROLE"], "E1",
            "DIRECT_WORLD_RECORD", role.role_commitment,
            ASOF, VALID_FROM, VALID_TO,
        ),
        verifiers["EPISTEMIC_ROLE"],
        as_of=ASOF,
    )
    evidence = c.evidence_with_epistemic_role(evidence, role_installation)
    records = [c.evidence_record_mapping(evidence)]

    snapshot = c.draft_snapshot(
        records,
        scope_id="scope:demo:iso",
        snapshot_id="snapshot:demo:iso",
        snapshot_created_at=ASOF,
        snapshot_available_at=ASOF,
        valid_from=VALID_FROM,
        valid_to=VALID_TO,
    )
    c.install_verified_snapshot(
        snapshot,
        records,
        RetrievalAuthorityAttestation(
            "att:iso:retrieval", AUTHORITIES["RETRIEVAL"],
            c.snapshot_commitment(snapshot), ASOF, VALID_FROM, VALID_TO,
        ),
        verifiers["RETRIEVAL"],
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
    false_gates = sorted(k for k, v in result.gates.items() if not v)
    claim = result.claims[0] if result.claims else {}
    return {
        "claim_state": claim.get("state"),
        "claim_reason": claim.get("reason"),
        "control_closure": result.control_closure,
        "stop_type": result.stop_type,
        "false_gates": false_gates,
        "claim_support_policy_violations": result.raw.get("claim_support_policy_violations", []),
        "critical_unresolved": result.raw.get("critical_unresolved", []),
        "global_consistency_violations": result.raw.get("global_consistency_violations", []),
    }


def main():
    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "SINGLE_E1_WITH_PRESERVED_SHARED_LINEAGE_PROVENANCE",
        "result": execute_single_shared_e1(),
        "purpose": (
            "Isolate whether STOP/VERIFIED persists when E2 is absent but E1 retains "
            "the same shared-lineage/common-mode provenance identifiers."
        ),
    }
    Path("single_shared_e1_isolation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
