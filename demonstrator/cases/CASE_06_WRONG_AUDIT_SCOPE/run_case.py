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
AUTHORITIES = {
    "IDENTITY": "DEMO_CASE06_IDENTITY_AUTHORITY",
    "SOURCE_SEMANTICS": "DEMO_CASE06_SOURCE_SEMANTICS_AUTHORITY",
    "PROVENANCE": "DEMO_CASE06_PROVENANCE_AUTHORITY",
    "EVIDENCE_AUTHORITY": "DEMO_CASE06_EVIDENCE_AUTHORITY",
    "EPISTEMIC_ROLE": "DEMO_CASE06_EPISTEMIC_ROLE_AUTHORITY",
    "RETRIEVAL": "DEMO_CASE06_RETRIEVAL_AUTHORITY",
    "FAILURE_DOMAIN_TOPOLOGY": "DEMO_CASE06_FAILURE_DOMAIN_TOPOLOGY_AUTHORITY",
}

# These verifiers are deliberately synthetic and case-scoped. They establish only the
# fictional demonstration trust state. They do not model production IAM/crypto/signatures.
class IdentityVerifier:
    def verify(self, a, *, draft):
        return IdentityAuthorityVerdict(True, "demo-case06:id:v1", a.attestation_id, a.authority_id, "SYNTHETIC_CASE_FIXTURE")
class SourceSemanticsVerifier:
    def verify(self, a, *, draft):
        return SourceSemanticsAuthorityVerdict(True, "demo-case06:ss:v1", a.attestation_id, a.authority_id, "SYNTHETIC_CASE_FIXTURE")
class ProvenanceVerifier:
    def verify(self, a, *, draft):
        return ProvenanceAuthorityVerdict(True, "demo-case06:prov:v1", a.attestation_id, a.authority_id, a.evidence_id, "SYNTHETIC_CASE_FIXTURE")
class EvidenceVerifier:
    def verify(self, a, *, draft):
        return EvidenceAuthorityVerdict(True, "demo-case06:ev:v1", a.attestation_id, a.authority_id, a.evidence_id, "SYNTHETIC_CASE_FIXTURE")
class RoleVerifier:
    def verify(self, a, *, draft, evidence):
        return EpistemicRoleAuthorityVerdict(True, "demo-case06:role:v1", a.attestation_id, a.authority_id, a.evidence_id, a.epistemic_role, "SYNTHETIC_CASE_FIXTURE")
class RetrievalVerifier:
    def verify(self, a, *, draft, evidence):
        return RetrievalAuthorityVerdict(True, "demo-case06:ret:v1", a.attestation_id, a.authority_id, "SYNTHETIC_CASE_FIXTURE")
class TopologyVerifier:
    def verify(self, a, *, draft):
        return FailureDomainTopologyVerdict(True, "demo-case06:topo:v1", a.attestation_id, a.authority_id, a.topology_commitment, "SYNTHETIC_CASE_FIXTURE")

verifiers = {
    "IDENTITY": IdentityVerifier(),
    "SOURCE_SEMANTICS": SourceSemanticsVerifier(),
    "PROVENANCE": ProvenanceVerifier(),
    "EVIDENCE_AUTHORITY": EvidenceVerifier(),
    "EPISTEMIC_ROLE": RoleVerifier(),
    "RETRIEVAL": RetrievalVerifier(),
    "FAILURE_DOMAIN_TOPOLOGY": TopologyVerifier(),
}
trust = HostTrustPolicy(tuple(
    HostTrustRegistration(boundary, AUTHORITIES[boundary], verifiers[boundary])
    for boundary in AUTHORITIES
))
c = Controller(scope="IGNORE", trust_policy=trust)

identity = c.draft_identity(
    registry_entry_id="id:demo-subject:v1", surface_subject="DemoSubject",
    domain_id="GENERAL_ENTITY", entity_id="entity:demo-subject",
    event_id="event:current", version_id="v1",
)
c.install_verified_identity(
    identity,
    IdentityAuthorityAttestation("att:case06:identity", AUTHORITIES["IDENTITY"], c.identity_commitment(identity), ASOF, "2026-01-01", "2026-12-31"),
    verifiers["IDENTITY"], as_of=ASOF,
)

semantics = c.draft_source_semantics(
    semantics_registry_entry_id="sem:case06:e1", source_id="general-record:case06:e1",
    repository_id="repo:case06", producer_id="producer:case06", process_id="process:case06",
    failure_domain_id="fd:case06:e1", resolution_state="KNOWN",
)
c.install_verified_source_semantics(
    semantics,
    SourceSemanticsAuthorityAttestation("att:case06:semantics", AUTHORITIES["SOURCE_SEMANTICS"], c.source_semantics_commitment(semantics), ASOF, "2026-01-01", "2026-12-31"),
    verifiers["SOURCE_SEMANTICS"], as_of=ASOF,
)

topology = c.draft_failure_domain_topology()
c.install_verified_failure_domain_topology(
    topology,
    FailureDomainTopologyAttestation("att:case06:topology", AUTHORITIES["FAILURE_DOMAIN_TOPOLOGY"], c.failure_domain_topology_commitment(topology), ASOF, "2026-01-01", "2026-12-31"),
    verifiers["FAILURE_DOMAIN_TOPOLOGY"], as_of=ASOF,
)

prefix = {
    "data_source":"data", "sensor_input":"sensor", "transform":"transform",
    "model":"model", "extractor":"extractor", "cache":"cache",
    "upstream_db":"db", "operator":"operator", "preprocessing":"prep", "runtime":"runtime",
}
dependencies = {k: {"state":"KNOWN", "id":f"{v}:case06:e1"} for k, v in prefix.items()}
provenance = {
    "source_id":"general-record:case06:e1",
    "root_origin_id":"general-record:root:case06:e1",
    "origin_id":"general-record:origin:case06:e1",
    "referent_entity_id":"entity:demo-subject",
    "referent_event_id":"event:current",
    "referent_version_id":"v1",
    "extractor_id":"extractor:case06:e1",
    "common_mode_group":"group:case06:e1",
    "lineage":["general-record:root:case06:e1", "general-record:origin:case06:e1"],
    "dependencies":dependencies,
}
evidence = c.draft_evidence_record(
    evidence_id="E1", subject="DemoSubject", predicate="state", value="safe",
    source="display:case06:e1", identity_registry_entry_id="id:demo-subject:v1",
    authority_id="GENERAL_RECORD_V5", authority_record_entity_id="entity:demo-subject",
    authority_record_event_id="event:current", authority_record_version_id="v1",
    valid_from="2026-01-01", valid_to="2026-12-31", observed_at=ASOF, available_at=ASOF,
    provenance=provenance, polarity="POSITIVE", source_semantics_id="sem:case06:e1",
)
c.verify_evidence_provenance(
    evidence,
    ProvenanceAuthorityAttestation("att:case06:provenance", AUTHORITIES["PROVENANCE"], "E1", c.provenance_commitment(evidence), ASOF, "2026-01-01", "2026-12-31"),
    verifiers["PROVENANCE"], as_of=ASOF,
)
c.verify_evidence_authority(
    evidence,
    EvidenceAuthorityAttestation("att:case06:evidence", AUTHORITIES["EVIDENCE_AUTHORITY"], "E1", "GENERAL_RECORD_V5", c.evidence_authority_commitment(evidence), ASOF, "2026-01-01", "2026-12-31"),
    verifiers["EVIDENCE_AUTHORITY"], as_of=ASOF,
)
role = c.draft_epistemic_role(evidence, epistemic_role="DIRECT_WORLD_RECORD")
role_installation = c.install_verified_epistemic_role(
    evidence, role,
    EpistemicRoleAuthorityAttestation("att:case06:role", AUTHORITIES["EPISTEMIC_ROLE"], "E1", "DIRECT_WORLD_RECORD", role.role_commitment, ASOF, "2026-01-01", "2026-12-31"),
    verifiers["EPISTEMIC_ROLE"], as_of=ASOF,
)
evidence = c.evidence_with_epistemic_role(evidence, role_installation)
record = c.evidence_record_mapping(evidence)

snapshot = c.draft_snapshot(
    [record], scope_id="scope:demo:case06", snapshot_id="snapshot:demo:case06",
    snapshot_created_at=ASOF,
    snapshot_available_at=ASOF, valid_from="2026-01-01", valid_to="2026-12-31",
)
c.install_verified_snapshot(
    snapshot, [record],
    RetrievalAuthorityAttestation("att:case06:retrieval", AUTHORITIES["RETRIEVAL"], c.snapshot_commitment(snapshot), ASOF, "2026-01-01", "2026-12-31"),
    verifiers["RETRIEVAL"], as_of=ASOF,
)

result = c.evaluate_snapshot(
    snapshot, "DemoSubject is safe.", [record], {"c1":"id:demo-subject:v1"}, as_of=ASOF, requirements={"c1":{"required_independent_supports":1}},
)
summary = {
    "case_id":"CASE_06_WRONG_AUDIT_SCOPE",
    "engine_sha256":c.controller_sha256,
    "mandatory_gate_count":c.mandatory_gate_count,
    "persistence_schema":c.persistence_schema,
    "model_conclusion":"DemoSubject is safe.",
    "evidence":[record],
    "claim_states":result.claims,
    "stop_type":result.stop_type,
    "control_closure":result.control_closure,
    "gates":result.gates,
    "evidence_errors":result.raw.get("evidence_errors", []),
    "identity_errors":result.raw.get("identity_errors", []),
    "integration_errors":result.raw.get("integration_errors", []),
    "raw_keys":sorted(result.raw.keys()),
    "critical_unresolved":result.raw.get("critical_unresolved", []),
    "claim_support_policy_violations":result.raw.get("claim_support_policy_violations", []),
    "constraint_relation_coverage_violations":result.raw.get("constraint_relation_coverage_violations", []),
    "constraint_coverage_violations":result.raw.get("constraint_coverage_violations", []),
    "global_consistency_violations":result.raw.get("global_consistency_violations", []),
}
print(json.dumps(summary, indent=2, sort_keys=True))
