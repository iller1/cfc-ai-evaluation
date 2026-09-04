from __future__ import annotations
import json, sys
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
)

ASOF = "2026-09-03"
VALID_FROM = "2026-01-01"
VALID_TO = "2026-12-31"
STALE_TO = "2026-08-31"

ALLOWED = {
    "conclusion": {"POSITIVE", "NEGATIVE"},
    "polarity": {"POSITIVE", "NEGATIVE", "OMIT"},
    "validity": {"CURRENT", "STALE"},
    "provenance_shape": {"DISTINCT", "SHARED_LINEAGE"},
    "independence_authority": {"NONE", "VERIFIED"},
    "scope": {"EXPECTED", "WRONG"},
}

def fail(msg: str):
    print(json.dumps({"error": msg}, indent=2)); raise SystemExit(2)

def validate(cfg):
    if not isinstance(cfg, dict): fail("custom input must be a JSON object")
    conclusion = cfg.get("conclusion", "POSITIVE")
    if conclusion not in ALLOWED["conclusion"]: fail("invalid conclusion")
    required = cfg.get("required_independent_supports", 1)
    if required not in (1, 2): fail("required_independent_supports must be 1 or 2")
    provenance_shape = cfg.get("provenance_shape", "DISTINCT")
    if provenance_shape not in ALLOWED["provenance_shape"]: fail("invalid provenance_shape")
    independence_authority = cfg.get("independence_authority", "NONE")
    if independence_authority not in ALLOWED["independence_authority"]: fail("invalid independence_authority")
    scope = cfg.get("scope", "EXPECTED")
    if scope not in ALLOWED["scope"]: fail("invalid scope")
    evidence = cfg.get("evidence")
    if not isinstance(evidence, list) or not (1 <= len(evidence) <= 2): fail("evidence must contain 1 or 2 records")
    out=[]
    for i,row in enumerate(evidence,1):
        if not isinstance(row, dict): fail(f"evidence {i} must be an object")
        polarity=row.get("polarity","POSITIVE")
        validity=row.get("validity","CURRENT")
        if polarity not in ALLOWED["polarity"]: fail(f"invalid polarity for evidence {i}")
        if validity not in ALLOWED["validity"]: fail(f"invalid validity for evidence {i}")
        if polarity != "OMIT": out.append({"polarity":polarity,"validity":validity})
    if not out: fail("at least one evidence record must be included")
    return {"conclusion": conclusion, "required_independent_supports": required, "provenance_shape": provenance_shape, "independence_authority": independence_authority, "scope": scope, "evidence": out}

class VIdentity:
    def verify(self,a,*,draft): return IdentityAuthorityVerdict(True,"custom:id:v1",a.attestation_id,a.authority_id,"SYNTHETIC_CUSTOM_FIXTURE")
class VSource:
    def verify(self,a,*,draft): return SourceSemanticsAuthorityVerdict(True,"custom:ss:v1",a.attestation_id,a.authority_id,"SYNTHETIC_CUSTOM_FIXTURE")
class VProv:
    def verify(self,a,*,draft): return ProvenanceAuthorityVerdict(True,"custom:prov:v1",a.attestation_id,a.authority_id,a.evidence_id,"SYNTHETIC_CUSTOM_FIXTURE")
class VEvidence:
    def verify(self,a,*,draft): return EvidenceAuthorityVerdict(True,"custom:ev:v1",a.attestation_id,a.authority_id,a.evidence_id,"SYNTHETIC_CUSTOM_FIXTURE")
class VRole:
    def verify(self,a,*,draft,evidence): return EpistemicRoleAuthorityVerdict(True,"custom:role:v1",a.attestation_id,a.authority_id,a.evidence_id,a.epistemic_role,"SYNTHETIC_CUSTOM_FIXTURE")
class VRetrieval:
    def verify(self,a,*,draft,evidence): return RetrievalAuthorityVerdict(True,"custom:ret:v1",a.attestation_id,a.authority_id,"SYNTHETIC_CUSTOM_FIXTURE")
class VTopology:
    def verify(self,a,*,draft): return FailureDomainTopologyVerdict(True,"custom:topo:v1",a.attestation_id,a.authority_id,a.topology_commitment,"SYNTHETIC_CUSTOM_FIXTURE")
class VSupportSetIndependence:
    def verify(self,a,*,draft,evidence): return SupportSetIndependenceAuthorityVerdict(True,"custom:ssi:v1",a.attestation_id,a.authority_id,draft.independence_id,"SYNTHETIC_CUSTOM_FIXTURE")

AUTHORITIES={
    "IDENTITY":"DEMO_CUSTOM_IDENTITY_AUTHORITY",
    "SOURCE_SEMANTICS":"DEMO_CUSTOM_SOURCE_SEMANTICS_AUTHORITY",
    "PROVENANCE":"DEMO_CUSTOM_PROVENANCE_AUTHORITY",
    "EVIDENCE_AUTHORITY":"DEMO_CUSTOM_EVIDENCE_AUTHORITY",
    "EPISTEMIC_ROLE":"DEMO_CUSTOM_EPISTEMIC_ROLE_AUTHORITY",
    "RETRIEVAL":"DEMO_CUSTOM_RETRIEVAL_AUTHORITY",
    "FAILURE_DOMAIN_TOPOLOGY":"DEMO_CUSTOM_FAILURE_DOMAIN_TOPOLOGY_AUTHORITY",
    "SUPPORT_SET_INDEPENDENCE":"DEMO_CUSTOM_SUPPORT_SET_INDEPENDENCE_AUTHORITY",
}
VERIFIERS={
    "IDENTITY":VIdentity(),"SOURCE_SEMANTICS":VSource(),"PROVENANCE":VProv(),
    "EVIDENCE_AUTHORITY":VEvidence(),"EPISTEMIC_ROLE":VRole(),"RETRIEVAL":VRetrieval(),
    "FAILURE_DOMAIN_TOPOLOGY":VTopology(),
    "SUPPORT_SET_INDEPENDENCE":VSupportSetIndependence(),
}

def execute(cfg):
    cfg=validate(cfg)
    trust=HostTrustPolicy(tuple(HostTrustRegistration(k,AUTHORITIES[k],VERIFIERS[k]) for k in AUTHORITIES))
    c=Controller(scope=("IGNORE" if cfg["scope"]=="WRONG" else None), trust_policy=trust)
    identity=c.draft_identity(
        registry_entry_id="id:demo-subject:v1", surface_subject="DemoSubject", domain_id="GENERAL_ENTITY",
        entity_id="entity:demo-subject", event_id="event:current", version_id="v1")
    c.install_verified_identity(identity,
        IdentityAuthorityAttestation("att:custom:identity",AUTHORITIES["IDENTITY"],c.identity_commitment(identity),ASOF,VALID_FROM,VALID_TO),
        VERIFIERS["IDENTITY"],as_of=ASOF)

    topology=c.draft_failure_domain_topology()
    c.install_verified_failure_domain_topology(topology,
        FailureDomainTopologyAttestation("att:custom:topology",AUTHORITIES["FAILURE_DOMAIN_TOPOLOGY"],c.failure_domain_topology_commitment(topology),ASOF,VALID_FROM,VALID_TO),
        VERIFIERS["FAILURE_DOMAIN_TOPOLOGY"],as_of=ASOF)

    prefix={"data_source":"data","sensor_input":"sensor","transform":"transform","model":"model","extractor":"extractor","cache":"cache","upstream_db":"db","operator":"operator","preprocessing":"prep","runtime":"runtime"}
    records=[]
    draft_records=[]
    for idx,row in enumerate(cfg["evidence"],1):
        eid=f"E{idx}"; token=f"custom:e{idx}"
        shared=(cfg["provenance_shape"]=="SHARED_LINEAGE" and len(cfg["evidence"])>1)
        semantic_token="shared" if shared else token
        sem_id=f"sem:{token}"
        semantics=c.draft_source_semantics(
            semantics_registry_entry_id=sem_id, source_id=f"general-record:{token}",
            repository_id=f"repo:{semantic_token}", producer_id=f"producer:{semantic_token}", process_id=f"process:{semantic_token}",
            failure_domain_id=f"fd:{semantic_token}", resolution_state="KNOWN")
        c.install_verified_source_semantics(semantics,
            SourceSemanticsAuthorityAttestation(f"att:{token}:semantics",AUTHORITIES["SOURCE_SEMANTICS"],c.source_semantics_commitment(semantics),ASOF,VALID_FROM,VALID_TO),
            VERIFIERS["SOURCE_SEMANTICS"],as_of=ASOF)
        dep_token="shared" if shared else token
        dependencies={k:{"state":"KNOWN","id":f"{v}:{dep_token}"} for k,v in prefix.items()}
        provenance={
            "source_id":f"general-record:{token}",
            "root_origin_id":f"general-record:root:{dep_token}",
            "origin_id":f"general-record:origin:{dep_token}",
            "referent_entity_id":"entity:demo-subject","referent_event_id":"event:current","referent_version_id":"v1",
            "extractor_id":f"extractor:{dep_token}","common_mode_group":f"group:{dep_token}",
            "lineage":[f"general-record:root:{dep_token}",f"general-record:origin:{dep_token}"],"dependencies":dependencies}
        valid_to=STALE_TO if row["validity"]=="STALE" else VALID_TO
        observed_at="2026-08-30" if row["validity"]=="STALE" else ASOF
        evidence=c.draft_evidence_record(
            evidence_id=eid, subject="DemoSubject", predicate="state", value="safe", source=f"display:{token}",
            identity_registry_entry_id="id:demo-subject:v1", authority_id="GENERAL_RECORD_V5",
            authority_record_entity_id="entity:demo-subject", authority_record_event_id="event:current", authority_record_version_id="v1",
            valid_from=VALID_FROM, valid_to=valid_to, observed_at=observed_at, available_at=observed_at,
            provenance=provenance, polarity=row["polarity"], source_semantics_id=sem_id)
        c.verify_evidence_provenance(evidence,
            ProvenanceAuthorityAttestation(f"att:{token}:prov",AUTHORITIES["PROVENANCE"],eid,c.provenance_commitment(evidence),ASOF,VALID_FROM,VALID_TO),
            VERIFIERS["PROVENANCE"],as_of=ASOF)
        c.verify_evidence_authority(evidence,
            EvidenceAuthorityAttestation(f"att:{token}:evidence",AUTHORITIES["EVIDENCE_AUTHORITY"],eid,"GENERAL_RECORD_V5",c.evidence_authority_commitment(evidence),ASOF,VALID_FROM,VALID_TO),
            VERIFIERS["EVIDENCE_AUTHORITY"],as_of=ASOF)
        role=c.draft_epistemic_role(evidence,epistemic_role="DIRECT_WORLD_RECORD")
        role_installation=c.install_verified_epistemic_role(evidence,role,
            EpistemicRoleAuthorityAttestation(f"att:{token}:role",AUTHORITIES["EPISTEMIC_ROLE"],eid,"DIRECT_WORLD_RECORD",role.role_commitment,ASOF,VALID_FROM,VALID_TO),
            VERIFIERS["EPISTEMIC_ROLE"],as_of=ASOF)
        evidence=c.evidence_with_epistemic_role(evidence,role_installation)
        draft_records.append(evidence)
        records.append(c.evidence_record_mapping(evidence))

    snapshot=c.draft_snapshot(records,scope_id="scope:demo:custom",snapshot_id="snapshot:demo:custom",snapshot_created_at=ASOF,snapshot_available_at=ASOF,valid_from=VALID_FROM,valid_to=VALID_TO)
    c.install_verified_snapshot(snapshot,records,
        RetrievalAuthorityAttestation("att:custom:retrieval",AUTHORITIES["RETRIEVAL"],c.snapshot_commitment(snapshot),ASOF,VALID_FROM,VALID_TO),
        VERIFIERS["RETRIEVAL"],as_of=ASOF)

    # Optional host-provided independence authority state. The adapter does not infer
    # independence from distinct-looking IDs; it installs this certificate only when
    # the user explicitly selects VERIFIED in the custom state builder.
    if cfg["independence_authority"]=="VERIFIED" and len(records)==2:
        ssi=c.draft_support_set_independence(
            independence_id="ssi:custom:e1-e2", claim_id="c1", retrieval_scope_id="scope:demo:custom", evidence_ids=["E1","E2"],
            reason="Synthetic custom fixture: host independence authority explicitly certifies E1/E2.", as_of_date=ASOF)
        ssi_att=SupportSetIndependenceAuthorityAttestation(
            "att:custom:ssi",AUTHORITIES["SUPPORT_SET_INDEPENDENCE"],c.support_set_independence_commitment(ssi,[*draft_records]),ASOF,VALID_FROM,VALID_TO)
        c.install_verified_support_set_independence(ssi,[*draft_records],ssi_att,VERIFIERS["SUPPORT_SET_INDEPENDENCE"],as_of=ASOF)

    conclusion="DemoSubject is safe." if cfg["conclusion"]=="POSITIVE" else "DemoSubject is not safe."
    result=c.evaluate_snapshot(snapshot,conclusion,records,{"c1":"id:demo-subject:v1"},as_of=ASOF,requirements={"c1":{"required_independent_supports":cfg["required_independent_supports"]}})
    return {
        "case_id":"CUSTOM_CASE", "input_schema_version":"1", "custom_input":cfg,
        "engine_sha256":c.controller_sha256,"mandatory_gate_count":c.mandatory_gate_count,"persistence_schema":c.persistence_schema,
        "model_conclusion":conclusion,"evidence":records,"claim_states":result.claims,"stop_type":result.stop_type,
        "control_closure":result.control_closure,"gates":result.gates,
        "evidence_errors":result.raw.get("evidence_errors",[]),"identity_errors":result.raw.get("identity_errors",[]),
        "integration_errors":result.raw.get("integration_errors",[]),"critical_unresolved":result.raw.get("critical_unresolved",[]),
        "claim_support_policy_violations":result.raw.get("claim_support_policy_violations",[]),
        "constraint_relation_coverage_violations":result.raw.get("constraint_relation_coverage_violations",[]),
        "constraint_coverage_violations":result.raw.get("constraint_coverage_violations",[]),
        "global_consistency_violations":result.raw.get("global_consistency_violations",[]),
    }

if __name__=="__main__":
    try:
        cfg=json.load(sys.stdin)
        print(json.dumps(execute(cfg),indent=2,sort_keys=True))
    except SystemExit: raise
    except Exception as e:
        print(json.dumps({"error":f"{type(e).__name__}: {e}"},indent=2)); raise SystemExit(1)
