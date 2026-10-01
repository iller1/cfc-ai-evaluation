from __future__ import annotations

import hashlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any

from cfc_anchor import (
    Controller,
    HostTrustPolicy,
    HostTrustRegistration,
    IdentityAuthorityAttestation,
    IdentityAuthorityVerdict,
    SourceSemanticsAuthorityAttestation,
    SourceSemanticsAuthorityVerdict,
    ProvenanceAuthorityAttestation,
    ProvenanceAuthorityVerdict,
    EvidenceAuthorityAttestation,
    EvidenceAuthorityVerdict,
    EpistemicRoleAuthorityAttestation,
    EpistemicRoleAuthorityVerdict,
    RetrievalAuthorityAttestation,
    RetrievalAuthorityVerdict,
    FailureDomainTopologyAttestation,
    FailureDomainTopologyVerdict,
    SupportSetIndependenceAuthorityAttestation,
    SupportSetIndependenceAuthorityVerdict,
)

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
ADAPTER_PATH = REPO_ROOT / "collaboration/cfc-ridi/v0.2/f2_adapter/adapter.py"
WHEEL_PATH = REPO_ROOT / "demonstrator/cfc_anchor-0.2.90rc1-py3-none-any.whl"

SPEC = importlib.util.spec_from_file_location("f3_frozen_adapter", ADAPTER_PATH)
assert SPEC and SPEC.loader
adapter = importlib.util.module_from_spec(SPEC)
sys.modules["f3_frozen_adapter"] = adapter
SPEC.loader.exec_module(adapter)

ASOF = "2026-09-03"
VALID_FROM = "2026-01-01"
VALID_TO = "2026-12-31"
STALE_TO = "2026-08-31"

AUTHORITIES = {
    "IDENTITY": "F3_FIXTURE_IDENTITY_AUTHORITY",
    "SOURCE_SEMANTICS": "F3_FIXTURE_SOURCE_SEMANTICS_AUTHORITY",
    "PROVENANCE": "F3_FIXTURE_PROVENANCE_AUTHORITY",
    "EVIDENCE_AUTHORITY": "F3_FIXTURE_EVIDENCE_AUTHORITY",
    "EPISTEMIC_ROLE": "F3_FIXTURE_EPISTEMIC_ROLE_AUTHORITY",
    "RETRIEVAL": "F3_FIXTURE_RETRIEVAL_AUTHORITY",
    "FAILURE_DOMAIN_TOPOLOGY": "F3_FIXTURE_FAILURE_DOMAIN_TOPOLOGY_AUTHORITY",
    "SUPPORT_SET_INDEPENDENCE": "F3_FIXTURE_SUPPORT_SET_INDEPENDENCE_AUTHORITY",
}


class VIdentity:
    def verify(self, a, *, draft):
        return IdentityAuthorityVerdict(
            True, "f3:id:v1", a.attestation_id, a.authority_id, "F3_TEST_FIXTURE"
        )


class VSource:
    def verify(self, a, *, draft):
        return SourceSemanticsAuthorityVerdict(
            True, "f3:ss:v1", a.attestation_id, a.authority_id, "F3_TEST_FIXTURE"
        )


class VProv:
    def verify(self, a, *, draft):
        return ProvenanceAuthorityVerdict(
            True,
            "f3:prov:v1",
            a.attestation_id,
            a.authority_id,
            a.evidence_id,
            "F3_TEST_FIXTURE",
        )


class VEvidence:
    def verify(self, a, *, draft):
        return EvidenceAuthorityVerdict(
            True,
            "f3:ev:v1",
            a.attestation_id,
            a.authority_id,
            a.evidence_id,
            "F3_TEST_FIXTURE",
        )


class VRole:
    def verify(self, a, *, draft, evidence):
        return EpistemicRoleAuthorityVerdict(
            True,
            "f3:role:v1",
            a.attestation_id,
            a.authority_id,
            a.evidence_id,
            a.epistemic_role,
            "F3_TEST_FIXTURE",
        )


class VRetrieval:
    def verify(self, a, *, draft, evidence):
        return RetrievalAuthorityVerdict(
            True,
            "f3:ret:v1",
            a.attestation_id,
            a.authority_id,
            "F3_TEST_FIXTURE",
        )


class VTopology:
    def verify(self, a, *, draft):
        return FailureDomainTopologyVerdict(
            True,
            "f3:topo:v1",
            a.attestation_id,
            a.authority_id,
            a.topology_commitment,
            "F3_TEST_FIXTURE",
        )


class VSupportSetIndependence:
    def verify(self, a, *, draft, evidence):
        return SupportSetIndependenceAuthorityVerdict(
            True,
            "f3:ssi:v1",
            a.attestation_id,
            a.authority_id,
            draft.independence_id,
            "F3_TEST_FIXTURE",
        )


VERIFIERS = {
    "IDENTITY": VIdentity(),
    "SOURCE_SEMANTICS": VSource(),
    "PROVENANCE": VProv(),
    "EVIDENCE_AUTHORITY": VEvidence(),
    "EPISTEMIC_ROLE": VRole(),
    "RETRIEVAL": VRetrieval(),
    "FAILURE_DOMAIN_TOPOLOGY": VTopology(),
    "SUPPORT_SET_INDEPENDENCE": VSupportSetIndependence(),
}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _kwargs_for(cls, *positional_values) -> dict[str, Any]:
    sig = inspect.signature(cls)
    names = [
        name
        for name, p in sig.parameters.items()
        if p.kind
        in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
    ]
    if len(positional_values) > len(names):
        raise RuntimeError(
            f"too many values for {cls.__name__}: {len(positional_values)} > {len(names)}"
        )
    return dict(zip(names, positional_values))


def make_neutral_arm(
    *,
    case_id: str = "F3-CASE-A",
    arm: str = "A",
    dataset: str = "nq",
    task: str = "qa",
    draw: int = 0,
    passage_namespace: str = "shared",
    canonical: str = "DemoSubject is safe.",
) -> dict[str, Any]:
    question = (
        "Is DemoSubject safe?"
        if task == "qa"
        else "DemoSubject has the property safe."
    )
    passages = []
    for i in range(1, 11):
        text = f"F3 registered passage {passage_namespace} {i}"
        passages.append(
            {
                "ordinal": i,
                "docid": f"doc:{passage_namespace}:{i}",
                "text": text,
                "text_sha256": sha_text(text),
            }
        )
    return {
        "schema_version": adapter.NEUTRAL_SCHEMA_VERSION,
        "case_id": case_id,
        "arm": arm,
        "dataset": dataset,
        "task": task,
        "draw": draw,
        "query": {
            "qid": f"qid:{case_id}",
            "source_qid": f"source-qid:{case_id}",
            "question": question,
            "question_sha256": sha_text(question),
        },
        "source_binding": {
            "registered_context_line_sha256": sha_text(
                f"context-line:{case_id}:{arm}"
            ),
            "source_contexts_corpus_sha256": adapter.SOURCE_CORPUS_SHA256,
            "source_registration": f"registration:{dataset}",
            "prompt_sha256": sha_text(f"prompt:{case_id}:{arm}"),
        },
        "passages": passages,
        "recorded_endpoint": {
            "endpoint_record_sha256": sha_text(f"endpoint:{case_id}:{arm}"),
            "raw": canonical,
            "canonical": canonical,
            "model": "F3FixtureModel",
            "revision": "f3-fixture-revision",
            "source_generations_sha256": sha_text("f3-fixture-generations"),
            "source_result_archive": "F3_FIXTURE_ONLY",
        },
        "neutrality": {
            "adapter_unit": "ONE_ARM_ONLY",
            "candidate_claim_source": "recorded_endpoint.canonical",
            "endpoint_is_candidate_claim_only": True,
            "authority_asserted_by_schema": False,
            "semantic_support_asserted_by_schema": False,
            "ground_truth_withheld": True,
            "retrieval_grade_withheld": True,
            "prompt_text_withheld": True,
            "perturbation_condition_withheld": True,
            "counterpart_arm_withheld": True,
            "ridi_result_withheld": True,
            "correctness_withheld": True,
        },
    }


def _trust_rows() -> list[dict[str, Any]]:
    return [
        {
            "authority_class": k,
            "authority_id": AUTHORITIES[k],
            "verifier": VERIFIERS[k],
        }
        for k in AUTHORITIES
    ]


def _trust_policy(rows: list[dict[str, Any]]) -> HostTrustPolicy:
    return HostTrustPolicy(
        tuple(
            HostTrustRegistration(
                r["authority_class"], r["authority_id"], r["verifier"]
            )
            for r in rows
        )
    )


def build_resolved_state(
    payload: dict[str, Any],
    *,
    tag: str = "base",
    shared_lineage: bool = False,
    required_independent_supports: int = 1,
    install_independence: bool = False,
    controller_scope: str | None = None,
    snapshot_scope: str = "scope:f3:expected",
    claim_relevant_count: int = 10,
) -> dict[str, Any]:
    if not 1 <= claim_relevant_count <= 10:
        raise ValueError("claim_relevant_count must be 1..10")
    adapter.validate_neutral_arm(payload)
    rows = _trust_rows()
    trust = _trust_policy(rows)
    c = Controller(scope=controller_scope, trust_policy=trust)

    identity_id = f"id:demo-subject:{tag}:v1"
    identity_draft = {
        "registry_entry_id": identity_id,
        "surface_subject": "DemoSubject",
        "domain_id": "GENERAL_ENTITY",
        "entity_id": "entity:demo-subject",
        "event_id": "event:current",
        "version_id": "v1",
    }
    identity = c.draft_identity(**identity_draft)
    identity_att_kwargs = _kwargs_for(
        IdentityAuthorityAttestation,
        f"att:f3:{tag}:identity",
        AUTHORITIES["IDENTITY"],
        c.identity_commitment(identity),
        ASOF,
        VALID_FROM,
        VALID_TO,
    )
    identity_att = IdentityAuthorityAttestation(**identity_att_kwargs)
    c.install_verified_identity(
        identity, identity_att, VERIFIERS["IDENTITY"], as_of=ASOF
    )

    topology_draft: dict[str, Any] = {}
    topology = c.draft_failure_domain_topology(**topology_draft)
    topology_att_kwargs = _kwargs_for(
        FailureDomainTopologyAttestation,
        f"att:f3:{tag}:topology",
        AUTHORITIES["FAILURE_DOMAIN_TOPOLOGY"],
        c.failure_domain_topology_commitment(topology),
        ASOF,
        VALID_FROM,
        VALID_TO,
    )
    topology_att = FailureDomainTopologyAttestation(**topology_att_kwargs)
    c.install_verified_failure_domain_topology(
        topology,
        topology_att,
        VERIFIERS["FAILURE_DOMAIN_TOPOLOGY"],
        as_of=ASOF,
    )

    resolved_passages = []
    evidence_objects = []
    evidence_mappings = []
    dep_prefix = {
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

    for idx, neutral in enumerate(payload["passages"], 1):
        token = f"{tag}:e{idx}"
        dep = f"{tag}:shared" if shared_lineage else token

        semantics_draft = {
            "semantics_registry_entry_id": f"sem:{token}",
            "source_id": f"general-record:{token}",
            "repository_id": f"repo:{dep}",
            "producer_id": f"producer:{dep}",
            "process_id": f"process:{dep}",
            "failure_domain_id": f"fd:{dep}",
            "resolution_state": "KNOWN",
        }
        semantics = c.draft_source_semantics(**semantics_draft)
        semantics_att_kwargs = _kwargs_for(
            SourceSemanticsAuthorityAttestation,
            f"att:{token}:semantics",
            AUTHORITIES["SOURCE_SEMANTICS"],
            c.source_semantics_commitment(semantics),
            ASOF,
            VALID_FROM,
            VALID_TO,
        )
        semantics_att = SourceSemanticsAuthorityAttestation(
            **semantics_att_kwargs
        )
        c.install_verified_source_semantics(
            semantics,
            semantics_att,
            VERIFIERS["SOURCE_SEMANTICS"],
            as_of=ASOF,
        )

        dependencies = {
            k: {"state": "KNOWN", "id": f"{v}:{dep}"}
            for k, v in dep_prefix.items()
        }
        provenance = {
            "source_id": f"general-record:{token}",
            "root_origin_id": f"general-record:root:{dep}",
            "origin_id": f"general-record:origin:{dep}",
            "referent_entity_id": "entity:demo-subject",
            "referent_event_id": "event:current",
            "referent_version_id": "v1",
            "extractor_id": f"extractor:{dep}",
            "common_mode_group": f"group:{dep}",
            "lineage": [
                f"general-record:root:{dep}",
                f"general-record:origin:{dep}",
            ],
            "dependencies": dependencies,
        }
        claim_relevant = idx <= claim_relevant_count
        evidence_draft = {
            "evidence_id": f"{tag}:E{idx}",
            "subject": "DemoSubject",
            "predicate": "state" if claim_relevant else f"context_{idx}",
            "value": "safe" if claim_relevant else f"auxiliary_{idx}",
            "source": f"display:{token}",
            "identity_registry_entry_id": identity_id,
            "authority_id": "GENERAL_RECORD_V5",
            "authority_record_entity_id": "entity:demo-subject",
            "authority_record_event_id": "event:current",
            "authority_record_version_id": "v1",
            "valid_from": VALID_FROM,
            "valid_to": VALID_TO,
            "observed_at": ASOF,
            "available_at": ASOF,
            "provenance": provenance,
            "polarity": "POSITIVE",
            "source_semantics_id": semantics_draft[
                "semantics_registry_entry_id"
            ],
        }
        evidence = c.draft_evidence_record(**evidence_draft)

        prov_att_kwargs = _kwargs_for(
            ProvenanceAuthorityAttestation,
            f"att:{token}:prov",
            AUTHORITIES["PROVENANCE"],
            evidence_draft["evidence_id"],
            c.provenance_commitment(evidence),
            ASOF,
            VALID_FROM,
            VALID_TO,
        )
        prov_att = ProvenanceAuthorityAttestation(**prov_att_kwargs)
        c.verify_evidence_provenance(
            evidence, prov_att, VERIFIERS["PROVENANCE"], as_of=ASOF
        )

        evidence_att_kwargs = _kwargs_for(
            EvidenceAuthorityAttestation,
            f"att:{token}:evidence",
            AUTHORITIES["EVIDENCE_AUTHORITY"],
            evidence_draft["evidence_id"],
            evidence_draft["authority_id"],
            c.evidence_authority_commitment(evidence),
            ASOF,
            VALID_FROM,
            VALID_TO,
        )
        evidence_att = EvidenceAuthorityAttestation(**evidence_att_kwargs)
        c.verify_evidence_authority(
            evidence,
            evidence_att,
            VERIFIERS["EVIDENCE_AUTHORITY"],
            as_of=ASOF,
        )

        role_draft = {"epistemic_role": "DIRECT_WORLD_RECORD"}
        role = c.draft_epistemic_role(evidence, **role_draft)
        role_att_kwargs = _kwargs_for(
            EpistemicRoleAuthorityAttestation,
            f"att:{token}:role",
            AUTHORITIES["EPISTEMIC_ROLE"],
            evidence_draft["evidence_id"],
            role_draft["epistemic_role"],
            role.role_commitment,
            ASOF,
            VALID_FROM,
            VALID_TO,
        )
        role_att = EpistemicRoleAuthorityAttestation(**role_att_kwargs)
        role_installation = c.install_verified_epistemic_role(
            evidence,
            role,
            role_att,
            VERIFIERS["EPISTEMIC_ROLE"],
            as_of=ASOF,
        )
        evidence = c.evidence_with_epistemic_role(
            evidence, role_installation
        )

        evidence_objects.append(evidence)
        evidence_mappings.append(c.evidence_record_mapping(evidence))

        resolved_passages.append(
            {
                "neutral_binding": {
                    "ordinal": neutral["ordinal"],
                    "docid": neutral["docid"],
                    "text_sha256": neutral["text_sha256"],
                },
                "source_semantics": {
                    "draft_kwargs": semantics_draft,
                    "attestation_kwargs": semantics_att_kwargs,
                    "verifier": VERIFIERS["SOURCE_SEMANTICS"],
                },
                "evidence_draft_kwargs": evidence_draft,
                "provenance": {
                    "attestation_kwargs": prov_att_kwargs,
                    "verifier": VERIFIERS["PROVENANCE"],
                },
                "evidence_authority": {
                    "attestation_kwargs": evidence_att_kwargs,
                    "verifier": VERIFIERS["EVIDENCE_AUTHORITY"],
                },
                "epistemic_role": {
                    "draft_kwargs": role_draft,
                    "attestation_kwargs": role_att_kwargs,
                    "verifier": VERIFIERS["EPISTEMIC_ROLE"],
                },
            }
        )

    snapshot_draft = {
        "scope_id": snapshot_scope,
        "snapshot_id": f"snapshot:f3:{tag}",
        "snapshot_created_at": ASOF,
        "snapshot_available_at": ASOF,
        "valid_from": VALID_FROM,
        "valid_to": VALID_TO,
    }
    snapshot = c.draft_snapshot(evidence_mappings, **snapshot_draft)
    snapshot_att_kwargs = _kwargs_for(
        RetrievalAuthorityAttestation,
        f"att:f3:{tag}:retrieval",
        AUTHORITIES["RETRIEVAL"],
        c.snapshot_commitment(snapshot),
        ASOF,
        VALID_FROM,
        VALID_TO,
    )
    snapshot_att = RetrievalAuthorityAttestation(**snapshot_att_kwargs)
    c.install_verified_snapshot(
        snapshot,
        evidence_mappings,
        snapshot_att,
        VERIFIERS["RETRIEVAL"],
        as_of=ASOF,
    )

    ssi_spec = None
    if install_independence:
        ssi_draft = {
            "independence_id": f"ssi:f3:{tag}",
            "claim_id": "c1",
            "retrieval_scope_id": snapshot_scope,
            "evidence_ids": [
                f"{tag}:E{i}" for i in range(1, claim_relevant_count + 1)
            ],
            "reason": "F3 fixture-only explicit independence certificate.",
            "as_of_date": ASOF,
        }
        ssi = c.draft_support_set_independence(**ssi_draft)
        ssi_att_kwargs = _kwargs_for(
            SupportSetIndependenceAuthorityAttestation,
            f"att:f3:{tag}:ssi",
            AUTHORITIES["SUPPORT_SET_INDEPENDENCE"],
            c.support_set_independence_commitment(
                ssi, [*evidence_objects[:claim_relevant_count]]
            ),
            ASOF,
            VALID_FROM,
            VALID_TO,
        )
        ssi_att = SupportSetIndependenceAuthorityAttestation(
            **ssi_att_kwargs
        )
        c.install_verified_support_set_independence(
            ssi,
            evidence_objects[:claim_relevant_count],
            ssi_att,
            VERIFIERS["SUPPORT_SET_INDEPENDENCE"],
            as_of=ASOF,
        )
        ssi_spec = {
            "draft_kwargs": ssi_draft,
            "attestation_kwargs": ssi_att_kwargs,
            "verifier": VERIFIERS["SUPPORT_SET_INDEPENDENCE"],
        }

    return {
        "decision_as_of": ASOF,
        "controller_scope": controller_scope,
        "claim_identity_map": {"c1": identity_id},
        "requirements": {
            "c1": {
                "required_independent_supports": required_independent_supports
            }
        },
        "host_trust_registrations": rows,
        "identity": {
            "draft_kwargs": identity_draft,
            "attestation_kwargs": identity_att_kwargs,
            "verifier": VERIFIERS["IDENTITY"],
        },
        "failure_domain_topology": {
            "draft_kwargs": topology_draft,
            "attestation_kwargs": topology_att_kwargs,
            "verifier": VERIFIERS["FAILURE_DOMAIN_TOPOLOGY"],
        },
        "passages": resolved_passages,
        "snapshot": {
            "draft_kwargs": snapshot_draft,
            "attestation_kwargs": snapshot_att_kwargs,
            "verifier": VERIFIERS["RETRIEVAL"],
        },
        "support_set_independence": ssi_spec,
    }


def execute(payload: dict[str, Any], resolved: dict[str, Any]):
    return adapter.execute_with_resolved_state(
        payload, resolved, anchor_wheel_path=WHEEL_PATH
    )
