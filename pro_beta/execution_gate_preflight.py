from __future__ import annotations

from typing import Any

from control_stack.execution_gate import assess_execution_gate
from pro_beta.contracts import (
    ExecutionIntentRegistration,
    ExecutionReceiptRecord,
)
from pro_beta.service import EXECUTION_GATE_REGISTRY_ADAPTER_VERSION


PRO_BETA_EXECUTION_PREFLIGHT_VERSION = "PRO_BETA_EXECUTION_PREFLIGHT_V0_1"
PRO_BETA_EXECUTION_PREFLIGHT_BOUNDARY = (
    "PERSISTED_INTENT_STATE_INTEGRITY_EXECUTION_RECEIPTS_AND_EXPLICIT_NO_AUTHORITY_ONLY"
)
REAL_EXECUTION_AUTHORITY_STATUS = "HOLD_REAL_EXECUTION_AUTHORITY_UNAVAILABLE"


def unresolved_execution_preflight(
    reason: str,
    *,
    current_state_id: str | None = None,
    state_integrity_status: str = "UNKNOWN",
) -> dict[str, Any]:
    return {
        "version": PRO_BETA_EXECUTION_PREFLIGHT_VERSION,
        "preflight_status": "PREFLIGHT_UNRESOLVED",
        "gate_status": "EXECUTION_BLOCKED",
        "reason": reason,
        "blockers": [reason],
        "intent_id": None,
        "action_id": None,
        "controller_run_id": None,
        "controller_decision": "NOT_RUN",
        "current_state_id": current_state_id,
        "current_state_version": None,
        "state_integrity_status": state_integrity_status,
        "authority_status": REAL_EXECUTION_AUTHORITY_STATUS,
        "authority_source": "NONE",
        "prior_execution_receipt_count": 0,
        "execution": {
            "attempted": False,
            "executed": False,
            "execution_status": "BLOCKED",
            "effect_handle": None,
            "idempotency_key": None,
            "pre_execution_state_id": current_state_id,
            "receipt_id": None,
        },
        "read_only": True,
        "persistence_actions": [],
        "cfc_executed": False,
        "authority_effect": "DOES_NOT_CREATE_AUTHORITY",
        "boundary": PRO_BETA_EXECUTION_PREFLIGHT_BOUNDARY,
    }


def assess_persisted_execution_preflight(
    *,
    current_state_id: str,
    current_state_version: str,
    state_integrity_result: dict[str, Any],
    intent: ExecutionIntentRegistration,
    prior_receipts: list[ExecutionReceiptRecord],
) -> dict[str, Any]:
    """Read-only negative-authority Execution Gate preflight.

    v0.1 intentionally has no real execution-authority receipt source.
    It evaluates exact state/replay conditions while preserving the explicit
    real-authority HOLD. It never executes CFC or an external action.
    """

    if state_integrity_result.get("status") != "STATE_VALID":
        return unresolved_execution_preflight(
            "STATE_INTEGRITY_NOT_VALID",
            current_state_id=current_state_id,
            state_integrity_status=str(
                state_integrity_result.get("status") or "UNKNOWN"
            ),
        )

    if (
        state_integrity_result.get("snapshot_id") != current_state_id
        or state_integrity_result.get("state_id") != current_state_id
        or state_integrity_result.get("state_fingerprint")
        != current_state_version
    ):
        return unresolved_execution_preflight(
            "STATE_INTEGRITY_RESULT_BINDING_MISMATCH",
            current_state_id=current_state_id,
            state_integrity_status="STATE_VALID",
        )

    if (
        intent.adapter_version
        != EXECUTION_GATE_REGISTRY_ADAPTER_VERSION
    ):
        return unresolved_execution_preflight(
            "EXECUTION_INTENT_ADAPTER_VERSION_UNSUPPORTED",
            current_state_id=current_state_id,
            state_integrity_status="STATE_VALID",
        )

    prior = [
        {
            "receipt_id": row.receipt_id,
            "action_id": row.action_id,
            "idempotency_key": row.idempotency_key,
        }
        for row in prior_receipts
    ]

    result = assess_execution_gate(
        action_id=intent.action_id,
        controller_run_id=intent.controller_run_id,
        controller_decision="NOT_RUN",
        controller_blockers=[REAL_EXECUTION_AUTHORITY_STATUS],
        controller_state_id=intent.state_id,
        current_state_id=current_state_id,
        controller_state_version=intent.state_version,
        current_state_version=current_state_version,
        cfc_authority_state="NOT_ESTABLISHED",
        current_authority_state="NOT_ESTABLISHED",
        idempotency_key=intent.idempotency_key,
        receipt_id=intent.receipt_id,
        prior_execution_receipts=prior,
        human_review_required=intent.human_review_required,
        human_review_approved=False,
        transaction_required=intent.transaction_required,
        transaction_supported=False,
    )

    result.update(
        {
            "version": PRO_BETA_EXECUTION_PREFLIGHT_VERSION,
            "preflight_status": "PREFLIGHT_BLOCKED",
            "intent_id": intent.intent_id,
            "state_integrity_status": "STATE_VALID",
            "authority_status": REAL_EXECUTION_AUTHORITY_STATUS,
            "authority_source": "NONE",
            "prior_execution_receipt_count": len(prior_receipts),
            "read_only": True,
            "persistence_actions": [],
            "cfc_executed": False,
            "boundary": PRO_BETA_EXECUTION_PREFLIGHT_BOUNDARY,
        }
    )
    return result
