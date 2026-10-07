from __future__ import annotations

import hashlib
from typing import Any

from control_stack.execution_gate import (
    EXECUTION_BLOCKED,
    EXECUTION_GATE_BOUNDARY,
    EXECUTION_GATE_VERSION,
    assess_execution_gate,
)
from pro_beta.contracts import (
    CFCRun,
    ExecutionReceiptRecord,
    HAWMSnapshot,
    HAWMSnapshotIdentity,
)
from pro_beta.service import HAWM_STATE_IDENTITY_ADAPTER_VERSION


PRO_BETA_EXECUTION_GATE_ADAPTER_VERSION = (
    "PRO_BETA_EXECUTION_GATE_ADAPTER_V0_1"
)
PRO_BETA_EXECUTION_GATE_BOUNDARY = (
    "PERSISTED_CURRENT_STATE_AND_BOUND_SYNTHETIC_CFC_RUN_PREFLIGHT_ONLY_"
    "NO_REAL_ACTION_EXECUTION"
)
PREFLIGHT_ACTION_ID = "PRO_BETA_EXECUTION_PREFLIGHT_ONLY"


def _token(prefix: str, *parts: str) -> str:
    payload = "|".join(parts).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    return f"{prefix}:{digest}"


def _blocked_without_gate(
    reason: str,
    *,
    current_snapshot_id: str | None = None,
    controller_run_id: str | None = None,
    state_integrity_status: str | None = None,
) -> dict[str, Any]:
    state_id = current_snapshot_id or "UNKNOWN_STATE"
    run_id = controller_run_id or "UNKNOWN_CONTROLLER_RUN"
    return {
        "adapter_version": PRO_BETA_EXECUTION_GATE_ADAPTER_VERSION,
        "version": EXECUTION_GATE_VERSION,
        "gate_status": EXECUTION_BLOCKED,
        "reason": reason,
        "blockers": [reason],
        "action_id": PREFLIGHT_ACTION_ID,
        "controller_run_id": run_id,
        "controller_decision": "HOLD",
        "controller_state_id": state_id,
        "current_state_id": state_id,
        "controller_state_version": "UNKNOWN",
        "current_state_version": "UNKNOWN",
        "cfc_authority_state": "NOT_ESTABLISHED",
        "current_authority_state": "NOT_ESTABLISHED",
        "human_review_required": False,
        "human_review_approved": False,
        "transaction_required": False,
        "transaction_supported": False,
        "prior_receipt_id": None,
        "execution": {
            "attempted": False,
            "executed": False,
            "execution_status": "BLOCKED",
            "effect_handle": None,
            "idempotency_key": _token(
                "preflight-idem", run_id, state_id, reason
            ),
            "pre_execution_state_id": state_id,
            "receipt_id": _token(
                "preflight-receipt", run_id, state_id, reason
            ),
        },
        "authority_effect": "DOES_NOT_CREATE_AUTHORITY",
        "boundary": EXECUTION_GATE_BOUNDARY,
        "adapter_boundary": PRO_BETA_EXECUTION_GATE_BOUNDARY,
        "state_integrity_status": state_integrity_status or "UNKNOWN",
        "read_only": True,
        "executor_called": False,
        "persistence_actions": [],
        "synthetic_cfc_only": True,
    }


def _normalize_synthetic_cfc(
    run: CFCRun,
) -> tuple[str, list[str], str | None]:
    """Normalize the current demonstrator without upgrading demo closure.

    The present Pro Beta CFC paths execute synthetic fixtures / DemoSubject
    analogies. A frozen-controller closure therefore cannot be translated into
    real action CONTINUE.
    """
    if run.controller_anchor != "0.2.90rc1":
        return "HOLD", ["FROZEN_CFC_ANCHOR_MISMATCH"], None

    raw = run.controller_result
    presentation = run.presentation
    if not isinstance(raw, dict) or not isinstance(presentation, dict):
        return "HOLD", ["CFC_RUN_REPRESENTATION_INVALID"], None

    closure = raw.get("control_closure")
    decision = presentation.get("decision")
    if not isinstance(closure, bool):
        return "HOLD", ["CFC_CONTROL_CLOSURE_NOT_BOOLEAN"], None

    expected_presentation = "ALLOW" if closure else "STOP"
    if decision != expected_presentation:
        return "HOLD", ["CFC_RUN_REPRESENTATION_MISMATCH"], None

    if closure:
        return (
            "HOLD",
            [
                "SYNTHETIC_CFC_CLOSURE_NOT_REAL_ACTION_AUTHORITY",
                "REAL_ACTION_AUTHORITY_NOT_ESTABLISHED",
            ],
            "SYNTHETIC_CLOSURE_ONLY",
        )

    return (
        "STOP",
        [
            "FROZEN_CFC_CONTROL_CLOSURE_FALSE",
            "REAL_ACTION_AUTHORITY_NOT_ESTABLISHED",
        ],
        "SYNTHETIC_STOP",
    )


def assess_persisted_execution_preflight(
    *,
    current: HAWMSnapshot,
    current_identity: HAWMSnapshotIdentity,
    state_integrity_result: dict[str, Any],
    cfc_run: CFCRun | None,
    controller_identity: HAWMSnapshotIdentity | None,
    prior_execution_receipts: list[ExecutionReceiptRecord],
) -> dict[str, Any]:
    """Read-only execution preflight for current Pro Beta.

    No executor is accepted or invoked. The adapter derives every control fact
    from persisted server state. Current Pro Beta CFC closure is synthetic and
    is never upgraded to real-action CONTINUE.
    """
    if state_integrity_result.get("status") != "STATE_VALID":
        return _blocked_without_gate(
            "STATE_INTEGRITY_NOT_VALID",
            current_snapshot_id=current.snapshot_id,
            controller_run_id=(cfc_run.run_id if cfc_run else None),
            state_integrity_status=state_integrity_result.get("status"),
        )

    if (
        state_integrity_result.get("snapshot_id") != current.snapshot_id
        or state_integrity_result.get("state_id") != current.snapshot_id
    ):
        return _blocked_without_gate(
            "STATE_INTEGRITY_RESULT_BINDING_MISMATCH",
            current_snapshot_id=current.snapshot_id,
            controller_run_id=(cfc_run.run_id if cfc_run else None),
            state_integrity_status=state_integrity_result.get("status"),
        )

    if (
        state_integrity_result.get("authorization_effect")
        != "DOES_NOT_AUTHORIZE_CLOSURE"
    ):
        return _blocked_without_gate(
            "STATE_INTEGRITY_AUTHORIZATION_BOUNDARY_MISMATCH",
            current_snapshot_id=current.snapshot_id,
            controller_run_id=(cfc_run.run_id if cfc_run else None),
            state_integrity_status=state_integrity_result.get("status"),
        )

    if (
        current_identity.adapter_version
        != HAWM_STATE_IDENTITY_ADAPTER_VERSION
    ):
        return _blocked_without_gate(
            "CURRENT_IDENTITY_ADAPTER_VERSION_UNSUPPORTED",
            current_snapshot_id=current.snapshot_id,
            controller_run_id=(cfc_run.run_id if cfc_run else None),
            state_integrity_status=state_integrity_result.get("status"),
        )

    if (
        current_identity.snapshot_id != current.snapshot_id
        or current_identity.conversation_id != current.conversation_id
        or current_identity.state_id != current.snapshot_id
    ):
        return _blocked_without_gate(
            "CURRENT_IDENTITY_BINDING_MISMATCH",
            current_snapshot_id=current.snapshot_id,
            controller_run_id=(cfc_run.run_id if cfc_run else None),
            state_integrity_status=state_integrity_result.get("status"),
        )

    if cfc_run is None:
        return _blocked_without_gate(
            "BOUND_CFC_RUN_NOT_FOUND",
            current_snapshot_id=current.snapshot_id,
            state_integrity_status=state_integrity_result.get("status"),
        )

    if cfc_run.case_id != "HAWM_STRUCTURED_CUSTOM":
        return _blocked_without_gate(
            "CFC_RUN_CASE_NOT_SUPPORTED_FOR_EXECUTION_PREFLIGHT",
            current_snapshot_id=current.snapshot_id,
            controller_run_id=cfc_run.run_id,
            state_integrity_status=state_integrity_result.get("status"),
        )

    if cfc_run.conversation_id != current.conversation_id:
        return _blocked_without_gate(
            "CFC_RUN_CONVERSATION_MISMATCH",
            current_snapshot_id=current.snapshot_id,
            controller_run_id=cfc_run.run_id,
            state_integrity_status=state_integrity_result.get("status"),
        )

    if cfc_run.hawm_snapshot_id is None:
        return _blocked_without_gate(
            "CFC_RUN_NOT_STATE_BOUND",
            current_snapshot_id=current.snapshot_id,
            controller_run_id=cfc_run.run_id,
            state_integrity_status=state_integrity_result.get("status"),
        )

    if controller_identity is None:
        return _blocked_without_gate(
            "CONTROLLER_STATE_IDENTITY_NOT_FOUND",
            current_snapshot_id=current.snapshot_id,
            controller_run_id=cfc_run.run_id,
            state_integrity_status=state_integrity_result.get("status"),
        )

    if (
        controller_identity.adapter_version
        != HAWM_STATE_IDENTITY_ADAPTER_VERSION
    ):
        return _blocked_without_gate(
            "CONTROLLER_IDENTITY_ADAPTER_VERSION_UNSUPPORTED",
            current_snapshot_id=current.snapshot_id,
            controller_run_id=cfc_run.run_id,
            state_integrity_status=state_integrity_result.get("status"),
        )

    if (
        controller_identity.snapshot_id != cfc_run.hawm_snapshot_id
        or controller_identity.conversation_id != current.conversation_id
        or controller_identity.state_id != cfc_run.hawm_snapshot_id
    ):
        return _blocked_without_gate(
            "CONTROLLER_IDENTITY_BINDING_MISMATCH",
            current_snapshot_id=current.snapshot_id,
            controller_run_id=cfc_run.run_id,
            state_integrity_status=state_integrity_result.get("status"),
        )

    normalized_decision, synthetic_blockers, synthetic_result = (
        _normalize_synthetic_cfc(cfc_run)
    )

    idempotency_key = _token(
        "preflight-idem",
        cfc_run.run_id,
        cfc_run.hawm_snapshot_id,
        current.snapshot_id,
        PREFLIGHT_ACTION_ID,
    )
    receipt_id = _token(
        "preflight-receipt",
        cfc_run.run_id,
        cfc_run.hawm_snapshot_id,
        current.snapshot_id,
        PREFLIGHT_ACTION_ID,
    )

    prior = [
        {
            "receipt_id": receipt.receipt_id,
            "action_id": receipt.action_id,
            "idempotency_key": receipt.idempotency_key,
        }
        for receipt in prior_execution_receipts
    ]

    result = assess_execution_gate(
        action_id=PREFLIGHT_ACTION_ID,
        controller_run_id=cfc_run.run_id,
        controller_decision=normalized_decision,
        controller_blockers=synthetic_blockers,
        controller_state_id=cfc_run.hawm_snapshot_id,
        current_state_id=current.snapshot_id,
        controller_state_version=(
            controller_identity.registered_snapshot_fingerprint
        ),
        current_state_version=(
            current_identity.registered_snapshot_fingerprint
        ),
        cfc_authority_state="NOT_ESTABLISHED",
        current_authority_state="NOT_ESTABLISHED",
        idempotency_key=idempotency_key,
        receipt_id=receipt_id,
        prior_execution_receipts=prior,
        human_review_required=False,
        human_review_approved=False,
        transaction_required=False,
        transaction_supported=False,
    )
    result["adapter_version"] = PRO_BETA_EXECUTION_GATE_ADAPTER_VERSION
    result["adapter_boundary"] = PRO_BETA_EXECUTION_GATE_BOUNDARY
    result["state_integrity_status"] = state_integrity_result.get("status")
    result["read_only"] = True
    result["executor_called"] = False
    result["persistence_actions"] = []
    result["synthetic_cfc_only"] = True
    result["synthetic_cfc_result"] = synthetic_result
    result["raw_control_closure"] = (
        cfc_run.controller_result.get("control_closure")
        if isinstance(cfc_run.controller_result, dict)
        else None
    )
    result["presentation_decision"] = (
        cfc_run.presentation.get("decision")
        if isinstance(cfc_run.presentation, dict)
        else None
    )
    return result
