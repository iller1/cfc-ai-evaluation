from __future__ import annotations

from dataclasses import asdict
from typing import Any

from control_stack.state_integrity import (
    BLOCK_STATE,
    STATE_INTEGRITY_BOUNDARY,
    STATE_INTEGRITY_VERSION,
    STATE_INVALID,
    STATE_UNRESOLVED,
    assess_state_integrity,
)
from pro_beta.contracts import HAWMSnapshot, HAWMSnapshotIdentity
from pro_beta.service import (
    HAWM_STATE_IDENTITY_ADAPTER_VERSION,
    HAWM_STATE_IDENTITY_ARM_ID,
    HAWM_STATE_IDENTITY_CASE_ID,
)


PRO_BETA_STATE_INTEGRITY_ADAPTER_VERSION = (
    "PRO_BETA_STATE_INTEGRITY_ADAPTER_V0_1"
)
PRO_BETA_STATE_INTEGRITY_BOUNDARY = (
    "PERSISTED_HAWM_SNAPSHOT_AND_SERVER_IDENTITY_RECEIPT_ONLY"
)
PERSISTED_IDENTITY_SOURCE = "PERSISTED_HAWM_SNAPSHOT_IDENTITY"


def unresolved_state_integrity(
    reason: str,
    *,
    current_snapshot_id: str | None = None,
) -> dict[str, Any]:
    return {
        "adapter_version": PRO_BETA_STATE_INTEGRITY_ADAPTER_VERSION,
        "version": STATE_INTEGRITY_VERSION,
        "status": STATE_UNRESOLVED,
        "reason": reason,
        "case_id": HAWM_STATE_IDENTITY_CASE_ID,
        "arm_id": HAWM_STATE_IDENTITY_ARM_ID,
        "state_id": current_snapshot_id,
        "snapshot_id": current_snapshot_id,
        "lineage_id": None,
        "previous_state_id": None,
        "state_fingerprint": None,
        "binding_status": "UNKNOWN",
        "lineage_status": "UNKNOWN",
        "violations": [reason],
        "unresolved": [reason],
        "requires_review": True,
        "propagation_effect": BLOCK_STATE,
        "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
        "boundary": STATE_INTEGRITY_BOUNDARY,
        "adapter_boundary": PRO_BETA_STATE_INTEGRITY_BOUNDARY,
        "expectation_source": "NONE",
        "identity_adapter_version": None,
        "read_only": True,
    }


def _adapter_invalid(
    reason: str,
    *,
    current: HAWMSnapshot,
    identity: HAWMSnapshotIdentity,
) -> dict[str, Any]:
    return {
        "adapter_version": PRO_BETA_STATE_INTEGRITY_ADAPTER_VERSION,
        "version": STATE_INTEGRITY_VERSION,
        "status": STATE_INVALID,
        "reason": reason,
        "case_id": HAWM_STATE_IDENTITY_CASE_ID,
        "arm_id": HAWM_STATE_IDENTITY_ARM_ID,
        "state_id": current.snapshot_id,
        "snapshot_id": current.snapshot_id,
        "lineage_id": current.conversation_id,
        "previous_state_id": None,
        "state_fingerprint": None,
        "binding_status": "MISMATCH",
        "lineage_status": "INVALID",
        "violations": [reason],
        "unresolved": [reason],
        "requires_review": True,
        "propagation_effect": BLOCK_STATE,
        "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
        "boundary": STATE_INTEGRITY_BOUNDARY,
        "adapter_boundary": PRO_BETA_STATE_INTEGRITY_BOUNDARY,
        "expectation_source": PERSISTED_IDENTITY_SOURCE,
        "identity_adapter_version": identity.adapter_version,
        "read_only": True,
    }


def assess_persisted_hawm_state_integrity(
    *,
    current: HAWMSnapshot,
    previous: HAWMSnapshot | None,
    identity: HAWMSnapshotIdentity,
) -> dict[str, Any]:
    """Assess current HAWM state against a server-persisted identity receipt.

    The observed side is derived from current persisted host state and history.
    The expected side is derived from the identity receipt written when the
    snapshot was created. Request-supplied identity claims are not accepted.
    """

    if identity.adapter_version != HAWM_STATE_IDENTITY_ADAPTER_VERSION:
        result = unresolved_state_integrity(
            "IDENTITY_ADAPTER_VERSION_UNSUPPORTED",
            current_snapshot_id=current.snapshot_id,
        )
        result["expectation_source"] = PERSISTED_IDENTITY_SOURCE
        result["identity_adapter_version"] = identity.adapter_version
        return result

    for reason, valid in (
        (
            "IDENTITY_RECEIPT_SNAPSHOT_ID_MISMATCH",
            identity.snapshot_id == current.snapshot_id,
        ),
        (
            "IDENTITY_RECEIPT_CONVERSATION_MISMATCH",
            identity.conversation_id == current.conversation_id,
        ),
        (
            "IDENTITY_RECEIPT_STATE_ID_MISMATCH",
            identity.state_id == identity.snapshot_id,
        ),
    ):
        if not valid:
            return _adapter_invalid(
                reason,
                current=current,
                identity=identity,
            )

    observed_previous = previous.snapshot_id if previous is not None else None
    observed = {
        "case_id": HAWM_STATE_IDENTITY_CASE_ID,
        "arm_id": HAWM_STATE_IDENTITY_ARM_ID,
        "state_id": current.snapshot_id,
        "snapshot_id": current.snapshot_id,
        "lineage_id": current.conversation_id,
        "previous_state_id": observed_previous,
        "state_payload": current.state,
    }
    expectation = {
        "case_id": identity.case_id,
        "arm_id": identity.arm_id,
        "current_snapshot_id": identity.snapshot_id,
        "lineage_id": identity.lineage_id,
        "expected_previous_state_id": identity.previous_state_id,
        "registered_snapshot_fingerprint": (
            identity.registered_snapshot_fingerprint
        ),
    }

    result = assess_state_integrity(observed, expectation)
    result["adapter_version"] = PRO_BETA_STATE_INTEGRITY_ADAPTER_VERSION
    result["adapter_boundary"] = PRO_BETA_STATE_INTEGRITY_BOUNDARY
    result["expectation_source"] = PERSISTED_IDENTITY_SOURCE
    result["identity_adapter_version"] = identity.adapter_version
    result["read_only"] = True
    result["identity_receipt"] = {
        key: value
        for key, value in asdict(identity).items()
        if key
        in {
            "snapshot_id",
            "conversation_id",
            "case_id",
            "arm_id",
            "state_id",
            "lineage_id",
            "previous_state_id",
            "registered_snapshot_fingerprint",
            "adapter_version",
        }
    }
    return result
