from __future__ import annotations

import copy
from typing import Any


EVIDENCE_PROVENANCE_VERSION = "EVIDENCE_PROVENANCE_V0_1"
EVIDENCE_PROVENANCE_BOUNDARY = (
    "EXPLICIT_EVIDENCE_RECORDS_BOUND_RECEIPTS_AND_DRIFT_ONLY_"
    "NO_FREE_TEXT_SOURCE_TRUTH_OR_INDEPENDENCE_INFERENCE"
)

EVIDENCE_APPLICABLE = "EVIDENCE_APPLICABLE"
EVIDENCE_PARTIAL = "EVIDENCE_PARTIAL"
EVIDENCE_UNKNOWN = "EVIDENCE_UNKNOWN"
EVIDENCE_INVALID = "EVIDENCE_INVALID"

NO_ADDITIONAL_BLOCK = "NO_ADDITIONAL_BLOCK_FROM_EVIDENCE_PROVENANCE_ONLY"
BLOCK_EVIDENCE = "BLOCK_EVIDENCE_PROPAGATION_REVIEW_REQUIRED"

RECORD_KEYS = {
    "evidence_id",
    "source_id",
    "validity",
    "scope_status",
    "failure_domain_id",
}
PROVENANCE_RECEIPT_KEYS = {
    "receipt_id",
    "state_id",
    "evidence_id",
    "source_id",
    "status",
}
DEPENDENCY_RECEIPT_KEYS = {
    "receipt_id",
    "state_id",
    "evidence_ids",
    "failure_domains",
    "status",
}

VALIDITIES = {"CURRENT", "STALE", "UNKNOWN", "INVALID"}
SCOPE_STATES = {"MATCH", "PARTIAL", "WRONG", "UNKNOWN"}
PROVENANCE_STATES = {"ESTABLISHED", "PARTIAL", "UNKNOWN", "INVALID"}
DEPENDENCY_STATES = {"RESOLVED", "PARTIAL", "UNKNOWN", "CONFLICTING"}
DRIFT_STATES = {"NO_DRIFT", "MATERIAL_DRIFT", "UNRESOLVED", "NOT_ASSESSED"}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _valid_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(_nonempty_string(item) for item in value)
        and len(value) == len(set(value))
    )


def _result(
    *,
    state_id: str | None,
    status: str,
    reason: str,
    provenance_state: str,
    applicability_state: str,
    dependency_state: str,
    evidence_set: list[dict[str, Any]],
    missing_evidence: list[str],
    drift_state: str,
    diagnostics: list[str],
    provenance_receipt_ids: list[str],
    dependency_receipt_id: str | None,
) -> dict[str, Any]:
    blocked = status != EVIDENCE_APPLICABLE
    return {
        "version": EVIDENCE_PROVENANCE_VERSION,
        "status": status,
        "reason": reason,
        "state_id": state_id,
        "evidence": {
            "status": status,
            "provenance_state": provenance_state,
            "applicability_state": applicability_state,
            "dependency_state": dependency_state,
            "evidence_set": copy.deepcopy(evidence_set),
            "missing_evidence": list(missing_evidence),
            "drift_state": drift_state,
        },
        "diagnostics": list(diagnostics),
        "provenance_receipt_ids": list(provenance_receipt_ids),
        "dependency_receipt_id": dependency_receipt_id,
        "requires_review": blocked,
        "propagation_effect": (
            BLOCK_EVIDENCE if blocked else NO_ADDITIONAL_BLOCK
        ),
        "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
        "boundary": EVIDENCE_PROVENANCE_BOUNDARY,
    }


def _invalid(
    reason: str,
    *,
    state_id: str | None,
    evidence_set: list[dict[str, Any]] | None = None,
    missing_evidence: list[str] | None = None,
    drift_state: str = "NOT_ASSESSED",
    diagnostics: list[str] | None = None,
    provenance_state: str = "INVALID",
    applicability_state: str = "INVALID",
    dependency_state: str = "UNKNOWN",
    provenance_receipt_ids: list[str] | None = None,
    dependency_receipt_id: str | None = None,
) -> dict[str, Any]:
    all_diagnostics = list(diagnostics or [])
    if reason not in all_diagnostics:
        all_diagnostics.insert(0, reason)
    return _result(
        state_id=state_id,
        status=EVIDENCE_INVALID,
        reason=reason,
        provenance_state=provenance_state,
        applicability_state=applicability_state,
        dependency_state=dependency_state,
        evidence_set=list(evidence_set or []),
        missing_evidence=list(missing_evidence or []),
        drift_state=drift_state,
        diagnostics=all_diagnostics,
        provenance_receipt_ids=list(provenance_receipt_ids or []),
        dependency_receipt_id=dependency_receipt_id,
    )


def _validate_records(
    evidence_set: Any,
) -> tuple[list[dict[str, Any]], str | None]:
    if not isinstance(evidence_set, list):
        return [], "EVIDENCE_SET_NOT_ARRAY"

    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for raw in evidence_set:
        if not isinstance(raw, dict) or set(raw) != RECORD_KEYS:
            return records, "EVIDENCE_RECORD_SCHEMA_INVALID"

        evidence_id = raw["evidence_id"]
        source_id = raw["source_id"]
        validity = raw["validity"]
        scope_status = raw["scope_status"]
        failure_domain_id = raw["failure_domain_id"]

        if not _nonempty_string(evidence_id):
            return records, "EVIDENCE_ID_INVALID"
        if evidence_id in seen_ids:
            return records, "DUPLICATE_EVIDENCE_ID"
        seen_ids.add(evidence_id)

        if not _nonempty_string(source_id):
            return records, "SOURCE_ID_INVALID"
        if validity not in VALIDITIES:
            return records, "EVIDENCE_VALIDITY_INVALID_ENUM"
        if scope_status not in SCOPE_STATES:
            return records, "EVIDENCE_SCOPE_INVALID_ENUM"
        if failure_domain_id is not None and not _nonempty_string(
            failure_domain_id
        ):
            return records, "FAILURE_DOMAIN_ID_INVALID"

        records.append(copy.deepcopy(raw))

    return records, None


def _applicability_state(records: list[dict[str, Any]]) -> str:
    if not records:
        return "UNKNOWN"
    if any(record["validity"] == "INVALID" for record in records):
        return "INVALID"
    if any(
        record["validity"] == "UNKNOWN"
        or record["scope_status"] == "UNKNOWN"
        for record in records
    ):
        return "UNKNOWN"
    if any(
        record["validity"] == "STALE"
        or record["scope_status"] == "WRONG"
        for record in records
    ):
        return "NOT_APPLICABLE"
    if any(record["scope_status"] == "PARTIAL" for record in records):
        return "PARTIAL"
    return "APPLICABLE"


def _validate_provenance(
    *,
    state_id: str,
    records: list[dict[str, Any]],
    provenance_receipts: Any,
) -> tuple[str, list[str], str | None]:
    if not isinstance(provenance_receipts, list):
        return "INVALID", [], "PROVENANCE_RECEIPTS_NOT_ARRAY"

    record_by_id = {record["evidence_id"]: record for record in records}
    receipt_ids: set[str] = set()
    by_evidence: dict[str, dict[str, Any]] = {}
    ordered_receipt_ids: list[str] = []

    for raw in provenance_receipts:
        if not isinstance(raw, dict) or set(raw) != PROVENANCE_RECEIPT_KEYS:
            return "INVALID", ordered_receipt_ids, "PROVENANCE_RECEIPT_SCHEMA_INVALID"

        receipt_id = raw["receipt_id"]
        if not _nonempty_string(receipt_id):
            return "INVALID", ordered_receipt_ids, "PROVENANCE_RECEIPT_ID_INVALID"
        if receipt_id in receipt_ids:
            return "INVALID", ordered_receipt_ids, "DUPLICATE_PROVENANCE_RECEIPT_ID"
        receipt_ids.add(receipt_id)
        ordered_receipt_ids.append(receipt_id)

        if raw["state_id"] != state_id:
            return "INVALID", ordered_receipt_ids, "PROVENANCE_RECEIPT_STATE_MISMATCH"
        evidence_id = raw["evidence_id"]
        if evidence_id not in record_by_id:
            return "INVALID", ordered_receipt_ids, "PROVENANCE_RECEIPT_EVIDENCE_MISMATCH"
        if evidence_id in by_evidence:
            return "INVALID", ordered_receipt_ids, "MULTIPLE_PROVENANCE_RECEIPTS_FOR_EVIDENCE"
        if raw["source_id"] != record_by_id[evidence_id]["source_id"]:
            return "INVALID", ordered_receipt_ids, "PROVENANCE_RECEIPT_SOURCE_MISMATCH"
        if raw["status"] not in PROVENANCE_STATES:
            return "INVALID", ordered_receipt_ids, "PROVENANCE_RECEIPT_STATUS_INVALID"
        by_evidence[evidence_id] = raw

    states: list[str] = []
    for record in records:
        receipt = by_evidence.get(record["evidence_id"])
        states.append("UNKNOWN" if receipt is None else receipt["status"])

    if any(state == "INVALID" for state in states):
        return "INVALID", ordered_receipt_ids, None
    if any(state == "UNKNOWN" for state in states):
        return "UNKNOWN", ordered_receipt_ids, None
    if any(state == "PARTIAL" for state in states):
        return "PARTIAL", ordered_receipt_ids, None
    if records and states and all(state == "ESTABLISHED" for state in states):
        return "ESTABLISHED", ordered_receipt_ids, None
    return "UNKNOWN", ordered_receipt_ids, None


def _validate_dependency(
    *,
    state_id: str,
    records: list[dict[str, Any]],
    dependency_receipt: Any,
) -> tuple[str, str | None, str | None]:
    if dependency_receipt is None:
        return "UNKNOWN", None, None
    if not isinstance(dependency_receipt, dict) or set(
        dependency_receipt
    ) != DEPENDENCY_RECEIPT_KEYS:
        return "UNKNOWN", None, "DEPENDENCY_RECEIPT_SCHEMA_INVALID"

    receipt_id = dependency_receipt["receipt_id"]
    if not _nonempty_string(receipt_id):
        return "UNKNOWN", None, "DEPENDENCY_RECEIPT_ID_INVALID"
    if dependency_receipt["state_id"] != state_id:
        return "UNKNOWN", receipt_id, "DEPENDENCY_RECEIPT_STATE_MISMATCH"

    status = dependency_receipt["status"]
    if status not in DEPENDENCY_STATES:
        return "UNKNOWN", receipt_id, "DEPENDENCY_RECEIPT_STATUS_INVALID"

    evidence_ids = dependency_receipt["evidence_ids"]
    if not _valid_string_list(evidence_ids):
        return "UNKNOWN", receipt_id, "DEPENDENCY_EVIDENCE_IDS_INVALID"

    record_ids = {record["evidence_id"] for record in records}
    if not set(evidence_ids).issubset(record_ids):
        return "UNKNOWN", receipt_id, "DEPENDENCY_RECEIPT_EVIDENCE_MISMATCH"

    failure_domains = dependency_receipt["failure_domains"]
    if not isinstance(failure_domains, dict):
        return "UNKNOWN", receipt_id, "DEPENDENCY_FAILURE_DOMAINS_NOT_OBJECT"
    if any(
        not _nonempty_string(key)
        or value is not None
        and not _nonempty_string(value)
        for key, value in failure_domains.items()
    ):
        return "UNKNOWN", receipt_id, "DEPENDENCY_FAILURE_DOMAIN_INVALID"
    if not set(failure_domains).issubset(record_ids):
        return "UNKNOWN", receipt_id, "DEPENDENCY_FAILURE_DOMAIN_EVIDENCE_MISMATCH"

    if status == "RESOLVED":
        if set(evidence_ids) != record_ids:
            return "UNKNOWN", receipt_id, "RESOLVED_DEPENDENCY_COVERAGE_MISMATCH"
        if set(failure_domains) != record_ids:
            return "UNKNOWN", receipt_id, "RESOLVED_FAILURE_DOMAIN_COVERAGE_MISMATCH"
        for record in records:
            expected = record["failure_domain_id"]
            if not _nonempty_string(expected):
                return "UNKNOWN", receipt_id, "RESOLVED_DEPENDENCY_REQUIRES_FAILURE_DOMAIN"
            if failure_domains[record["evidence_id"]] != expected:
                return "UNKNOWN", receipt_id, "RESOLVED_FAILURE_DOMAIN_VALUE_MISMATCH"

    return status, receipt_id, None


def assess_evidence_provenance(
    *,
    state_id: str,
    evidence_set: Any,
    provenance_receipts: Any,
    dependency_receipt: Any,
    missing_evidence: Any,
    drift_state: str,
) -> dict[str, Any]:
    """Assess bounded Layer B evidence/provenance representation.

    v0.1 establishes only structural, state-bound coherence of explicit
    evidence records and explicit provenance/dependency receipts.

    It does not authenticate a real-world source, infer source independence,
    evaluate free text, establish factual truth, or authorize closure.
    """
    if not _nonempty_string(state_id):
        return _invalid("STATE_ID_REQUIRED", state_id=None)

    if drift_state not in DRIFT_STATES:
        return _invalid(
            "DRIFT_STATE_INVALID",
            state_id=state_id,
            drift_state="NOT_ASSESSED",
        )

    if not _valid_string_list(missing_evidence):
        return _invalid(
            "MISSING_EVIDENCE_LEDGER_INVALID",
            state_id=state_id,
            drift_state=drift_state,
        )

    records, record_error = _validate_records(evidence_set)
    if record_error is not None:
        return _invalid(
            record_error,
            state_id=state_id,
            evidence_set=records,
            missing_evidence=missing_evidence,
            drift_state=drift_state,
        )

    applicability_state = _applicability_state(records)
    if applicability_state == "INVALID":
        return _invalid(
            "EVIDENCE_RECORD_INVALID",
            state_id=state_id,
            evidence_set=records,
            missing_evidence=missing_evidence,
            drift_state=drift_state,
            applicability_state="INVALID",
            provenance_state="UNKNOWN",
        )

    provenance_state, provenance_receipt_ids, provenance_error = (
        _validate_provenance(
            state_id=state_id,
            records=records,
            provenance_receipts=provenance_receipts,
        )
    )
    if provenance_error is not None or provenance_state == "INVALID":
        return _invalid(
            provenance_error or "PROVENANCE_INVALID",
            state_id=state_id,
            evidence_set=records,
            missing_evidence=missing_evidence,
            drift_state=drift_state,
            applicability_state=applicability_state,
            provenance_state="INVALID",
            provenance_receipt_ids=provenance_receipt_ids,
        )

    dependency_state, dependency_receipt_id, dependency_error = (
        _validate_dependency(
            state_id=state_id,
            records=records,
            dependency_receipt=dependency_receipt,
        )
    )
    if dependency_error is not None:
        return _invalid(
            dependency_error,
            state_id=state_id,
            evidence_set=records,
            missing_evidence=missing_evidence,
            drift_state=drift_state,
            applicability_state=applicability_state,
            provenance_state=provenance_state,
            dependency_state="UNKNOWN",
            provenance_receipt_ids=provenance_receipt_ids,
            dependency_receipt_id=dependency_receipt_id,
        )

    if not records:
        status = EVIDENCE_UNKNOWN
        reason = "EVIDENCE_SET_EMPTY"
    elif (
        provenance_state == "UNKNOWN"
        or applicability_state == "UNKNOWN"
        or dependency_state == "UNKNOWN"
        or drift_state in {"UNRESOLVED", "NOT_ASSESSED"}
    ):
        status = EVIDENCE_UNKNOWN
        reason = "EVIDENCE_STATE_UNRESOLVED"
    elif (
        provenance_state == "PARTIAL"
        or applicability_state in {"PARTIAL", "NOT_APPLICABLE"}
        or dependency_state in {"PARTIAL", "CONFLICTING"}
        or bool(missing_evidence)
        or drift_state == "MATERIAL_DRIFT"
    ):
        status = EVIDENCE_PARTIAL
        reason = "EVIDENCE_STATE_PARTIAL_OR_REEVALUATION_REQUIRED"
    elif (
        provenance_state == "ESTABLISHED"
        and applicability_state == "APPLICABLE"
        and dependency_state == "RESOLVED"
        and not missing_evidence
        and drift_state == "NO_DRIFT"
    ):
        status = EVIDENCE_APPLICABLE
        reason = "EXPLICIT_EVIDENCE_PROVENANCE_STATE_APPLICABLE"
    else:
        status = EVIDENCE_UNKNOWN
        reason = "EVIDENCE_STATE_UNRESOLVED"

    diagnostics: list[str] = []
    if provenance_state != "ESTABLISHED":
        diagnostics.append("PROVENANCE_NOT_ESTABLISHED")
    if applicability_state != "APPLICABLE":
        diagnostics.append("APPLICABILITY_NOT_ESTABLISHED")
    if dependency_state != "RESOLVED":
        diagnostics.append("DEPENDENCY_NOT_RESOLVED")
    if missing_evidence:
        diagnostics.append("MISSING_EVIDENCE_PRESENT")
    if drift_state != "NO_DRIFT":
        diagnostics.append("DRIFT_NOT_CLEAR")

    return _result(
        state_id=state_id,
        status=status,
        reason=reason,
        provenance_state=provenance_state,
        applicability_state=applicability_state,
        dependency_state=dependency_state,
        evidence_set=records,
        missing_evidence=missing_evidence,
        drift_state=drift_state,
        diagnostics=diagnostics,
        provenance_receipt_ids=provenance_receipt_ids,
        dependency_receipt_id=dependency_receipt_id,
    )
