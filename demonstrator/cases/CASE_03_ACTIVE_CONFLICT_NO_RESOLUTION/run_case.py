from __future__ import annotations
import json
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

ASOF = "2026-09-03"
TAG = "case03"
AUTHORITIES = {
    "IDENTITY": "DEMO_CASE03_IDENTITY_AUTHORITY",
    "SOURCE_SEMANTICS": "DEMO_CASE03_SOURCE_SEMANTICS_AUTHORITY",
    "PROVENANCE": "DEMO_CASE03_PROVENANCE_AUTHORITY",
    "EVIDENCE_AUTHORITY": "DEMO_CASE03_EVIDENCE_AUTHORITY",
    "EPISTEMIC_ROLE": "DEMO_CASE03_EPISTEMIC_ROLE_AUTHORITY",
    "RETRIEVAL": "DEMO_CASE03_RETRIEVAL_AUTHORITY",
    "FAILURE_DOMAIN_TOPOLOGY": "DEMO_CASE03_FAILURE_DOMAIN_TOPOLOGY_AUTHORITY",
}

class IdentityVerifier:
    def verify(self, a, *, draft): return IdentityAuthorityVerdict(True, f"demo-{TAG}:id:v1", a.attestation_id, a.authority_id, "SYNTHETIC_CASE_FIXTURE")
class SourceSemanticsVerifier:
    def verify(self, a, *, draft): return SourceSemanticsAuthorityVerdict(True, f"demo-{TAG}:ss:v1", a.attestation_id, a.authority_id, "SYNTHETIC_CASE_FIXTURE")
class ProvenanceVerifier:
    def verify(self, a, *, draft): return ProvenanceAuthorityVerdict(True, f"demo-{TAG}:prov:v1", a.attestation_id, a.authority_id, a.evidence_id, "SYNTHETIC_CASE_FIXTURE")
class EvidenceVerifier:
    def verify(self, a, *, draft): return EvidenceAuthorityVerdict(True, f"demo-{TAG}:ev:v1", a.attestation_id, a.authority_id, a.evidence_id, "SYNTHETIC_CASE_FIXTURE")
class RoleVerifier:
    def verify(self, a, *, draft, evidence): return EpistemicRoleAuthorityVerdict(True, f"demo-{TAG}:role:v1", a.attestation_id, a.authority_id, a.evidence_id, a.epistemic_role, "SYNTHETIC_CASE_FIXTURE")
class RetrievalVerifier:
    def verify(self, a, *, draft, evidence): return RetrievalAuthorityVerdict(True, f"demo-{TAG}:ret:v1", a.attestation_id, a.authority_id, "SYNTHETIC_CASE_FIXTURE")
class TopologyVerifier:
    def verify(self, a, *, draft): return FailureDomainTopologyVerdict(True, f"demo-{TAG}:topo:v1", a.attestation_id, a.authority_id, a.topology_commitment, "SYNTHETIC_CASE_FIXTURE")

verifiers = {
    "IDENTITY": IdentityVerifier(), "SOURCE_SEMANTICS": SourceSemanticsVerifier(),
    "PROVENANCE": ProvenanceVerifier(), "EVIDENCE_AUTHORITY": EvidenceVerifier(),
    "EPISTEMIC_ROLE": RoleVerifier(), "RETRIEVAL": RetrievalVerifier(),
    "FAILURE_DOMAIN_TOPOLOGY": TopologyVerifier(),
}
trust = HostTrustPolicy(tuple(HostTrustRegistration(k, AUTHORITIES[k], verifiers[k]) for k in AUTHORITIES))
c = Controller(trust_policy=trust)

identity = c.draft_identity(
    registry_entry_id="id:demo-subject:v1", surface_subject="DemoSubject",
    domain_id="GENERAL_ENTITY", entity_id="entity:demo-subject", event_id="event:current", version_id="v1",
)
c.install_verified_identity(
    identity,
    IdentityAuthorityAttestation("att:case03:identity", AUTHORITIES["IDENTITY"], c.identity_commitment(identity), ASOF, "2026-01-01", "2026-12-31"),
    verifiers["IDENTITY"], as_of=ASOF,
)

topology = c.draft_failure_domain_topology()
c.install_verified_failure_domain_topology(
    topology,
    FailureDomainTopologyAttestation("att:case03:topology", AUTHORITIES["FAILURE_DOMAIN_TOPOLOGY"], c.failure_domain_topology_commitment(topology), ASOF, "2026-01-01", "2026-12-31"),
    verifiers["FAILURE_DOMAIN_TOPOLOGY"], as_of=ASOF,
)

prefix = {"data_source":"data", "sensor_input":"sensor", "transform":"transform", "model":"model", "extractor":"extractor", "cache":"cache", "upstream_db":"db", "operator":"operator", "preprocessing":"prep", "runtime":"runtime"}

def trusted_record(eid: str, polarity: str):
    sem_id=f"sem:case03:{eid.lower()}"
    source_id=f"general-record:case03:{eid.lower()}"
    semantics=c.draft_source_semantics(
        semantics_registry_entry_id=sem_id, source_id=source_id,
        repository_id=f"repo:case03:{eid.lower()}", producer_id=f"producer:case03:{eid.lower()}", process_id=f"process:case03:{eid.lower()}",
        failure_domain_id=f"fd:case03:{eid.lower()}", resolution_state="KNOWN",
    )
    c.install_verified_source_semantics(
        semantics,
        SourceSemanticsAuthorityAttestation(f"att:case03:semantics:{eid}", AUTHORITIES["SOURCE_SEMANTICS"], c.source_semantics_commitment(semantics), ASOF, "2026-01-01", "2026-12-31"),
        verifiers["SOURCE_SEMANTICS"], as_of=ASOF,
    )
    deps={k:{"state":"KNOWN", "id":f"{v}:case03:{eid.lower()}"} for k,v in prefix.items()}
    provenance={
        "source_id":source_id,
        "root_origin_id":f"general-record:root:case03:{eid.lower()}",
        "origin_id":f"general-record:origin:case03:{eid.lower()}",
        "referent_entity_id":"entity:demo-subject", "referent_event_id":"event:current", "referent_version_id":"v1",
        "extractor_id":f"extractor:case03:{eid.lower()}", "common_mode_group":f"group:case03:{eid.lower()}",
        "lineage":[f"general-record:root:case03:{eid.lower()}", f"general-record:origin:case03:{eid.lower()}"],
        "dependencies":deps,
    }
    draft=c.draft_evidence_record(
        evidence_id=eid, subject="DemoSubject", predicate="state", value="safe", source=f"display:case03:{eid.lower()}",
        identity_registry_entry_id="id:demo-subject:v1", authority_id="GENERAL_RECORD_V5",
        authority_record_entity_id="entity:demo-subject", authority_record_event_id="event:current", authority_record_version_id="v1",
        valid_from="2026-01-01", valid_to="2026-12-31", observed_at=ASOF, available_at=ASOF,
        provenance=provenance, polarity=polarity, source_semantics_id=sem_id,
    )
    c.verify_evidence_provenance(
        draft,
        ProvenanceAuthorityAttestation(f"att:case03:provenance:{eid}", AUTHORITIES["PROVENANCE"], eid, c.provenance_commitment(draft), ASOF, "2026-01-01", "2026-12-31"),
        verifiers["PROVENANCE"], as_of=ASOF,
    )
    c.verify_evidence_authority(
        draft,
        EvidenceAuthorityAttestation(f"att:case03:evidence:{eid}", AUTHORITIES["EVIDENCE_AUTHORITY"], eid, "GENERAL_RECORD_V5", c.evidence_authority_commitment(draft), ASOF, "2026-01-01", "2026-12-31"),
        verifiers["EVIDENCE_AUTHORITY"], as_of=ASOF,
    )
    role=c.draft_epistemic_role(draft, epistemic_role="DIRECT_WORLD_RECORD")
    role_install=c.install_verified_epistemic_role(
        draft, role,
        EpistemicRoleAuthorityAttestation(f"att:case03:role:{eid}", AUTHORITIES["EPISTEMIC_ROLE"], eid, "DIRECT_WORLD_RECORD", role.role_commitment, ASOF, "2026-01-01", "2026-12-31"),
        verifiers["EPISTEMIC_ROLE"], as_of=ASOF,
    )
    return c.evidence_record_mapping(c.evidence_with_epistemic_role(draft, role_install))

records=[trusted_record("E1", "POSITIVE"), trusted_record("E2", "NEGATIVE")]
snapshot=c.draft_snapshot(
    records, scope_id="scope:demo:case03", snapshot_id="snapshot:demo:case03", snapshot_created_at=ASOF, snapshot_available_at=ASOF, valid_from="2026-01-01", valid_to="2026-12-31",
)
c.install_verified_snapshot(
    snapshot, records,
    RetrievalAuthorityAttestation("att:case03:retrieval", AUTHORITIES["RETRIEVAL"], c.snapshot_commitment(snapshot), ASOF, "2026-01-01", "2026-12-31"),
    verifiers["RETRIEVAL"], as_of=ASOF,
)

result=c.evaluate_snapshot(snapshot, "DemoSubject is safe.", records, {"c1":"id:demo-subject:v1"}, as_of=ASOF, requirements={"c1":{"required_independent_supports":1}})
summary={
    "case_id":"CASE_03_ACTIVE_CONFLICT_NO_RESOLUTION",
    "engine_sha256":c.controller_sha256,
    "mandatory_gate_count":c.mandatory_gate_count,
    "persistence_schema":c.persistence_schema,
    "model_conclusion":"DemoSubject is safe.",
    "evidence":records,
    "claim_states":result.claims,
    "stop_type":result.stop_type,
    "control_closure":result.control_closure,
    "gates":result.gates,
    "evidence_errors":result.raw.get("evidence_errors", []),
    "identity_errors":result.raw.get("identity_errors", []),
    "integration_errors":result.raw.get("integration_errors", []),
    "global_consistency_violations":result.raw.get("global_consistency_violations", []),
    "relation_resolution_certificates":result.raw.get("relation_resolution_certificates", []),
    "raw_keys":sorted(result.raw.keys()),
    "critical_unresolved":result.raw.get("critical_unresolved", []),
    "claim_support_policy_violations":result.raw.get("claim_support_policy_violations", []),
    "constraint_relation_coverage_violations":result.raw.get("constraint_relation_coverage_violations", []),
    "constraint_coverage_violations":result.raw.get("constraint_coverage_violations", []),
}
print(json.dumps(summary,indent=2,sort_keys=True))
