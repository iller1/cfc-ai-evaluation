from __future__ import annotations

import copy
from typing import Any

from control_stack.state_integrity import assess_state_integrity
from pro_beta.contracts import HAWMSnapshot, HAWMSnapshotIdentity
from pro_beta.state_integrity_adapter import assess_persisted_hawm_state_integrity
from pro_beta.service import (
    HAWM_STATE_IDENTITY_ADAPTER_VERSION,
    HAWM_STATE_IDENTITY_ARM_ID,
    HAWM_STATE_IDENTITY_CASE_ID,
)


STATE_INTEGRITY_ACCEPTANCE_VERSION = "STATE_INTEGRITY_ADVERSARIAL_ACCEPTANCE_V0_1"
STATE_INTEGRITY_ACCEPTANCE_BOUNDARY = (
    "SERVER_DERIVED_IN_MEMORY_VARIANTS_ONLY_NO_PERSISTENCE_NO_CFC_EXECUTION"
)


def _server_derived_inputs(
    *,
    current: HAWMSnapshot,
    previous: HAWMSnapshot | None,
    identity: HAWMSnapshotIdentity,
) -> tuple[dict[str, Any], dict[str, Any]]:
    observed_previous = previous.snapshot_id if previous is not None else None
    observed = {
        "case_id": HAWM_STATE_IDENTITY_CASE_ID,
        "arm_id": HAWM_STATE_IDENTITY_ARM_ID,
        "state_id": current.snapshot_id,
        "snapshot_id": current.snapshot_id,
        "lineage_id": current.conversation_id,
        "previous_state_id": observed_previous,
        "state_payload": copy.deepcopy(current.state),
    }
    expectation = {
        "case_id": identity.case_id,
        "arm_id": identity.arm_id,
        "current_snapshot_id": identity.snapshot_id,
        "lineage_id": identity.lineage_id,
        "expected_previous_state_id": identity.previous_state_id,
        "registered_snapshot_fingerprint": identity.registered_snapshot_fingerprint,
    }
    return observed, expectation


def _case_result(
    name: str,
    observed: dict[str, Any],
    expectation: dict[str, Any],
    *,
    expected_status: str,
    expected_reason: str,
) -> dict[str, Any]:
    result = assess_state_integrity(observed, expectation)
    passed = (
        result["status"] == expected_status
        and result["reason"] == expected_reason
        and result["authorization_effect"] == "DOES_NOT_AUTHORIZE_CLOSURE"
    )
    return {
        "case": name,
        "status": result["status"],
        "reason": result["reason"],
        "binding_status": result["binding_status"],
        "lineage_status": result["lineage_status"],
        "propagation_effect": result["propagation_effect"],
        "authorization_effect": result["authorization_effect"],
        "expected_status": expected_status,
        "expected_reason": expected_reason,
        "pass": passed,
    }


def run_state_integrity_adversarial_acceptance(
    *,
    current: HAWMSnapshot,
    previous: HAWMSnapshot | None,
    identity: HAWMSnapshotIdentity,
) -> dict[str, Any]:
    """Run non-persistent adversarial variants against the deployed primitive.

    All baseline identity values come from persisted server-side state and the
    persisted identity receipt. The caller cannot supply case, arm, snapshot,
    lineage, predecessor or fingerprint claims.

    Variants are copies created only in memory. This function performs no
    persistence and does not execute CFC.
    """

    baseline = assess_persisted_hawm_state_integrity(
        current=current,
        previous=previous,
        identity=identity,
    )
    if baseline["status"] != "STATE_VALID":
        return {
            "version": STATE_INTEGRITY_ACCEPTANCE_VERSION,
            "status": "ACCEPTANCE_UNRESOLVED",
            "reason": "BASELINE_STATE_NOT_VALID",
            "baseline_status": baseline["status"],
            "baseline_reason": baseline["reason"],
            "current_snapshot_id": current.snapshot_id,
            "identity_adapter_version": identity.adapter_version,
            "read_only": True,
            "persistence_actions": [],
            "cfc_executed": False,
            "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
            "boundary": STATE_INTEGRITY_ACCEPTANCE_BOUNDARY,
            "cases": [],
        }

    if identity.adapter_version != HAWM_STATE_IDENTITY_ADAPTER_VERSION:
        return {
            "version": STATE_INTEGRITY_ACCEPTANCE_VERSION,
            "status": "ACCEPTANCE_UNRESOLVED",
            "reason": "IDENTITY_ADAPTER_VERSION_UNSUPPORTED",
            "baseline_status": baseline["status"],
            "baseline_reason": baseline["reason"],
            "current_snapshot_id": current.snapshot_id,
            "identity_adapter_version": identity.adapter_version,
            "read_only": True,
            "persistence_actions": [],
            "cfc_executed": False,
            "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
            "boundary": STATE_INTEGRITY_ACCEPTANCE_BOUNDARY,
            "cases": [],
        }

    observed, expectation = _server_derived_inputs(
        current=current,
        previous=previous,
        identity=identity,
    )

    cross_case = copy.deepcopy(observed)
    cross_case["case_id"] = observed["case_id"] + "::ADVERSARIAL"

    cross_arm = copy.deepcopy(observed)
    cross_arm["arm_id"] = str(observed["arm_id"]) + "::ADVERSARIAL"

    wrong_lineage = copy.deepcopy(observed)
    wrong_lineage["lineage_id"] = observed["lineage_id"] + "::ADVERSARIAL"

    stale_snapshot = copy.deepcopy(observed)
    stale_snapshot["state_id"] = observed["state_id"] + "::STALE"
    stale_snapshot["snapshot_id"] = observed["snapshot_id"] + "::STALE"

    changed_payload = copy.deepcopy(observed)
    changed_payload["state_payload"] = {
        "__state_integrity_acceptance_probe__": "MUTATED_IN_MEMORY",
        "original_payload": changed_payload["state_payload"],
    }

    wrong_predecessor = copy.deepcopy(observed)
    wrong_predecessor["previous_state_id"] = (
        str(observed["previous_state_id"]) + "::ADVERSARIAL"
    )

    cases = [
        _case_result(
            "CROSS_CASE_SUBSTITUTION",
            cross_case,
            expectation,
            expected_status="STATE_INVALID",
            expected_reason="CASE_ID_MISMATCH",
        ),
        _case_result(
            "CROSS_ARM_SUBSTITUTION",
            cross_arm,
            expectation,
            expected_status="STATE_INVALID",
            expected_reason="ARM_ID_MISMATCH",
        ),
        _case_result(
            "LINEAGE_SUBSTITUTION",
            wrong_lineage,
            expectation,
            expected_status="STATE_INVALID",
            expected_reason="LINEAGE_ID_MISMATCH",
        ),
        _case_result(
            "STALE_SNAPSHOT",
            stale_snapshot,
            expectation,
            expected_status="STATE_UNRESOLVED",
            expected_reason="CURRENT_SNAPSHOT_MISMATCH",
        ),
        _case_result(
            "SAME_SNAPSHOT_CHANGED_PAYLOAD",
            changed_payload,
            expectation,
            expected_status="STATE_INVALID",
            expected_reason="SNAPSHOT_FINGERPRINT_MISMATCH",
        ),
        _case_result(
            "PREDECESSOR_MISMATCH",
            wrong_predecessor,
            expectation,
            expected_status="STATE_UNRESOLVED",
            expected_reason="PREDECESSOR_MISMATCH",
        ),
    ]

    passed = all(item["pass"] for item in cases)
    return {
        "version": STATE_INTEGRITY_ACCEPTANCE_VERSION,
        "status": "ACCEPTANCE_PASS" if passed else "ACCEPTANCE_FAIL",
        "reason": (
            "ALL_ADVERSARIAL_VARIANTS_FAILED_CLOSED_AS_EXPECTED"
            if passed
            else "ONE_OR_MORE_ADVERSARIAL_VARIANTS_DID_NOT_FAIL_CLOSED"
        ),
        "baseline_status": baseline["status"],
        "baseline_reason": baseline["reason"],
        "current_snapshot_id": current.snapshot_id,
        "identity_adapter_version": identity.adapter_version,
        "read_only": True,
        "persistence_actions": [],
        "cfc_executed": False,
        "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
        "boundary": STATE_INTEGRITY_ACCEPTANCE_BOUNDARY,
        "cases": cases,
    }
