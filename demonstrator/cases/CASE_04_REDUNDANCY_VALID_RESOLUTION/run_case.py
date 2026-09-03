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
    SupportSetIndependenceAuthorityAttestation, SupportSetIndependenceAuthorityVerdict,
    SupportRelationAuthorityAttestation, SupportRelationAuthorityVerdict,
    SupportSelectionAuthorityAttestation, SupportSelectionAuthorityVerdict,
    RelationResolutionAuthorityAttestation, RelationResolutionAuthorityVerdict,
    ExcludedSupportDispositionAuthorityAttestation, ExcludedSupportDispositionAuthorityVerdict,
)

ASOF = "2026-09-03"
TAG = "case04"
AUTHORITIES = {
    "IDENTITY": "DEMO_CASE04_IDENTITY_AUTHORITY",
    "SOURCE_SEMANTICS": "DEMO_CASE04_SOURCE_SEMANTICS_AUTHORITY",
    "PROVENANCE": "DEMO_CASE04_PROVENANCE_AUTHORITY",
    "EVIDENCE_AUTHORITY": "DEMO_CASE04_EVIDENCE_AUTHORITY",
    "EPISTEMIC_ROLE": "DEMO_CASE04_EPISTEMIC_ROLE_AUTHORITY",
    "RETRIEVAL": "DEMO_CASE04_RETRIEVAL_AUTHORITY",
    "FAILURE_DOMAIN_TOPOLOGY": "DEMO_CASE04_FAILURE_DOMAIN_TOPOLOGY_AUTHORITY",
    "SUPPORT_SET_INDEPENDENCE": "DEMO_CASE04_SUPPORT_SET_INDEPENDENCE_AUTHORITY",
    "SUPPORT_RELATION": "DEMO_CASE04_SUPPORT_RELATION_AUTHORITY",
    "SUPPORT_SELECTION": "DEMO_CASE04_SUPPORT_SELECTION_AUTHORITY",
    "RELATION_RESOLUTION": "DEMO_CASE04_RELATION_RESOLUTION_AUTHORITY",
    "EXCLUDED_SUPPORT_DISPOSITION": "DEMO_CASE04_EXCLUDED_SUPPORT_DISPOSITION_AUTHORITY",
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
class SupportSetIndependenceVerifier:
    def verify(self, a, *, draft, evidence): return SupportSetIndependenceAuthorityVerdict(True, f"demo-{TAG}:ssi:v1", a.attestation_id, a.authority_id, draft.independence_id, "SYNTHETIC_CASE_FIXTURE")
class SupportRelationVerifier:
    def verify(self, a, *, draft, evidence): return SupportRelationAuthorityVerdict(True, f"demo-{TAG}:rel:v1", a.attestation_id, a.authority_id, draft.relation_id, "SYNTHETIC_CASE_FIXTURE")
class SupportSelectionVerifier:
    def verify(self, a, *, draft, evidence): return SupportSelectionAuthorityVerdict(True, f"demo-{TAG}:sel:v1", a.attestation_id, a.authority_id, draft.selection_id, "SYNTHETIC_CASE_FIXTURE")
class RelationResolutionVerifier:
    def verify(self, a, *, draft, evidence): return RelationResolutionAuthorityVerdict(True, f"demo-{TAG}:rr:v1", a.attestation_id, a.authority_id, draft.resolution_id, "SYNTHETIC_CASE_FIXTURE")
class ExcludedDispositionVerifier:
    def verify(self, a, *, draft, evidence): return ExcludedSupportDispositionAuthorityVerdict(True, f"demo-{TAG}:disp:v1", a.attestation_id, a.authority_id, draft.disposition_id, "SYNTHETIC_CASE_FIXTURE")

verifiers = {
    "IDENTITY": IdentityVerifier(), "SOURCE_SEMANTICS": SourceSemanticsVerifier(),
    "PROVENANCE": ProvenanceVerifier(), "EVIDENCE_AUTHORITY": EvidenceVerifier(),
    "EPISTEMIC_ROLE": RoleVerifier(), "RETRIEVAL": RetrievalVerifier(),
    "FAILURE_DOMAIN_TOPOLOGY": TopologyVerifier(),
    "SUPPORT_SET_INDEPENDENCE": SupportSetIndependenceVerifier(),
    "SUPPORT_RELATION": SupportRelationVerifier(),
    "SUPPORT_SELECTION": SupportSelectionVerifier(),
    "RELATION_RESOLUTION": RelationResolutionVerifier(),
    "EXCLUDED_SUPPORT_DISPOSITION": ExcludedDispositionVerifier(),
}
trust = HostTrustPolicy(tuple(HostTrustRegistration(k, AUTHORITIES[k], verifiers[k]) for k in AUTHORITIES))
c = Controller(trust_policy=trust)

identity = c.draft_identity(
    registry_entry_id="id:demo-subject:v1", surface_subject="DemoSubject",
    domain_id="GENERAL_ENTITY", entity_id="entity:demo-subject", event_id="event:current", version_id="v1",
)
c.install_verified_identity(
    identity,
    IdentityAuthorityAttestation("att:case04:identity", AUTHORITIES["IDENTITY"], c.identity_commitment(identity), ASOF, "2026-01-01", "2026-12-31"),
    verifiers["IDENTITY"], as_of=ASOF,
)

topology = c.draft_failure_domain_topology()
c.install_verified_failure_domain_topology(
    topology,
    FailureDomainTopologyAttestation("att:case04:topology", AUTHORITIES["FAILURE_DOMAIN_TOPOLOGY"], c.failure_domain_topology_commitment(topology), ASOF, "2026-01-01", "2026-12-31"),
    verifiers["FAILURE_DOMAIN_TOPOLOGY"], as_of=ASOF,
)

prefix = {"data_source":"data", "sensor_input":"sensor", "transform":"transform", "model":"model", "extractor":"extractor", "cache":"cache", "upstream_db":"db", "operator":"operator", "preprocessing":"prep", "runtime":"runtime"}

def trusted_record(eid: str, polarity: str):
    sem_id=f"sem:case04:{eid.lower()}"
    source_id=f"general-record:case04:{eid.lower()}"
    semantics=c.draft_source_semantics(
        semantics_registry_entry_id=sem_id, source_id=source_id,
        repository_id=f"repo:case04:{eid.lower()}", producer_id=f"producer:case04:{eid.lower()}", process_id=f"process:case04:{eid.lower()}",
        failure_domain_id=f"fd:case04:{eid.lower()}", resolution_state="KNOWN",
    )
    c.install_verified_source_semantics(
        semantics,
        SourceSemanticsAuthorityAttestation(f"att:case04:semantics:{eid}", AUTHORITIES["SOURCE_SEMANTICS"], c.source_semantics_commitment(semantics), ASOF, "2026-01-01", "2026-12-31"),
        verifiers["SOURCE_SEMANTICS"], as_of=ASOF,
    )
    deps={k:{"state":"KNOWN", "id":f"{v}:case04:{eid.lower()}"} for k,v in prefix.items()}
    provenance={
        "source_id":source_id,
        "root_origin_id":f"general-record:root:case04:{eid.lower()}",
        "origin_id":f"general-record:origin:case04:{eid.lower()}",
        "referent_entity_id":"entity:demo-subject", "referent_event_id":"event:current", "referent_version_id":"v1",
        "extractor_id":f"extractor:case04:{eid.lower()}", "common_mode_group":f"group:case04:{eid.lower()}",
        "lineage":[f"general-record:root:case04:{eid.lower()}", f"general-record:origin:case04:{eid.lower()}"],
        "dependencies":deps,
    }
    draft=c.draft_evidence_record(
        evidence_id=eid, subject="DemoSubject", predicate="state", value="safe", source=f"display:case04:{eid.lower()}",
        identity_registry_entry_id="id:demo-subject:v1", authority_id="GENERAL_RECORD_V5",
        authority_record_entity_id="entity:demo-subject", authority_record_event_id="event:current", authority_record_version_id="v1",
        valid_from="2026-01-01", valid_to="2026-12-31", observed_at=ASOF, available_at=ASOF,
        provenance=provenance, polarity=polarity, source_semantics_id=sem_id,
    )
    c.verify_evidence_provenance(
        draft,
        ProvenanceAuthorityAttestation(f"att:case04:provenance:{eid}", AUTHORITIES["PROVENANCE"], eid, c.provenance_commitment(draft), ASOF, "2026-01-01", "2026-12-31"),
        verifiers["PROVENANCE"], as_of=ASOF,
    )
    c.verify_evidence_authority(
        draft,
        EvidenceAuthorityAttestation(f"att:case04:evidence:{eid}", AUTHORITIES["EVIDENCE_AUTHORITY"], eid, "GENERAL_RECORD_V5", c.evidence_authority_commitment(draft), ASOF, "2026-01-01", "2026-12-31"),
        verifiers["EVIDENCE_AUTHORITY"], as_of=ASOF,
    )
    role=c.draft_epistemic_role(draft, epistemic_role="DIRECT_WORLD_RECORD")
    role_install=c.install_verified_epistemic_role(
        draft, role,
        EpistemicRoleAuthorityAttestation(f"att:case04:role:{eid}", AUTHORITIES["EPISTEMIC_ROLE"], eid, "DIRECT_WORLD_RECORD", role.role_commitment, ASOF, "2026-01-01", "2026-12-31"),
        verifiers["EPISTEMIC_ROLE"], as_of=ASOF,
    )
    installed=c.evidence_with_epistemic_role(draft, role_install)
    return installed, c.evidence_record_mapping(installed)

pairs=[trusted_record("E1", "POSITIVE"), trusted_record("E2", "POSITIVE"), trusted_record("E3", "POSITIVE")]
drafts=[x[0] for x in pairs]
records=[x[1] for x in pairs]
snapshot=c.draft_snapshot(
    records, scope_id="scope:demo:case04", snapshot_id="snapshot:demo:case04", snapshot_created_at=ASOF, snapshot_available_at=ASOF, valid_from="2026-01-01", valid_to="2026-12-31",
)
c.install_verified_snapshot(
    snapshot, records,
    RetrievalAuthorityAttestation("att:case04:retrieval", AUTHORITIES["RETRIEVAL"], c.snapshot_commitment(snapshot), ASOF, "2026-01-01", "2026-12-31"),
    verifiers["RETRIEVAL"], as_of=ASOF,
)

TEXT="DemoSubject is safe."
CLAIM_MAP={"c1":"id:demo-subject:v1"}
REQ={"c1":{"required_independent_supports":2}}
SCOPE="scope:demo:case04"

# E1 + E2 are the selected independent supports.
ssi=c.draft_support_set_independence(
    independence_id="ssi:case04:selected", claim_id="c1", retrieval_scope_id=SCOPE, evidence_ids=["E1","E2"],
    reason="Synthetic authority verifies E1 and E2 as an independent selected support set.", as_of_date=ASOF,
)
ssi_att=SupportSetIndependenceAuthorityAttestation(
    "att:case04:ssi", AUTHORITIES["SUPPORT_SET_INDEPENDENCE"], c.support_set_independence_commitment(ssi,drafts[:2]), ASOF, "2026-01-01", "2026-12-31"
)
c.install_verified_support_set_independence(ssi,drafts[:2],ssi_att,verifiers["SUPPORT_SET_INDEPENDENCE"],as_of=ASOF)

# E3 is matching evidence but shares an explicitly modeled redundancy/common-mode relation with E2.
relation=c.draft_support_relation(
    relation_id="rel:case04:e2-e3-redundancy", relation_type="COMMON_MODE", evidence_ids=["E2","E3"],
    reason="Synthetic authority identifies E2 and E3 as redundant/common-mode supports.",
    relation_effect="REDUNDANCY_ONLY", claim_id="c1", retrieval_scope_id=SCOPE,
)
rel_att=SupportRelationAuthorityAttestation(
    "att:case04:support-relation", AUTHORITIES["SUPPORT_RELATION"], c.support_relation_commitment(relation,drafts[1:]), ASOF, "2026-01-01", "2026-12-31"
)
c.install_verified_support_relation(relation,drafts[1:],rel_att,verifiers["SUPPORT_RELATION"],as_of=ASOF)

selection=c.draft_support_selection(
    selection_id="sel:case04", claim_id="c1", retrieval_scope_id=SCOPE,
    matching_evidence_ids=["E1","E2","E3"], selected_support_ids=["E1","E2"], required_supports=2,
    exclusion_classifications={"E3":"EXCLUDED_REDUNDANT"},
    exclusion_reasons={"E3":"E3 is explicitly redundant with selected support E2 and is not counted again."},
    justification_reason="Select two independent supports and explicitly account for the third redundant support.",
    text=TEXT,evidence=drafts,claim_identity_map=CLAIM_MAP,as_of=ASOF,requirements=REQ,
)
sel_att=SupportSelectionAuthorityAttestation(
    "att:case04:support-selection", AUTHORITIES["SUPPORT_SELECTION"], c.support_selection_commitment(selection,drafts), ASOF, "2026-01-01", "2026-12-31"
)
c.install_verified_support_selection(selection,drafts,sel_att,verifiers["SUPPORT_SELECTION"],text=TEXT,claim_identity_map=CLAIM_MAP,as_of=ASOF,requirements=REQ)

resolution=c.draft_relation_resolution(
    resolution_id="rr:case04:e2-e3", relation_id="rel:case04:e2-e3-redundancy", claim_id="c1", retrieval_scope_id=SCOPE,
    selected_support_ids=["E1","E2"], resolution_type="REDUNDANT_RELATION_ACCOUNTED",
    justification_reason="The E2/E3 redundancy is explicitly accounted and E3 is not double-counted as independent support.",
    text=TEXT,evidence=drafts,claim_identity_map=CLAIM_MAP,as_of=ASOF,requirements=REQ,
)
rr_att=RelationResolutionAuthorityAttestation(
    "att:case04:relation-resolution", AUTHORITIES["RELATION_RESOLUTION"], c.relation_resolution_commitment(resolution,drafts), ASOF, "2026-01-01", "2026-12-31"
)
c.install_verified_relation_resolution(resolution,drafts,rr_att,verifiers["RELATION_RESOLUTION"],text=TEXT,claim_identity_map=CLAIM_MAP,as_of=ASOF,requirements=REQ)

disposition=c.draft_excluded_support_disposition(
    disposition_id="disp:case04:e3", claim_id="c1", retrieval_scope_id=SCOPE, excluded_evidence_id="E3",
    selected_evidence_ids=["E1","E2"], supporting_relation_ids=["rel:case04:e2-e3-redundancy"],
    justification_reason="E3 is a certified redundant exclusion supported by the exact E2/E3 redundancy relation and its resolution.",
    text=TEXT,evidence=drafts,claim_identity_map=CLAIM_MAP,as_of=ASOF,requirements=REQ,
)
disp_att=ExcludedSupportDispositionAuthorityAttestation(
    "att:case04:excluded-disposition", AUTHORITIES["EXCLUDED_SUPPORT_DISPOSITION"], c.excluded_support_disposition_commitment(disposition,drafts), ASOF, "2026-01-01", "2026-12-31"
)
c.install_verified_excluded_support_disposition(disposition,drafts,disp_att,verifiers["EXCLUDED_SUPPORT_DISPOSITION"],text=TEXT,claim_identity_map=CLAIM_MAP,as_of=ASOF,requirements=REQ)

bound=c.finalize_verified_decision_authorities_for_prepare(TEXT,drafts,CLAIM_MAP,as_of=ASOF,retrieval_scope=SCOPE,requirements=REQ)
result=c.evaluate_snapshot(snapshot,TEXT,records,CLAIM_MAP,as_of=ASOF,requirements=REQ)
summary={
    "case_id":"CASE_04_REDUNDANCY_VALID_RESOLUTION",
    "engine_sha256":c.controller_sha256,
    "mandatory_gate_count":c.mandatory_gate_count,
    "persistence_schema":c.persistence_schema,
    "model_conclusion":"DemoSubject is safe.",
    "selected_support_ids":["E1","E2"],
    "excluded_redundant_id":"E3",
    "relation_effect":"REDUNDANCY_ONLY",
    "resolution_type":"REDUNDANT_RELATION_ACCOUNTED",
    "bound_relation_resolution_ids":list(bound),
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
    "support_selection_certificates":result.raw.get("support_selection_certificates", []),
    "claim_support_universe_coverage_certificates":result.raw.get("claim_support_universe_coverage_certificates", []),
    "excluded_support_disposition_certificates":result.raw.get("excluded_support_disposition_certificates", []),
    "decision_support_closure_certificate":result.raw.get("decision_support_closure_certificate"),
    "raw_keys":sorted(result.raw.keys()),
    "critical_unresolved":result.raw.get("critical_unresolved", []),
    "claim_support_policy_violations":result.raw.get("claim_support_policy_violations", []),
    "constraint_relation_coverage_violations":result.raw.get("constraint_relation_coverage_violations", []),
    "constraint_coverage_violations":result.raw.get("constraint_coverage_violations", []),
}
print(json.dumps(summary,indent=2,sort_keys=True))
