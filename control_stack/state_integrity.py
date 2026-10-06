from __future__ import annotations

import hashlib
import json
from typing import Any


STATE_INTEGRITY_VERSION = "STATE_INTEGRITY_V0_1"
STATE_INTEGRITY_BOUNDARY = (
    "EXPLICIT_IDENTITY_LINEAGE_AND_SNAPSHOT_BINDING_ONLY"
)

STATE_VALID = "STATE_VALID"
STATE_UNRESOLVED = "STATE_UNRESOLVED"
STATE_INVALID = "STATE_INVALID"

NO_ADDITIONAL_BLOCK = "NO_ADDITIONAL_BLOCK_FROM_STATE_INTEGRITY_ONLY"
BLOCK_STATE = "BLOCK_STATE_CARRY_FORWARD_STATE_INTEGRITY_REQUIRED"


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def state_fingerprint(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _result(
    *,
    status: str,
    reason: str,
    observed: dict[str, Any],
    fingerprint: str | None,
    binding_status: str,
    lineage_status: str,
    violations: list[str],
) -> dict[str, Any]:
    blocked = status != STATE_VALID
    return {
        "version": STATE_INTEGRITY_VERSION,
        "status": status,
        "reason": reason,
        "case_id": observed.get("case_id"),
        "arm_id": observed.get("arm_id"),
        "state_id": observed.get("state_id"),
        "snapshot_id": observed.get("snapshot_id"),
        "lineage_id": observed.get("lineage_id"),
        "previous_state_id": observed.get("previous_state_id"),
        "state_fingerprint": fingerprint,
        "binding_status": binding_status,
        "lineage_status": lineage_status,
        "violations": violations,
        "unresolved": list(violations) if blocked else [],
        "requires_review": blocked,
        "propagation_effect": BLOCK_STATE if blocked else NO_ADDITIONAL_BLOCK,
        "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
        "boundary": STATE_INTEGRITY_BOUNDARY,
    }


def _malformed_reason(record: Any, expectation: Any) -> list[str]:
    reasons: list[str] = []
    if not isinstance(record, dict):
        return ["RECORD_NOT_OBJECT"]
    if not isinstance(expectation, dict):
        return ["EXPECTATION_NOT_OBJECT"]

    required_record = {
        "case_id",
        "arm_id",
        "state_id",
        "snapshot_id",
        "lineage_id",
        "previous_state_id",
        "state_payload",
    }
    required_expectation = {
        "case_id",
        "arm_id",
        "current_snapshot_id",
        "lineage_id",
        "expected_previous_state_id",
        "registered_snapshot_fingerprint",
    }

    missing_record = sorted(required_record - set(record))
    missing_expectation = sorted(required_expectation - set(expectation))
    reasons.extend(f"RECORD_MISSING_{key.upper()}" for key in missing_record)
    reasons.extend(
        f"EXPECTATION_MISSING_{key.upper()}" for key in missing_expectation
    )
    if reasons:
        return reasons

    for key in ("case_id", "state_id", "snapshot_id", "lineage_id"):
        if not isinstance(record[key], str) or not record[key]:
            reasons.append(f"RECORD_INVALID_{key.upper()}")

    for key in ("case_id", "current_snapshot_id", "lineage_id"):
        if not isinstance(expectation[key], str) or not expectation[key]:
            reasons.append(f"EXPECTATION_INVALID_{key.upper()}")

    for path, value in (
        ("record.arm_id", record["arm_id"]),
        ("record.previous_state_id", record["previous_state_id"]),
        ("expectation.arm_id", expectation["arm_id"]),
        ("expectation.expected_previous_state_id", expectation["expected_previous_state_id"]),
        (
            "expectation.registered_snapshot_fingerprint",
            expectation["registered_snapshot_fingerprint"],
        ),
    ):
        if value is not None and not isinstance(value, str):
            reasons.append("INVALID_" + path.replace(".", "_").upper())

    if not isinstance(record["state_payload"], dict):
        reasons.append("RECORD_STATE_PAYLOAD_NOT_OBJECT")

    fp = expectation["registered_snapshot_fingerprint"]
    if fp is not None:
        if len(fp) != 64 or any(ch not in "0123456789abcdef" for ch in fp):
            reasons.append("EXPECTATION_INVALID_REGISTERED_SNAPSHOT_FINGERPRINT")

    return reasons


def assess_state_integrity(
    record: dict[str, Any],
    expectation: dict[str, Any],
) -> dict[str, Any]:
    """Assess exact state identity, current-snapshot binding and lineage.

    v0.1 is intentionally narrow. It does not decide evidence applicability,
    continuity authority, controller closure or action permission.

    The record argument is the observed state identity plus its explicit
    payload. The expectation argument is an independently supplied binding
    target and registered fingerprint for the expected current snapshot.
    """
    malformed = _malformed_reason(record, expectation)
    if malformed:
        observed = record if isinstance(record, dict) else {}
        return _result(
            status=STATE_UNRESOLVED,
            reason="STATE_INTEGRITY_INPUT_UNRESOLVED",
            observed=observed,
            fingerprint=None,
            binding_status="UNKNOWN",
            lineage_status="UNKNOWN",
            violations=malformed,
        )

    observed_fp = state_fingerprint(record["state_payload"])
    violations_invalid: list[str] = []
    violations_unresolved: list[str] = []

    if record["case_id"] != expectation["case_id"]:
        violations_invalid.append("CASE_ID_MISMATCH")

    expected_arm = expectation["arm_id"]
    if record["arm_id"] != expected_arm:
        violations_invalid.append("ARM_ID_MISMATCH")

    if record["lineage_id"] != expectation["lineage_id"]:
        violations_invalid.append("LINEAGE_ID_MISMATCH")

    if record["snapshot_id"] != expectation["current_snapshot_id"]:
        violations_unresolved.append("CURRENT_SNAPSHOT_MISMATCH")

    expected_previous = expectation["expected_previous_state_id"]
    if record["previous_state_id"] != expected_previous:
        violations_unresolved.append("PREDECESSOR_MISMATCH")

    registered_fp = expectation["registered_snapshot_fingerprint"]
    if registered_fp is None:
        violations_unresolved.append("SNAPSHOT_FINGERPRINT_NOT_REGISTERED")
    elif observed_fp != registered_fp:
        violations_invalid.append("SNAPSHOT_FINGERPRINT_MISMATCH")

    if violations_invalid:
        violations = violations_invalid + violations_unresolved
        return _result(
            status=STATE_INVALID,
            reason=violations_invalid[0],
            observed=record,
            fingerprint=observed_fp,
            binding_status="MISMATCH",
            lineage_status=(
                "INVALID"
                if any(
                    item in {"CASE_ID_MISMATCH", "ARM_ID_MISMATCH", "LINEAGE_ID_MISMATCH"}
                    for item in violations_invalid
                )
                else "UNKNOWN"
            ),
            violations=violations,
        )

    if violations_unresolved:
        return _result(
            status=STATE_UNRESOLVED,
            reason=violations_unresolved[0],
            observed=record,
            fingerprint=observed_fp,
            binding_status=(
                "UNKNOWN"
                if "SNAPSHOT_FINGERPRINT_NOT_REGISTERED" in violations_unresolved
                else "MISMATCH"
            ),
            lineage_status=(
                "DEGRADED"
                if "PREDECESSOR_MISMATCH" in violations_unresolved
                else "ESTABLISHED"
            ),
            violations=violations_unresolved,
        )

    return _result(
        status=STATE_VALID,
        reason="EXACT_STATE_BINDING_ESTABLISHED",
        observed=record,
        fingerprint=observed_fp,
        binding_status="BOUND",
        lineage_status="ESTABLISHED",
        violations=[],
    )
