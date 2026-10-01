from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

ADAPTER_VERSION = "CFC-RIDI-F2-ADAPTER-v0.1"
ANCHOR_VERSION = "0.2.90rc1"
ANCHOR_WHEEL_SHA256 = "b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303"
ANCHOR_ENGINE_SHA256 = "77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0"
F1_INTERFACE_SHA256 = "b23719df7efd75dc4d53b33808377e1002a044a88acc5354defd06dc59829184"
NEUTRAL_SCHEMA_VERSION = "CFC-RIDI-NEUTRAL-ARM-v0.2-R1"
NEUTRAL_SCHEMA_SHA256 = "d609a6d6af94d1108048360a349edb612b65b95336d5f90e6874c4da022b60a0"
SOURCE_CORPUS_SHA256 = "1485c0ad114673d297c580080d11086d3ace8827f9b586b15ad3928c7d0b21a1"

F2_PRIMARY_NO_GO = "F2_NO_GO_API_OR_IMPLEMENTATION_BOUNDARY"
F2_REASON_API_INCOMPATIBLE = "API_INCOMPATIBLE"

_REQUIRED_ROOT = {
    "schema_version", "case_id", "arm", "dataset", "task", "draw", "query",
    "source_binding", "passages", "recorded_endpoint", "neutrality",
}
_REQUIRED_QUERY = {"qid", "source_qid", "question", "question_sha256"}
_REQUIRED_SOURCE_BINDING = {
    "registered_context_line_sha256", "source_contexts_corpus_sha256",
    "source_registration", "prompt_sha256",
}
_REQUIRED_ENDPOINT = {
    "endpoint_record_sha256", "raw", "canonical", "model", "revision",
    "source_generations_sha256",
}
_OPTIONAL_ENDPOINT = {"source_result_archive"}
_REQUIRED_NEUTRALITY = {
    "adapter_unit", "candidate_claim_source", "endpoint_is_candidate_claim_only",
    "authority_asserted_by_schema", "semantic_support_asserted_by_schema",
    "ground_truth_withheld", "retrieval_grade_withheld", "prompt_text_withheld",
    "perturbation_condition_withheld", "counterpart_arm_withheld",
    "ridi_result_withheld", "correctness_withheld",
}
_REQUIRED_PASSAGE = {"ordinal", "docid", "text", "text_sha256"}

_EXPECTED_NEUTRALITY = {
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
}

_ALLOWED_DATASETS = {"nq", "hotpotqa", "fever", "scifact"}
_ALLOWED_TASKS = {"qa", "verdict"}
_ALLOWED_ARMS = {"A", "B"}

_F1_PUBLIC_IMPORTS = (
    "Controller",
    "HostTrustPolicy",
    "HostTrustRegistration",
    "IdentityAuthorityAttestation",
    "IdentityAuthorityVerdict",
    "SourceSemanticsAuthorityAttestation",
    "SourceSemanticsAuthorityVerdict",
    "ProvenanceAuthorityAttestation",
    "ProvenanceAuthorityVerdict",
    "EvidenceAuthorityAttestation",
    "EvidenceAuthorityVerdict",
    "EpistemicRoleAuthorityAttestation",
    "EpistemicRoleAuthorityVerdict",
    "RetrievalAuthorityAttestation",
    "RetrievalAuthorityVerdict",
    "FailureDomainTopologyAttestation",
    "FailureDomainTopologyVerdict",
    "SupportSetIndependenceAuthorityAttestation",
    "SupportSetIndependenceAuthorityVerdict",
)

_F1_CONTROLLER_METHODS = {
    "draft_identity",
    "install_verified_identity",
    "draft_failure_domain_topology",
    "install_verified_failure_domain_topology",
    "draft_source_semantics",
    "install_verified_source_semantics",
    "draft_evidence_record",
    "verify_evidence_provenance",
    "verify_evidence_authority",
    "draft_epistemic_role",
    "install_verified_epistemic_role",
    "evidence_with_epistemic_role",
    "evidence_record_mapping",
    "draft_snapshot",
    "install_verified_snapshot",
    "draft_support_set_independence",
    "install_verified_support_set_independence",
    "identity_commitment",
    "failure_domain_topology_commitment",
    "source_semantics_commitment",
    "provenance_commitment",
    "evidence_authority_commitment",
    "snapshot_commitment",
    "support_set_independence_commitment",
    "evaluate_snapshot",
}


class AdapterError(Exception):
    pass


class NeutralSchemaError(AdapterError):
    pass


class BindingError(AdapterError):
    pass


class AuthorityStateRequired(AdapterError):
    pass


class ImplementationBoundaryError(AdapterError):
    def __init__(self, reason_code: str, message: str):
        super().__init__(message)
        self.primary_status = F2_PRIMARY_NO_GO
        self.reason_code = reason_code


@dataclass(frozen=True)
class PreparedArm:
    case_id: str
    arm: str
    dataset: str
    task: str
    draw: int
    candidate_conclusion: str
    candidate_conclusion_sha256: str
    question_sha256: str
    registered_context_line_sha256: str
    source_contexts_corpus_sha256: str
    source_registration: str
    prompt_sha256: str
    endpoint_record_sha256: str
    source_generations_sha256: str
    passage_bindings: tuple[tuple[int, str, str], ...]

    def to_mapping_manifest(self) -> dict[str, Any]:
        return {
            "adapter_version": ADAPTER_VERSION,
            "neutral_schema_version": NEUTRAL_SCHEMA_VERSION,
            "neutral_schema_sha256": NEUTRAL_SCHEMA_SHA256,
            "anchor_version": ANCHOR_VERSION,
            "anchor_wheel_sha256": ANCHOR_WHEEL_SHA256,
            "f1_interface_sha256": F1_INTERFACE_SHA256,
            "case_id": self.case_id,
            "arm": self.arm,
            "dataset": self.dataset,
            "task": self.task,
            "draw": self.draw,
            "candidate_conclusion": self.candidate_conclusion,
            "candidate_conclusion_sha256": self.candidate_conclusion_sha256,
            "question_sha256": self.question_sha256,
            "source_binding": {
                "registered_context_line_sha256": self.registered_context_line_sha256,
                "source_contexts_corpus_sha256": self.source_contexts_corpus_sha256,
                "source_registration": self.source_registration,
                "prompt_sha256": self.prompt_sha256,
                "endpoint_record_sha256": self.endpoint_record_sha256,
                "source_generations_sha256": self.source_generations_sha256,
            },
            "passage_bindings": [
                {"ordinal": o, "docid": d, "text_sha256": h}
                for o, d, h in self.passage_bindings
            ],
            "semantic_state": {
                "identity": "UNRESOLVED_UNTIL_EXTERNAL_STATE",
                "evidence_semantics": "UNRESOLVED_UNTIL_EXTERNAL_STATE",
                "provenance": "UNRESOLVED_UNTIL_EXTERNAL_STATE",
                "polarity": "UNRESOLVED_UNTIL_EXTERNAL_STATE",
                "epistemic_role": "UNRESOLVED_UNTIL_EXTERNAL_STATE",
                "decision_as_of": "UNRESOLVED_UNTIL_EXTERNAL_STATE",
                "scope": "UNRESOLVED_UNTIL_EXTERNAL_STATE",
                "support_requirement": "UNRESOLVED_UNTIL_EXTERNAL_STATE",
                "independence": "UNRESOLVED_UNTIL_EXTERNAL_STATE",
            },
            "authority_state": "NOT_ASSERTED_BY_NEUTRAL_SCHEMA",
        }


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _require_exact_keys(
    obj: Mapping[str, Any],
    required: set[str],
    optional: set[str] | None = None,
    *,
    where: str,
) -> None:
    optional = optional or set()
    keys = set(obj)
    missing = required - keys
    extra = keys - required - optional
    if missing:
        raise NeutralSchemaError(f"{where}: missing keys: {sorted(missing)}")
    if extra:
        raise NeutralSchemaError(f"{where}: unexpected keys: {sorted(extra)}")


def _require_nonempty_string(value: Any, *, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise NeutralSchemaError(f"{where}: expected non-empty string")
    return value


def _require_sha(value: Any, *, where: str) -> str:
    if not _is_sha256(value):
        raise NeutralSchemaError(f"{where}: expected lowercase SHA-256")
    return value


def validate_neutral_arm(payload: Mapping[str, Any]) -> None:
    if not isinstance(payload, Mapping):
        raise NeutralSchemaError("root: expected object")
    _require_exact_keys(payload, _REQUIRED_ROOT, where="root")

    if payload["schema_version"] != NEUTRAL_SCHEMA_VERSION:
        raise NeutralSchemaError("schema_version mismatch")
    if payload["arm"] not in _ALLOWED_ARMS:
        raise NeutralSchemaError("arm must be A or B")
    if payload["dataset"] not in _ALLOWED_DATASETS:
        raise NeutralSchemaError("unsupported dataset")
    if payload["task"] not in _ALLOWED_TASKS:
        raise NeutralSchemaError("unsupported task")
    if type(payload["draw"]) is not int or payload["draw"] < 0:
        raise NeutralSchemaError("draw must be a non-negative integer")

    _require_nonempty_string(payload["case_id"], where="case_id")
    if any(ord(ch) < 0x21 or ord(ch) > 0x7E for ch in payload["case_id"]):
        raise NeutralSchemaError("case_id must contain visible ASCII only")

    query = payload["query"]
    if not isinstance(query, Mapping):
        raise NeutralSchemaError("query: expected object")
    _require_exact_keys(query, _REQUIRED_QUERY, where="query")
    _require_nonempty_string(query["qid"], where="query.qid")
    _require_nonempty_string(query["source_qid"], where="query.source_qid")
    question = _require_nonempty_string(query["question"], where="query.question")
    question_sha = _require_sha(query["question_sha256"], where="query.question_sha256")
    if _sha256_text(question) != question_sha:
        raise BindingError("query.question_sha256 does not bind query.question UTF-8 bytes")

    sb = payload["source_binding"]
    if not isinstance(sb, Mapping):
        raise NeutralSchemaError("source_binding: expected object")
    _require_exact_keys(sb, _REQUIRED_SOURCE_BINDING, where="source_binding")
    _require_sha(
        sb["registered_context_line_sha256"],
        where="source_binding.registered_context_line_sha256",
    )
    corpus_sha = _require_sha(
        sb["source_contexts_corpus_sha256"],
        where="source_binding.source_contexts_corpus_sha256",
    )
    if corpus_sha != SOURCE_CORPUS_SHA256:
        raise BindingError("neutral arm is not bound to the accepted registered source corpus")
    _require_nonempty_string(
        sb["source_registration"],
        where="source_binding.source_registration",
    )
    _require_sha(sb["prompt_sha256"], where="source_binding.prompt_sha256")

    ep = payload["recorded_endpoint"]
    if not isinstance(ep, Mapping):
        raise NeutralSchemaError("recorded_endpoint: expected object")
    _require_exact_keys(
        ep,
        _REQUIRED_ENDPOINT,
        _OPTIONAL_ENDPOINT,
        where="recorded_endpoint",
    )
    _require_sha(
        ep["endpoint_record_sha256"],
        where="recorded_endpoint.endpoint_record_sha256",
    )
    _require_nonempty_string(ep["raw"], where="recorded_endpoint.raw")
    _require_nonempty_string(ep["canonical"], where="recorded_endpoint.canonical")
    _require_nonempty_string(ep["model"], where="recorded_endpoint.model")
    _require_nonempty_string(ep["revision"], where="recorded_endpoint.revision")
    _require_sha(
        ep["source_generations_sha256"],
        where="recorded_endpoint.source_generations_sha256",
    )
    if (
        "source_result_archive" in ep
        and ep["source_result_archive"] is not None
        and not isinstance(ep["source_result_archive"], str)
    ):
        raise NeutralSchemaError("recorded_endpoint.source_result_archive must be string or null")

    n = payload["neutrality"]
    if not isinstance(n, Mapping):
        raise NeutralSchemaError("neutrality: expected object")
    _require_exact_keys(n, _REQUIRED_NEUTRALITY, where="neutrality")
    for key, expected in _EXPECTED_NEUTRALITY.items():
        if n[key] != expected:
            raise NeutralSchemaError(f"neutrality.{key} must equal {expected!r}")

    passages = payload["passages"]
    if not isinstance(passages, list) or len(passages) != 10:
        raise NeutralSchemaError("passages must contain exactly 10 records")
    seen_ordinals: set[int] = set()
    seen_positions: list[int] = []
    for idx, row in enumerate(passages, 1):
        if not isinstance(row, Mapping):
            raise NeutralSchemaError(f"passages[{idx}]: expected object")
        _require_exact_keys(row, _REQUIRED_PASSAGE, where=f"passages[{idx}]")
        ordinal = row["ordinal"]
        if type(ordinal) is not int or not 1 <= ordinal <= 10:
            raise NeutralSchemaError(f"passages[{idx}].ordinal must be 1..10")
        if ordinal in seen_ordinals:
            raise BindingError("passage ordinals must be unique")
        seen_ordinals.add(ordinal)
        seen_positions.append(ordinal)
        _require_nonempty_string(row["docid"], where=f"passages[{idx}].docid")
        text = _require_nonempty_string(row["text"], where=f"passages[{idx}].text")
        text_sha = _require_sha(
            row["text_sha256"],
            where=f"passages[{idx}].text_sha256",
        )
        if _sha256_text(text) != text_sha:
            raise BindingError(
                f"passages[{idx}].text_sha256 does not bind passage text UTF-8 bytes"
            )
    if seen_positions != list(range(1, 11)):
        raise BindingError("passages must be ordered by ordinal 1..10")


def prepare_neutral_arm(payload: Mapping[str, Any]) -> PreparedArm:
    validate_neutral_arm(payload)
    ep = payload["recorded_endpoint"]
    q = payload["query"]
    sb = payload["source_binding"]
    passage_bindings = tuple(
        (row["ordinal"], row["docid"], row["text_sha256"])
        for row in payload["passages"]
    )
    return PreparedArm(
        case_id=payload["case_id"],
        arm=payload["arm"],
        dataset=payload["dataset"],
        task=payload["task"],
        draw=payload["draw"],
        candidate_conclusion=ep["canonical"],
        candidate_conclusion_sha256=_sha256_text(ep["canonical"]),
        question_sha256=q["question_sha256"],
        registered_context_line_sha256=sb["registered_context_line_sha256"],
        source_contexts_corpus_sha256=sb["source_contexts_corpus_sha256"],
        source_registration=sb["source_registration"],
        prompt_sha256=sb["prompt_sha256"],
        endpoint_record_sha256=ep["endpoint_record_sha256"],
        source_generations_sha256=ep["source_generations_sha256"],
        passage_bindings=passage_bindings,
    )


def authority_requirements(prepared: PreparedArm) -> dict[str, Any]:
    return {
        "adapter_version": ADAPTER_VERSION,
        "case_id": prepared.case_id,
        "arm": prepared.arm,
        "neutral_binding": {
            "question_sha256": prepared.question_sha256,
            "registered_context_line_sha256": prepared.registered_context_line_sha256,
            "passage_bindings": [
                {"ordinal": o, "docid": d, "text_sha256": h}
                for o, d, h in prepared.passage_bindings
            ],
        },
        "required_external_state": [
            "decision_as_of",
            "decision_scope",
            "claim_id",
            "claim_identity_binding",
            "required_independent_supports",
            "identity_state_and_authority",
            "failure_domain_topology_state_and_authority",
            "per_passage_source_semantics_state_and_authority",
            "per_passage_provenance_state_and_authority",
            "per_passage_evidence_authority",
            "per_passage_epistemic_role_state_and_authority",
            "retrieval_snapshot_state_and_authority",
            "support_set_independence_state_and_authority_if_required",
            "host_trust_registrations_and_verifiers",
        ],
        "prohibited_derivations": [
            "do_not_infer_identity_from_question_or_endpoint",
            "do_not_infer_polarity_from_retrieval_or_endpoint",
            "do_not_infer_provenance_from_docid_or_hash",
            "do_not_infer_independence_from_distinct_ids",
            "do_not_infer_scope_or_freshness_from_bookkeeping_metadata",
            "do_not_use_endpoint_as_evidence_or_authority",
        ],
    }


def verify_anchor_wheel_file(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise ImplementationBoundaryError(
            F2_REASON_API_INCOMPATIBLE,
            f"accepted Anchor wheel not found: {p}",
        )
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    if digest != ANCHOR_WHEEL_SHA256:
        raise ImplementationBoundaryError(
            F2_REASON_API_INCOMPATIBLE,
            f"Anchor wheel SHA-256 mismatch: {digest}",
        )
    return {
        "path": str(p),
        "bytes": p.stat().st_size,
        "sha256": digest,
        "expected_sha256": ANCHOR_WHEEL_SHA256,
    }


def _load_anchor_public_api() -> dict[str, Any]:
    try:
        import cfc_anchor
    except Exception as exc:
        raise ImplementationBoundaryError(
            F2_REASON_API_INCOMPATIBLE,
            f"cannot import accepted public package cfc_anchor: {type(exc).__name__}: {exc}",
        ) from exc

    api: dict[str, Any] = {}
    for name in _F1_PUBLIC_IMPORTS:
        if not hasattr(cfc_anchor, name):
            raise ImplementationBoundaryError(
                F2_REASON_API_INCOMPATIBLE,
                f"accepted public symbol missing: cfc_anchor.{name}",
            )
        api[name] = getattr(cfc_anchor, name)

    Controller = api["Controller"]
    for method_name in sorted(_F1_CONTROLLER_METHODS):
        if not hasattr(Controller, method_name):
            raise ImplementationBoundaryError(
                F2_REASON_API_INCOMPATIBLE,
                f"accepted public Controller method missing: {method_name}",
            )
    return api


def public_interface_probe(anchor_wheel_path: str | Path) -> dict[str, Any]:
    wheel = verify_anchor_wheel_file(anchor_wheel_path)
    api = _load_anchor_public_api()
    return {
        "adapter_version": ADAPTER_VERSION,
        "anchor_version": ANCHOR_VERSION,
        "anchor_wheel_artifact_verified": wheel,
        "anchor_wheel_sha256_expected": ANCHOR_WHEEL_SHA256,
        "anchor_engine_sha256_expected": ANCHOR_ENGINE_SHA256,
        "f1_interface_sha256": F1_INTERFACE_SHA256,
        "neutral_schema_sha256": NEUTRAL_SCHEMA_SHA256,
        "public_symbols_present": sorted(api),
        "controller_methods_present": sorted(_F1_CONTROLLER_METHODS),
        "private_engine_accessed": False,
    }


def canonical_json_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def prepare_artifacts(payload: Mapping[str, Any]) -> dict[str, Any]:
    prepared = prepare_neutral_arm(payload)
    mapping = prepared.to_mapping_manifest()
    requirements = authority_requirements(prepared)
    return {
        "mapping_manifest": mapping,
        "mapping_manifest_sha256": canonical_json_sha256(mapping),
        "authority_requirements": requirements,
        "authority_requirements_sha256": canonical_json_sha256(requirements),
        "substantive_execution_authorized": False,
        "next_required_gate": "F4_AUTHORITY_UNIVERSE_AND_LATER_F5_BINDING",
    }


def execute_with_resolved_state(
    payload: Mapping[str, Any],
    resolved: Mapping[str, Any],
    *,
    anchor_wheel_path: str | Path,
) -> dict[str, Any]:
    """
    Execute only when an external, pre-frozen resolved-state package supplies every
    semantic/authority input. This adapter contains no verifier implementation and
    creates no authority. The resolved package is expected to be produced later
    under accepted F4/F5 rules.

    Required resolved-package structure is intentionally strict and is validated
    against the neutral passage bindings before any Controller call.
    """
    prepared = prepare_neutral_arm(payload)
    _validate_resolved_state(prepared, resolved)
    wheel = verify_anchor_wheel_file(anchor_wheel_path)
    api = _load_anchor_public_api()

    Controller = api["Controller"]
    HostTrustPolicy = api["HostTrustPolicy"]
    HostTrustRegistration = api["HostTrustRegistration"]

    registrations = tuple(
        HostTrustRegistration(
            row["authority_class"],
            row["authority_id"],
            row["verifier"],
        )
        for row in resolved["host_trust_registrations"]
    )
    trust = HostTrustPolicy(registrations)
    c = Controller(scope=resolved["controller_scope"], trust_policy=trust)

    identity_spec = resolved["identity"]
    identity = c.draft_identity(**identity_spec["draft_kwargs"])
    identity_attestation = api["IdentityAuthorityAttestation"](
        **identity_spec["attestation_kwargs"]
    )
    c.install_verified_identity(
        identity,
        identity_attestation,
        identity_spec["verifier"],
        as_of=resolved["decision_as_of"],
    )

    topology_spec = resolved["failure_domain_topology"]
    topology = c.draft_failure_domain_topology(
        **topology_spec.get("draft_kwargs", {})
    )
    topology_attestation = api["FailureDomainTopologyAttestation"](
        **topology_spec["attestation_kwargs"]
    )
    c.install_verified_failure_domain_topology(
        topology,
        topology_attestation,
        topology_spec["verifier"],
        as_of=resolved["decision_as_of"],
    )

    evidence_objects = []
    evidence_mappings = []
    for state_row in resolved["passages"]:
        semantics_spec = state_row["source_semantics"]
        semantics = c.draft_source_semantics(**semantics_spec["draft_kwargs"])
        semantics_attestation = api["SourceSemanticsAuthorityAttestation"](
            **semantics_spec["attestation_kwargs"]
        )
        c.install_verified_source_semantics(
            semantics,
            semantics_attestation,
            semantics_spec["verifier"],
            as_of=resolved["decision_as_of"],
        )

        evidence = c.draft_evidence_record(**state_row["evidence_draft_kwargs"])

        prov_spec = state_row["provenance"]
        prov_attestation = api["ProvenanceAuthorityAttestation"](
            **prov_spec["attestation_kwargs"]
        )
        c.verify_evidence_provenance(
            evidence,
            prov_attestation,
            prov_spec["verifier"],
            as_of=resolved["decision_as_of"],
        )

        auth_spec = state_row["evidence_authority"]
        auth_attestation = api["EvidenceAuthorityAttestation"](
            **auth_spec["attestation_kwargs"]
        )
        c.verify_evidence_authority(
            evidence,
            auth_attestation,
            auth_spec["verifier"],
            as_of=resolved["decision_as_of"],
        )

        role_spec = state_row["epistemic_role"]
        role = c.draft_epistemic_role(evidence, **role_spec["draft_kwargs"])
        role_attestation = api["EpistemicRoleAuthorityAttestation"](
            **role_spec["attestation_kwargs"]
        )
        role_installation = c.install_verified_epistemic_role(
            evidence,
            role,
            role_attestation,
            role_spec["verifier"],
            as_of=resolved["decision_as_of"],
        )
        evidence = c.evidence_with_epistemic_role(evidence, role_installation)

        evidence_objects.append(evidence)
        evidence_mappings.append(c.evidence_record_mapping(evidence))

    snap = resolved["snapshot"]
    snapshot = c.draft_snapshot(evidence_mappings, **snap["draft_kwargs"])
    retrieval_attestation = api["RetrievalAuthorityAttestation"](
        **snap["attestation_kwargs"]
    )
    c.install_verified_snapshot(
        snapshot,
        evidence_mappings,
        retrieval_attestation,
        snap["verifier"],
        as_of=resolved["decision_as_of"],
    )

    if resolved.get("support_set_independence") is not None:
        ssi_spec = resolved["support_set_independence"]
        ssi = c.draft_support_set_independence(**ssi_spec["draft_kwargs"])
        ssi_attestation = api["SupportSetIndependenceAuthorityAttestation"](
            **ssi_spec["attestation_kwargs"]
        )
        c.install_verified_support_set_independence(
            ssi,
            evidence_objects,
            ssi_attestation,
            ssi_spec["verifier"],
            as_of=resolved["decision_as_of"],
        )

    result = c.evaluate_snapshot(
        snapshot,
        prepared.candidate_conclusion,
        evidence_mappings,
        resolved["claim_identity_map"],
        as_of=resolved["decision_as_of"],
        requirements=resolved["requirements"],
    )

    return {
        "adapter_version": ADAPTER_VERSION,
        "case_id": prepared.case_id,
        "arm": prepared.arm,
        "mapping_manifest_sha256": canonical_json_sha256(
            prepared.to_mapping_manifest()
        ),
        "candidate_conclusion_sha256": prepared.candidate_conclusion_sha256,
        "anchor_engine_sha256_expected": ANCHOR_ENGINE_SHA256,
        "anchor_wheel_artifact_verified": wheel,
        "claim_states": result.claims,
        "stop_type": result.stop_type,
        "control_closure": result.control_closure,
        "gates": result.gates,
        "raw": result.raw,
    }


def _validate_resolved_state(
    prepared: PreparedArm,
    resolved: Mapping[str, Any],
) -> None:
    if not isinstance(resolved, Mapping):
        raise AuthorityStateRequired("resolved state package is required")
    required = {
        "decision_as_of",
        "controller_scope",
        "claim_identity_map",
        "requirements",
        "host_trust_registrations",
        "identity",
        "failure_domain_topology",
        "passages",
        "snapshot",
    }
    missing = required - set(resolved)
    if missing:
        raise AuthorityStateRequired(
            f"resolved state missing keys: {sorted(missing)}"
        )

    registrations = resolved["host_trust_registrations"]
    if (
        not isinstance(registrations, Sequence)
        or isinstance(registrations, (str, bytes))
        or not registrations
    ):
        raise AuthorityStateRequired(
            "host_trust_registrations must be a non-empty sequence"
        )
    for idx, row in enumerate(registrations, 1):
        if not isinstance(row, Mapping):
            raise AuthorityStateRequired(
                f"host_trust_registrations[{idx}] must be an object"
            )
        for key in ("authority_class", "authority_id", "verifier"):
            if key not in row:
                raise AuthorityStateRequired(
                    f"host_trust_registrations[{idx}] missing {key}"
                )

    rows = resolved["passages"]
    if (
        not isinstance(rows, Sequence)
        or isinstance(rows, (str, bytes))
        or len(rows) != 10
    ):
        raise AuthorityStateRequired(
            "resolved passages must contain exactly 10 records"
        )

    for expected, row in zip(prepared.passage_bindings, rows):
        if not isinstance(row, Mapping):
            raise AuthorityStateRequired(
                "resolved passage row must be an object"
            )
        ordinal, docid, text_sha = expected
        binding = row.get("neutral_binding")
        exact = {
            "ordinal": ordinal,
            "docid": docid,
            "text_sha256": text_sha,
        }
        if binding != exact:
            raise BindingError(
                "resolved passage is not exactly bound to neutral passage identity"
            )
        for key in (
            "source_semantics",
            "evidence_draft_kwargs",
            "provenance",
            "evidence_authority",
            "epistemic_role",
        ):
            if key not in row:
                raise AuthorityStateRequired(
                    f"resolved passage {ordinal} missing {key}"
                )

    for name in ("identity", "failure_domain_topology", "snapshot"):
        if not isinstance(resolved[name], Mapping):
            raise AuthorityStateRequired(f"{name} must be an object")

    if (
        not isinstance(resolved["claim_identity_map"], Mapping)
        or not resolved["claim_identity_map"]
    ):
        raise AuthorityStateRequired(
            "claim_identity_map must be a non-empty object"
        )
    if (
        not isinstance(resolved["requirements"], Mapping)
        or not resolved["requirements"]
    ):
        raise AuthorityStateRequired(
            "requirements must be a non-empty object"
        )

    if (
        not isinstance(resolved["decision_as_of"], str)
        or not resolved["decision_as_of"]
    ):
        raise AuthorityStateRequired(
            "decision_as_of must be an explicit non-empty string"
        )
