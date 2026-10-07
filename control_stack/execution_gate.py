from __future__ import annotations

import copy
from typing import Any, Callable


EXECUTION_GATE_VERSION = "EXECUTION_GATE_V0_1"
EXECUTION_GATE_BOUNDARY = (
    "EXACT_CONTROLLER_STATE_AUTHORITY_IDEMPOTENCY_HUMAN_AND_SINGLE_ATTEMPT_ONLY"
)

EXECUTION_ALLOWED = "EXECUTION_ALLOWED"
EXECUTION_BLOCKED = "EXECUTION_BLOCKED"
EXECUTION_INVALID = "EXECUTION_INVALID"

VALID_DECISIONS = {"NOT_RUN", "CONTINUE", "HOLD", "STOP", "ESCALATE"}
VALID_AUTHORITY_STATES = {
    "ESTABLISHED",
    "NOT_ESTABLISHED",
    "UNKNOWN",
    "REVOKED",
    "EXPIRED",
    "NOT_ASSESSED",
}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _execution(
    *,
    attempted: bool,
    executed: bool | None,
    status: str,
    effect_handle: str | None,
    idempotency_key: str,
    pre_execution_state_id: str,
    receipt_id: str,
) -> dict[str, Any]:
    return {
        "attempted": attempted,
        "executed": executed,
        "execution_status": status,
        "effect_handle": effect_handle,
        "idempotency_key": idempotency_key,
        "pre_execution_state_id": pre_execution_state_id,
        "receipt_id": receipt_id,
    }


def _result(
    *,
    gate_status: str,
    reason: str,
    blockers: list[str],
    action_id: str,
    controller_run_id: str,
    controller_decision: str,
    controller_state_id: str,
    current_state_id: str,
    controller_state_version: str,
    current_state_version: str,
    cfc_authority_state: str,
    current_authority_state: str,
    human_review_required: bool,
    human_review_approved: bool,
    transaction_required: bool,
    transaction_supported: bool,
    execution: dict[str, Any],
    prior_receipt_id: str | None = None,
) -> dict[str, Any]:
    return {
        "version": EXECUTION_GATE_VERSION,
        "gate_status": gate_status,
        "reason": reason,
        "blockers": list(blockers),
        "action_id": action_id,
        "controller_run_id": controller_run_id,
        "controller_decision": controller_decision,
        "controller_state_id": controller_state_id,
        "current_state_id": current_state_id,
        "controller_state_version": controller_state_version,
        "current_state_version": current_state_version,
        "cfc_authority_state": cfc_authority_state,
        "current_authority_state": current_authority_state,
        "human_review_required": human_review_required,
        "human_review_approved": human_review_approved,
        "transaction_required": transaction_required,
        "transaction_supported": transaction_supported,
        "prior_receipt_id": prior_receipt_id,
        "execution": copy.deepcopy(execution),
        "authority_effect": "DOES_NOT_CREATE_AUTHORITY",
        "boundary": EXECUTION_GATE_BOUNDARY,
    }


def _input_error(
    reason: str,
    *,
    action_id: Any,
    controller_run_id: Any,
    controller_decision: Any,
    controller_state_id: Any,
    current_state_id: Any,
    controller_state_version: Any,
    current_state_version: Any,
    cfc_authority_state: Any,
    current_authority_state: Any,
    human_review_required: Any,
    human_review_approved: Any,
    transaction_required: Any,
    transaction_supported: Any,
    idempotency_key: Any,
    receipt_id: Any,
) -> dict[str, Any]:
    safe_action = action_id if _nonempty(action_id) else "INVALID_ACTION"
    safe_run = (
        controller_run_id
        if _nonempty(controller_run_id)
        else "INVALID_CONTROLLER_RUN"
    )
    safe_decision = (
        controller_decision
        if controller_decision in VALID_DECISIONS
        else "NOT_RUN"
    )
    safe_controller_state = (
        controller_state_id
        if _nonempty(controller_state_id)
        else "UNKNOWN_CONTROLLER_STATE"
    )
    safe_current_state = (
        current_state_id if _nonempty(current_state_id) else "UNKNOWN_STATE"
    )
    safe_controller_version = (
        controller_state_version
        if _nonempty(controller_state_version)
        else "UNKNOWN_CONTROLLER_VERSION"
    )
    safe_current_version = (
        current_state_version
        if _nonempty(current_state_version)
        else "UNKNOWN_STATE_VERSION"
    )
    safe_idem = idempotency_key if _nonempty(idempotency_key) else "INVALID_IDEMPOTENCY_KEY"
    safe_receipt = receipt_id if _nonempty(receipt_id) else "INVALID_RECEIPT_ID"
    execution = _execution(
        attempted=False,
        executed=False,
        status="BLOCKED",
        effect_handle=None,
        idempotency_key=safe_idem,
        pre_execution_state_id=safe_current_state,
        receipt_id=safe_receipt,
    )
    return _result(
        gate_status=EXECUTION_INVALID,
        reason=reason,
        blockers=[reason],
        action_id=safe_action,
        controller_run_id=safe_run,
        controller_decision=safe_decision,
        controller_state_id=safe_controller_state,
        current_state_id=safe_current_state,
        controller_state_version=safe_controller_version,
        current_state_version=safe_current_version,
        cfc_authority_state=(
            cfc_authority_state
            if cfc_authority_state in VALID_AUTHORITY_STATES
            else "UNKNOWN"
        ),
        current_authority_state=(
            current_authority_state
            if current_authority_state in VALID_AUTHORITY_STATES
            else "UNKNOWN"
        ),
        human_review_required=bool(human_review_required),
        human_review_approved=bool(human_review_approved),
        transaction_required=bool(transaction_required),
        transaction_supported=bool(transaction_supported),
        execution=execution,
    )


def _prior_receipt_match(
    *,
    prior_execution_receipts: Any,
    action_id: str,
    idempotency_key: str,
) -> tuple[str | None, str | None]:
    if not isinstance(prior_execution_receipts, list):
        return "PRIOR_EXECUTION_RECEIPTS_NOT_ARRAY", None

    for raw in prior_execution_receipts:
        if not isinstance(raw, dict):
            return "PRIOR_EXECUTION_RECEIPT_INVALID", None
        prior_key = raw.get("idempotency_key")
        prior_action = raw.get("action_id")
        prior_receipt_id = raw.get("receipt_id")
        if not _nonempty(prior_key) or not _nonempty(prior_action):
            return "PRIOR_EXECUTION_RECEIPT_INVALID", None
        if prior_key != idempotency_key:
            continue
        if prior_action != action_id:
            return "IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_ACTION", (
                prior_receipt_id if _nonempty(prior_receipt_id) else None
            )
        return "IDEMPOTENCY_REPLAY_BLOCKED", (
            prior_receipt_id if _nonempty(prior_receipt_id) else None
        )
    return None, None


def assess_execution_gate(
    *,
    action_id: str,
    controller_run_id: str,
    controller_decision: str,
    controller_blockers: list[str],
    controller_state_id: str,
    current_state_id: str,
    controller_state_version: str,
    current_state_version: str,
    cfc_authority_state: str,
    current_authority_state: str,
    idempotency_key: str,
    receipt_id: str,
    prior_execution_receipts: list[dict[str, Any]],
    human_review_required: bool = False,
    human_review_approved: bool = False,
    transaction_required: bool = False,
    transaction_supported: bool = False,
) -> dict[str, Any]:
    """Evaluate whether one exact action may be attempted.

    This gate enforces already-established authority. It never creates
    authority and never upgrades a non-CONTINUE controller decision.
    """
    values = (
        action_id,
        controller_run_id,
        controller_state_id,
        current_state_id,
        controller_state_version,
        current_state_version,
        idempotency_key,
        receipt_id,
    )
    if not all(_nonempty(value) for value in values):
        return _input_error(
            "EXECUTION_GATE_REQUIRED_IDENTITY_MISSING",
            action_id=action_id,
            controller_run_id=controller_run_id,
            controller_decision=controller_decision,
            controller_state_id=controller_state_id,
            current_state_id=current_state_id,
            controller_state_version=controller_state_version,
            current_state_version=current_state_version,
            cfc_authority_state=cfc_authority_state,
            current_authority_state=current_authority_state,
            human_review_required=human_review_required,
            human_review_approved=human_review_approved,
            transaction_required=transaction_required,
            transaction_supported=transaction_supported,
            idempotency_key=idempotency_key,
            receipt_id=receipt_id,
        )

    if controller_decision not in VALID_DECISIONS:
        return _input_error(
            "CONTROLLER_DECISION_INVALID",
            action_id=action_id,
            controller_run_id=controller_run_id,
            controller_decision=controller_decision,
            controller_state_id=controller_state_id,
            current_state_id=current_state_id,
            controller_state_version=controller_state_version,
            current_state_version=current_state_version,
            cfc_authority_state=cfc_authority_state,
            current_authority_state=current_authority_state,
            human_review_required=human_review_required,
            human_review_approved=human_review_approved,
            transaction_required=transaction_required,
            transaction_supported=transaction_supported,
            idempotency_key=idempotency_key,
            receipt_id=receipt_id,
        )

    if cfc_authority_state not in VALID_AUTHORITY_STATES:
        return _input_error(
            "CFC_AUTHORITY_STATE_INVALID",
            action_id=action_id,
            controller_run_id=controller_run_id,
            controller_decision=controller_decision,
            controller_state_id=controller_state_id,
            current_state_id=current_state_id,
            controller_state_version=controller_state_version,
            current_state_version=current_state_version,
            cfc_authority_state=cfc_authority_state,
            current_authority_state=current_authority_state,
            human_review_required=human_review_required,
            human_review_approved=human_review_approved,
            transaction_required=transaction_required,
            transaction_supported=transaction_supported,
            idempotency_key=idempotency_key,
            receipt_id=receipt_id,
        )

    if current_authority_state not in VALID_AUTHORITY_STATES:
        return _input_error(
            "CURRENT_AUTHORITY_STATE_INVALID",
            action_id=action_id,
            controller_run_id=controller_run_id,
            controller_decision=controller_decision,
            controller_state_id=controller_state_id,
            current_state_id=current_state_id,
            controller_state_version=controller_state_version,
            current_state_version=current_state_version,
            cfc_authority_state=cfc_authority_state,
            current_authority_state=current_authority_state,
            human_review_required=human_review_required,
            human_review_approved=human_review_approved,
            transaction_required=transaction_required,
            transaction_supported=transaction_supported,
            idempotency_key=idempotency_key,
            receipt_id=receipt_id,
        )

    if not isinstance(controller_blockers, list) or any(
        not _nonempty(item) for item in controller_blockers
    ):
        return _input_error(
            "CONTROLLER_BLOCKERS_INVALID",
            action_id=action_id,
            controller_run_id=controller_run_id,
            controller_decision=controller_decision,
            controller_state_id=controller_state_id,
            current_state_id=current_state_id,
            controller_state_version=controller_state_version,
            current_state_version=current_state_version,
            cfc_authority_state=cfc_authority_state,
            current_authority_state=current_authority_state,
            human_review_required=human_review_required,
            human_review_approved=human_review_approved,
            transaction_required=transaction_required,
            transaction_supported=transaction_supported,
            idempotency_key=idempotency_key,
            receipt_id=receipt_id,
        )

    if not all(
        isinstance(value, bool)
        for value in (
            human_review_required,
            human_review_approved,
            transaction_required,
            transaction_supported,
        )
    ):
        return _input_error(
            "EXECUTION_GATE_BOOLEAN_FLAG_INVALID",
            action_id=action_id,
            controller_run_id=controller_run_id,
            controller_decision=controller_decision,
            controller_state_id=controller_state_id,
            current_state_id=current_state_id,
            controller_state_version=controller_state_version,
            current_state_version=current_state_version,
            cfc_authority_state=cfc_authority_state,
            current_authority_state=current_authority_state,
            human_review_required=human_review_required,
            human_review_approved=human_review_approved,
            transaction_required=transaction_required,
            transaction_supported=transaction_supported,
            idempotency_key=idempotency_key,
            receipt_id=receipt_id,
        )

    blockers: list[str] = []
    if controller_decision != "CONTINUE":
        blockers.append("CONTROLLER_DECISION_NOT_CONTINUE")
    if controller_blockers:
        blockers.append("CONTROLLER_BLOCKERS_PRESENT")
    if cfc_authority_state != "ESTABLISHED":
        blockers.append("CFC_AUTHORITY_NOT_ESTABLISHED")
    if current_authority_state != "ESTABLISHED":
        blockers.append("CURRENT_AUTHORITY_NOT_ESTABLISHED")
    if controller_state_id != current_state_id:
        blockers.append("PRE_EXECUTION_STATE_ID_MISMATCH")
    if controller_state_version != current_state_version:
        blockers.append("PRE_EXECUTION_STATE_VERSION_MISMATCH")
    if human_review_required and not human_review_approved:
        blockers.append("HUMAN_REVIEW_REQUIRED")
    if transaction_required and not transaction_supported:
        blockers.append("TRANSACTION_BOUNDARY_UNAVAILABLE")

    prior_reason, prior_receipt_id = _prior_receipt_match(
        prior_execution_receipts=prior_execution_receipts,
        action_id=action_id,
        idempotency_key=idempotency_key,
    )
    if prior_reason is not None:
        blockers.append(prior_reason)

    execution = _execution(
        attempted=False,
        executed=False,
        status="BLOCKED" if blockers else "NOT_ATTEMPTED",
        effect_handle=None,
        idempotency_key=idempotency_key,
        pre_execution_state_id=current_state_id,
        receipt_id=receipt_id,
    )

    if blockers:
        return _result(
            gate_status=EXECUTION_BLOCKED,
            reason=blockers[0],
            blockers=blockers,
            action_id=action_id,
            controller_run_id=controller_run_id,
            controller_decision=controller_decision,
            controller_state_id=controller_state_id,
            current_state_id=current_state_id,
            controller_state_version=controller_state_version,
            current_state_version=current_state_version,
            cfc_authority_state=cfc_authority_state,
            current_authority_state=current_authority_state,
            human_review_required=human_review_required,
            human_review_approved=human_review_approved,
            transaction_required=transaction_required,
            transaction_supported=transaction_supported,
            execution=execution,
            prior_receipt_id=prior_receipt_id,
        )

    return _result(
        gate_status=EXECUTION_ALLOWED,
        reason="EXACT_PRE_EXECUTION_GATES_ESTABLISHED",
        blockers=[],
        action_id=action_id,
        controller_run_id=controller_run_id,
        controller_decision=controller_decision,
        controller_state_id=controller_state_id,
        current_state_id=current_state_id,
        controller_state_version=controller_state_version,
        current_state_version=current_state_version,
        cfc_authority_state=cfc_authority_state,
        current_authority_state=current_authority_state,
        human_review_required=human_review_required,
        human_review_approved=human_review_approved,
        transaction_required=transaction_required,
        transaction_supported=transaction_supported,
        execution=execution,
    )


def execute_with_gate(
    *,
    executor: Callable[[dict[str, Any]], dict[str, Any]] | None,
    action_payload: Any = None,
    **gate_inputs: Any,
) -> dict[str, Any]:
    """Attempt one effect only after the exact pre-execution gate passes.

    Executor contract:
      {"outcome": "EXECUTED", "effect_handle": "<non-empty>"}
      {"outcome": "NOT_EXECUTED", "effect_handle": None}
      {"outcome": "UNKNOWN", "effect_handle": <string-or-null>}

    An exception is classified as OUTCOME_UNKNOWN because the gate cannot
    safely infer whether an external side effect occurred before the error.
    """
    preflight = assess_execution_gate(**gate_inputs)
    if preflight["gate_status"] != EXECUTION_ALLOWED:
        return preflight

    execution = preflight["execution"]
    if not callable(executor):
        execution = _execution(
            attempted=False,
            executed=False,
            status="BLOCKED",
            effect_handle=None,
            idempotency_key=execution["idempotency_key"],
            pre_execution_state_id=execution["pre_execution_state_id"],
            receipt_id=execution["receipt_id"],
        )
        return {
            **preflight,
            "gate_status": EXECUTION_BLOCKED,
            "reason": "EXECUTOR_UNAVAILABLE",
            "blockers": ["EXECUTOR_UNAVAILABLE"],
            "execution": execution,
        }

    call = {
        "action_id": preflight["action_id"],
        "controller_run_id": preflight["controller_run_id"],
        "state_id": preflight["current_state_id"],
        "state_version": preflight["current_state_version"],
        "idempotency_key": execution["idempotency_key"],
        "receipt_id": execution["receipt_id"],
        "transaction_required": preflight["transaction_required"],
        "action_payload": copy.deepcopy(action_payload),
    }

    try:
        adapter_result = executor(copy.deepcopy(call))
    except Exception:
        execution = _execution(
            attempted=True,
            executed=None,
            status="OUTCOME_UNKNOWN",
            effect_handle=None,
            idempotency_key=execution["idempotency_key"],
            pre_execution_state_id=execution["pre_execution_state_id"],
            receipt_id=execution["receipt_id"],
        )
        return {
            **preflight,
            "gate_status": EXECUTION_ALLOWED,
            "reason": "EXECUTOR_EXCEPTION_OUTCOME_UNKNOWN",
            "execution": execution,
        }

    if not isinstance(adapter_result, dict):
        execution = _execution(
            attempted=True,
            executed=None,
            status="OUTCOME_UNKNOWN",
            effect_handle=None,
            idempotency_key=execution["idempotency_key"],
            pre_execution_state_id=execution["pre_execution_state_id"],
            receipt_id=execution["receipt_id"],
        )
        return {
            **preflight,
            "reason": "EXECUTOR_RESULT_INVALID_OUTCOME_UNKNOWN",
            "execution": execution,
        }

    outcome = adapter_result.get("outcome")
    effect_handle = adapter_result.get("effect_handle")
    if effect_handle is not None and not _nonempty(effect_handle):
        outcome = "UNKNOWN"
        effect_handle = None

    if outcome == "EXECUTED" and _nonempty(effect_handle):
        execution = _execution(
            attempted=True,
            executed=True,
            status="EXECUTED",
            effect_handle=effect_handle,
            idempotency_key=execution["idempotency_key"],
            pre_execution_state_id=execution["pre_execution_state_id"],
            receipt_id=execution["receipt_id"],
        )
        return {
            **preflight,
            "reason": "EXECUTOR_CONFIRMED_EFFECT",
            "execution": execution,
        }

    if outcome == "NOT_EXECUTED" and effect_handle is None:
        execution = _execution(
            attempted=True,
            executed=False,
            status="ATTEMPTED_NOT_EXECUTED",
            effect_handle=None,
            idempotency_key=execution["idempotency_key"],
            pre_execution_state_id=execution["pre_execution_state_id"],
            receipt_id=execution["receipt_id"],
        )
        return {
            **preflight,
            "reason": "EXECUTOR_CONFIRMED_NO_EFFECT",
            "execution": execution,
        }

    execution = _execution(
        attempted=True,
        executed=None,
        status="OUTCOME_UNKNOWN",
        effect_handle=effect_handle if _nonempty(effect_handle) else None,
        idempotency_key=execution["idempotency_key"],
        pre_execution_state_id=execution["pre_execution_state_id"],
        receipt_id=execution["receipt_id"],
    )
    return {
        **preflight,
        "reason": "EXECUTOR_OUTCOME_UNKNOWN",
        "execution": execution,
    }
