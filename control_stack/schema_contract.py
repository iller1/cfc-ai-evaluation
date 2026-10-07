from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "CONTROL_STACK_SCHEMA_v0.1"
FROZEN_CONTROLLER_VERSION = "0.2.90rc1"
SCHEMA_PATH = Path(__file__).with_name("CONTROL_STACK_SCHEMA_v0.1.json")


class ContractError(ValueError):
    """Raised when a Control Stack envelope violates v0.1 contract."""


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ContractError("SCHEMA_NOT_OBJECT")
    if value.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ContractError("SCHEMA_DRAFT_MISMATCH")
    if value.get("type") != "object":
        raise ContractError("SCHEMA_ROOT_NOT_OBJECT")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def round_trip(value: dict[str, Any]) -> dict[str, Any]:
    """Canonical JSON round-trip used by contract tests and receipts."""
    return json.loads(canonical_json(value))


def fingerprint(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _require_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{path}:OBJECT_REQUIRED")
    return value


def _require_keys(value: dict[str, Any], required: set[str], path: str) -> None:
    missing = sorted(required - set(value))
    if missing:
        raise ContractError(f"{path}:MISSING:{','.join(missing)}")


def _reject_extra(value: dict[str, Any], allowed: set[str], path: str) -> None:
    extra = sorted(set(value) - allowed)
    if extra:
        raise ContractError(f"{path}:UNDECLARED:{','.join(extra)}")


def _enum(value: Any, allowed: set[str], path: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ContractError(f"{path}:INVALID_ENUM")
    return value


def _nonempty(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{path}:NONEMPTY_STRING_REQUIRED")
    return value


def _nullable_string(value: Any, path: str) -> str | None:
    if value is not None and not isinstance(value, str):
        raise ContractError(f"{path}:STRING_OR_NULL_REQUIRED")
    return value


def _bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise ContractError(f"{path}:BOOLEAN_REQUIRED")
    return value


def _string_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        raise ContractError(f"{path}:ARRAY_REQUIRED")
    if any(not isinstance(item, str) or not item for item in value):
        raise ContractError(f"{path}:NONEMPTY_STRING_ITEMS_REQUIRED")
    if len(value) != len(set(value)):
        raise ContractError(f"{path}:DUPLICATE_ITEMS")
    return value


def _validate_identity(value: Any) -> dict[str, Any]:
    obj = _require_object(value, "identity")
    allowed = {
        "case_id",
        "arm_id",
        "conversation_id",
        "state_id",
        "snapshot_id",
        "lineage_id",
        "previous_state_id",
        "state_fingerprint",
    }
    required = {
        "case_id",
        "state_id",
        "snapshot_id",
        "lineage_id",
        "state_fingerprint",
    }
    _require_keys(obj, required, "identity")
    _reject_extra(obj, allowed, "identity")
    for key in ("case_id", "state_id", "snapshot_id", "lineage_id"):
        _nonempty(obj[key], f"identity.{key}")
    for key in ("arm_id", "conversation_id", "previous_state_id"):
        if key in obj:
            _nullable_string(obj[key], f"identity.{key}")
    fp = _nonempty(obj["state_fingerprint"], "identity.state_fingerprint")
    if len(fp) != 64 or any(ch not in "0123456789abcdef" for ch in fp):
        raise ContractError("identity.state_fingerprint:SHA256_HEX_REQUIRED")
    return obj


def _validate_state_integrity(value: Any) -> dict[str, Any]:
    obj = _require_object(value, "state_integrity")
    allowed = {"status", "binding_status", "lineage_status", "unresolved"}
    _require_keys(obj, allowed, "state_integrity")
    _reject_extra(obj, allowed, "state_integrity")
    _enum(
        obj["status"],
        {"STATE_VALID", "STATE_UNRESOLVED", "STATE_INVALID"},
        "state_integrity.status",
    )
    _enum(
        obj["binding_status"],
        {"BOUND", "UNBOUND", "MISMATCH", "UNKNOWN"},
        "state_integrity.binding_status",
    )
    _enum(
        obj["lineage_status"],
        {"ESTABLISHED", "DEGRADED", "UNKNOWN", "INVALID"},
        "state_integrity.lineage_status",
    )
    _string_list(obj["unresolved"], "state_integrity.unresolved")
    return obj


def _validate_evidence(value: Any) -> dict[str, Any]:
    obj = _require_object(value, "evidence")
    allowed = {
        "status",
        "provenance_state",
        "applicability_state",
        "dependency_state",
        "evidence_set",
        "missing_evidence",
        "drift_state",
    }
    _require_keys(obj, allowed, "evidence")
    _reject_extra(obj, allowed, "evidence")
    _enum(
        obj["status"],
        {
            "EVIDENCE_APPLICABLE",
            "EVIDENCE_PARTIAL",
            "EVIDENCE_UNKNOWN",
            "EVIDENCE_INVALID",
        },
        "evidence.status",
    )
    _enum(
        obj["provenance_state"],
        {"ESTABLISHED", "PARTIAL", "UNKNOWN", "INVALID"},
        "evidence.provenance_state",
    )
    _enum(
        obj["applicability_state"],
        {"APPLICABLE", "PARTIAL", "UNKNOWN", "NOT_APPLICABLE", "INVALID"},
        "evidence.applicability_state",
    )
    _enum(
        obj["dependency_state"],
        {"RESOLVED", "PARTIAL", "UNKNOWN", "CONFLICTING"},
        "evidence.dependency_state",
    )
    _enum(
        obj["drift_state"],
        {"NO_DRIFT", "MATERIAL_DRIFT", "UNRESOLVED", "NOT_ASSESSED"},
        "evidence.drift_state",
    )
    _string_list(obj["missing_evidence"], "evidence.missing_evidence")
    records = obj["evidence_set"]
    if not isinstance(records, list):
        raise ContractError("evidence.evidence_set:ARRAY_REQUIRED")
    seen_ids: set[str] = set()
    for idx, raw in enumerate(records):
        path = f"evidence.evidence_set[{idx}]"
        rec = _require_object(raw, path)
        allowed_rec = {
            "evidence_id",
            "source_id",
            "validity",
            "scope_status",
            "failure_domain_id",
        }
        _require_keys(rec, allowed_rec, path)
        _reject_extra(rec, allowed_rec, path)
        evidence_id = _nonempty(rec["evidence_id"], f"{path}.evidence_id")
        if evidence_id in seen_ids:
            raise ContractError("evidence.evidence_set:DUPLICATE_EVIDENCE_ID")
        seen_ids.add(evidence_id)
        _nonempty(rec["source_id"], f"{path}.source_id")
        _enum(
            rec["validity"],
            {"CURRENT", "STALE", "UNKNOWN", "INVALID"},
            f"{path}.validity",
        )
        _enum(
            rec["scope_status"],
            {"MATCH", "PARTIAL", "WRONG", "UNKNOWN"},
            f"{path}.scope_status",
        )
        _nullable_string(rec["failure_domain_id"], f"{path}.failure_domain_id")

    if obj["status"] == "EVIDENCE_APPLICABLE":
        if obj["provenance_state"] != "ESTABLISHED":
            raise ContractError(
                "evidence:APPLICABLE_REQUIRES_ESTABLISHED_PROVENANCE"
            )
        if obj["applicability_state"] != "APPLICABLE":
            raise ContractError(
                "evidence:APPLICABLE_REQUIRES_APPLICABILITY"
            )
        if obj["dependency_state"] != "RESOLVED":
            raise ContractError(
                "evidence:APPLICABLE_REQUIRES_RESOLVED_DEPENDENCIES"
            )
        if obj["missing_evidence"]:
            raise ContractError(
                "evidence:APPLICABLE_REQUIRES_NO_MISSING_EVIDENCE"
            )
        if obj["drift_state"] != "NO_DRIFT":
            raise ContractError(
                "evidence:APPLICABLE_REQUIRES_NO_DRIFT"
            )
        if not records:
            raise ContractError(
                "evidence:APPLICABLE_REQUIRES_EVIDENCE_RECORD"
            )
        if any(rec["validity"] != "CURRENT" for rec in records):
            raise ContractError(
                "evidence:APPLICABLE_REQUIRES_CURRENT_RECORDS"
            )
        if any(rec["scope_status"] != "MATCH" for rec in records):
            raise ContractError(
                "evidence:APPLICABLE_REQUIRES_SCOPE_MATCH"
            )
        if any(
            not isinstance(rec["failure_domain_id"], str)
            or not rec["failure_domain_id"]
            for rec in records
        ):
            raise ContractError(
                "evidence:APPLICABLE_REQUIRES_FAILURE_DOMAIN"
            )
    return obj


def _validate_continuity(value: Any) -> dict[str, Any]:
    obj = _require_object(value, "continuity")
    allowed = {
        "status",
        "transition_type",
        "reproducibility_state",
        "threshold_state",
        "unresolved",
    }
    _require_keys(obj, allowed, "continuity")
    _reject_extra(obj, allowed, "continuity")
    _enum(
        obj["status"],
        {
            "CONTINUITY_ESTABLISHED",
            "CONTINUITY_DEGRADED",
            "CONTINUITY_UNKNOWN",
        },
        "continuity.status",
    )
    _nonempty(obj["transition_type"], "continuity.transition_type")
    _enum(
        obj["reproducibility_state"],
        {"ESTABLISHED", "DEGRADED", "UNKNOWN", "NOT_ASSESSED"},
        "continuity.reproducibility_state",
    )
    _enum(
        obj["threshold_state"],
        {"WITHIN", "BREACHED", "UNKNOWN", "NOT_APPLICABLE"},
        "continuity.threshold_state",
    )
    _string_list(obj["unresolved"], "continuity.unresolved")
    return obj


def _validate_authority(value: Any) -> dict[str, Any]:
    obj = _require_object(value, "authority")
    allowed = {"state", "source", "valid_from", "valid_to", "revoked"}
    _require_keys(obj, allowed, "authority")
    _reject_extra(obj, allowed, "authority")
    _enum(
        obj["state"],
        {"ESTABLISHED", "NOT_ESTABLISHED", "UNKNOWN", "REVOKED", "EXPIRED"},
        "authority.state",
    )
    for key in ("source", "valid_from", "valid_to"):
        _nullable_string(obj[key], f"authority.{key}")
    _bool(obj["revoked"], "authority.revoked")
    if obj["revoked"] and obj["state"] != "REVOKED":
        raise ContractError("authority:REVOKED_FLAG_STATE_MISMATCH")
    if obj["state"] == "REVOKED" and not obj["revoked"]:
        raise ContractError("authority:REVOKED_STATE_FLAG_MISMATCH")
    return obj


def _validate_cfc(value: Any) -> dict[str, Any]:
    obj = _require_object(value, "cfc")
    allowed = {
        "decision",
        "authority_state",
        "blockers",
        "reason",
        "controller_version",
        "controller_identity",
    }
    _require_keys(obj, allowed, "cfc")
    _reject_extra(obj, allowed, "cfc")
    decision = _enum(
        obj["decision"],
        {"NOT_RUN", "CONTINUE", "HOLD", "STOP", "ESCALATE"},
        "cfc.decision",
    )
    _enum(
        obj["authority_state"],
        {
            "ESTABLISHED",
            "NOT_ESTABLISHED",
            "UNKNOWN",
            "REVOKED",
            "EXPIRED",
            "NOT_ASSESSED",
        },
        "cfc.authority_state",
    )
    _string_list(obj["blockers"], "cfc.blockers")
    if not isinstance(obj["reason"], str):
        raise ContractError("cfc.reason:STRING_REQUIRED")
    version = _nullable_string(obj["controller_version"], "cfc.controller_version")
    _nullable_string(obj["controller_identity"], "cfc.controller_identity")
    if decision == "NOT_RUN":
        if version is not None or obj["controller_identity"] is not None:
            raise ContractError("cfc:NOT_RUN_MUST_NOT_CLAIM_CONTROLLER_IDENTITY")
    else:
        if version != FROZEN_CONTROLLER_VERSION:
            raise ContractError("cfc:FROZEN_CONTROLLER_VERSION_REQUIRED")
        if not obj["controller_identity"]:
            raise ContractError("cfc:CONTROLLER_IDENTITY_REQUIRED")
    return obj


def _validate_execution(value: Any) -> dict[str, Any]:
    obj = _require_object(value, "execution")
    allowed = {
        "attempted",
        "executed",
        "execution_status",
        "effect_handle",
        "idempotency_key",
        "pre_execution_state_id",
        "receipt_id",
    }
    _require_keys(obj, allowed, "execution")
    _reject_extra(obj, allowed, "execution")
    attempted = _bool(obj["attempted"], "execution.attempted")
    executed = obj["executed"]
    if executed is not None and not isinstance(executed, bool):
        raise ContractError("execution.executed:BOOLEAN_OR_NULL_REQUIRED")
    status = _enum(
        obj["execution_status"],
        {
            "NOT_ATTEMPTED",
            "BLOCKED",
            "ATTEMPTED_NOT_EXECUTED",
            "EXECUTED",
            "FAILED",
            "OUTCOME_UNKNOWN",
        },
        "execution.execution_status",
    )
    for key in (
        "effect_handle",
        "idempotency_key",
        "pre_execution_state_id",
        "receipt_id",
    ):
        _nullable_string(obj[key], f"execution.{key}")

    if status == "NOT_ATTEMPTED":
        if attempted or executed is not False:
            raise ContractError("execution:NOT_ATTEMPTED_FLAG_MISMATCH")
    elif status == "BLOCKED":
        if attempted or executed is not False:
            raise ContractError("execution:BLOCKED_FLAG_MISMATCH")
    elif status in {"ATTEMPTED_NOT_EXECUTED", "FAILED"}:
        if not attempted or executed is not False:
            raise ContractError("execution:KNOWN_NO_EFFECT_FLAG_MISMATCH")
    elif status == "OUTCOME_UNKNOWN":
        if not attempted or executed is not None:
            raise ContractError("execution:OUTCOME_UNKNOWN_FLAG_MISMATCH")
    elif status == "EXECUTED":
        if not attempted or executed is not True:
            raise ContractError("execution:EXECUTED_STATUS_FLAG_MISMATCH")

    if status != "NOT_ATTEMPTED":
        for key in (
            "idempotency_key",
            "pre_execution_state_id",
            "receipt_id",
        ):
            if not isinstance(obj[key], str) or not obj[key]:
                raise ContractError(
                    f"execution:{key.upper()}_REQUIRED_FOR_GATE_RECEIPT"
                )

    if status == "EXECUTED":
        if not isinstance(obj["effect_handle"], str) or not obj["effect_handle"]:
            raise ContractError("execution:EXECUTED_REQUIRES_EFFECT_HANDLE")
    if status in {"BLOCKED", "ATTEMPTED_NOT_EXECUTED", "FAILED"}:
        if obj["effect_handle"] is not None:
            raise ContractError("execution:KNOWN_NO_EFFECT_MUST_NOT_HAVE_HANDLE")
    return obj


def _validate_audit(value: Any) -> dict[str, Any]:
    obj = _require_object(value, "audit")
    allowed = {
        "component_versions",
        "receipts",
        "supersedes",
        "superseded_by",
        "claim_ceiling",
    }
    _require_keys(obj, allowed, "audit")
    _reject_extra(obj, allowed, "audit")
    versions = obj["component_versions"]
    if not isinstance(versions, dict):
        raise ContractError("audit.component_versions:OBJECT_REQUIRED")
    if any(
        not isinstance(key, str)
        or not key
        or not isinstance(val, str)
        or not val
        for key, val in versions.items()
    ):
        raise ContractError("audit.component_versions:NONEMPTY_STRING_MAP_REQUIRED")
    for key in ("receipts", "supersedes", "superseded_by"):
        _string_list(obj[key], f"audit.{key}")
    _nonempty(obj["claim_ceiling"], "audit.claim_ceiling")
    return obj


def validate_envelope(value: Any) -> dict[str, Any]:
    """Validate the strict v0.1 envelope and cross-layer safety invariants."""
    root = _require_object(value, "root")
    allowed = {
        "schema_version",
        "envelope_id",
        "identity",
        "state_integrity",
        "evidence",
        "continuity",
        "authority",
        "cfc",
        "execution",
        "audit",
    }
    _require_keys(root, allowed, "root")
    _reject_extra(root, allowed, "root")

    if root["schema_version"] != SCHEMA_VERSION:
        raise ContractError("root:SCHEMA_VERSION_MISMATCH")
    _nonempty(root["envelope_id"], "envelope_id")

    identity = _validate_identity(root["identity"])
    state_integrity = _validate_state_integrity(root["state_integrity"])
    evidence = _validate_evidence(root["evidence"])
    continuity = _validate_continuity(root["continuity"])
    authority = _validate_authority(root["authority"])
    cfc = _validate_cfc(root["cfc"])
    execution = _validate_execution(root["execution"])
    _validate_audit(root["audit"])

    blockers = []
    if state_integrity["status"] != "STATE_VALID":
        blockers.append("STATE_INTEGRITY_NOT_VALID")
    if evidence["status"] != "EVIDENCE_APPLICABLE":
        blockers.append("EVIDENCE_NOT_APPLICABLE")
    if continuity["status"] != "CONTINUITY_ESTABLISHED":
        blockers.append("CONTINUITY_NOT_ESTABLISHED")
    if authority["state"] != "ESTABLISHED":
        blockers.append("AUTHORITY_NOT_ESTABLISHED")

    if cfc["decision"] == "CONTINUE" and blockers:
        raise ContractError(
            "cross_layer:CONTINUE_WITH_UPSTREAM_BLOCKER:" + ",".join(blockers)
        )

    if execution["executed"]:
        if cfc["decision"] != "CONTINUE":
            raise ContractError("cross_layer:EXECUTED_WITHOUT_CONTINUE")
        if cfc["authority_state"] != "ESTABLISHED":
            raise ContractError("cross_layer:EXECUTED_WITHOUT_CFC_AUTHORITY")
        if authority["state"] != "ESTABLISHED":
            raise ContractError("cross_layer:EXECUTED_WITHOUT_CURRENT_AUTHORITY")
        if execution["pre_execution_state_id"] != identity["state_id"]:
            raise ContractError("cross_layer:EXECUTED_ON_WRONG_STATE")

    if cfc["decision"] in {"HOLD", "STOP", "ESCALATE", "NOT_RUN"} and execution["executed"]:
        raise ContractError("cross_layer:BLOCKING_DECISION_WAS_EXECUTED")

    return copy.deepcopy(root)
