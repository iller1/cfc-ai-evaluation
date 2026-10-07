from __future__ import annotations

from dataclasses import asdict
from typing import Any

from control_stack.evidence_provenance import (
    BLOCK_EVIDENCE,
    EVIDENCE_INVALID,
    EVIDENCE_PROVENANCE_BOUNDARY,
    EVIDENCE_PROVENANCE_VERSION,
    EVIDENCE_UNKNOWN,
    assess_evidence_provenance,
)
from pro_beta.contracts import (
    EvidenceDependencyReceipt,
    EvidenceProvenanceReceipt,
    EvidenceSetRegistration,
    HAWMSnapshot,
    HAWMSnapshotIdentity,
)
from pro_beta.service import (
    EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION,
    HAWM_STATE_IDENTITY_ADAPTER_VERSION,
)


PRO_BETA_EVIDENCE_PROVENANCE_ADAPTER_VERSION = (
    "PRO_BETA_EVIDENCE_PROVENANCE_ADAPTER_V0_1"
)
PRO_BETA_EVIDENCE_PROVENANCE_BOUNDARY = (
    "PERSISTED_STATE_BOUND_EVIDENCE_REGISTRY_AND_DRIFT_ONLY"
)
PERSISTED_EVIDENCE_SOURCE = "PERSISTED_EVIDENCE_PROVENANCE_REGISTRY"
PERSISTED_DRIFT_SOURCE = "PERSISTED_CFC_RUN_BOUND_EVIDENCE_DRIFT"


def unresolved_evidence_provenance(
    reason: str,
    *,
    current_snapshot_id: str | None = None,
) -> dict[str, Any]:
    return {
        "adapter_version": PRO_BETA_EVIDENCE_PROVENANCE_ADAPTER_VERSION,
        "version": EVIDENCE_PROVENANCE_VERSION,
        "status": EVIDENCE_UNKNOWN,
        "reason": reason,
        "state_id": current_snapshot_id,
        "evidence": {
            "status": EVIDENCE_UNKNOWN,
            "provenance_state": "UNKNOWN",
            "applicability_state": "UNKNOWN",
            "dependency_state": "UNKNOWN",
            "evidence_set": [],
            "missing_evidence": [],
            "drift_state": "UNRESOLVED",
        },
        "diagnostics": [reason],
        "provenance_receipt_ids": [],
        "dependency_receipt_id": None,
        "requires_review": True,
        "propagation_effect": BLOCK_EVIDENCE,
        "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
        "boundary": EVIDENCE_PROVENANCE_BOUNDARY,
        "adapter_boundary": PRO_BETA_EVIDENCE_PROVENANCE_BOUNDARY,
        "registry_source": "NONE",
        "drift_source": "NONE",
        "registration_id": None,
        "read_only": True,
    }


def _adapter_invalid(
    reason: str,
    *,
    current_snapshot_id: str,
    registration: EvidenceSetRegistration | None,
) -> dict[str, Any]:
    evidence_set = (
        registration.evidence_set if registration is not None else []
    )
    missing_evidence = (
        registration.missing_evidence if registration is not None else []
    )
    return {
        "adapter_version": PRO_BETA_EVIDENCE_PROVENANCE_ADAPTER_VERSION,
        "version": EVIDENCE_PROVENANCE_VERSION,
        "status": EVIDENCE_INVALID,
        "reason": reason,
        "state_id": current_snapshot_id,
        "evidence": {
            "status": EVIDENCE_INVALID,
            "provenance_state": "INVALID",
            "applicability_state": "UNKNOWN",
            "dependency_state": "UNKNOWN",
            "evidence_set": evidence_set,
            "missing_evidence": missing_evidence,
            "drift_state": "UNRESOLVED",
        },
        "diagnostics": [reason],
        "provenance_receipt_ids": [],
        "dependency_receipt_id": None,
        "requires_review": True,
        "propagation_effect": BLOCK_EVIDENCE,
        "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
        "boundary": EVIDENCE_PROVENANCE_BOUNDARY,
        "adapter_boundary": PRO_BETA_EVIDENCE_PROVENANCE_BOUNDARY,
        "registry_source": PERSISTED_EVIDENCE_SOURCE,
        "drift_source": "NONE",
        "registration_id": (
            registration.registration_id if registration is not None else None
        ),
        "read_only": True,
    }


def assess_persisted_evidence_provenance(
    *,
    current: HAWMSnapshot,
    identity: HAWMSnapshotIdentity,
    registration: EvidenceSetRegistration,
    provenance_receipts: list[EvidenceProvenanceReceipt],
    dependency_receipt: EvidenceDependencyReceipt | None,
    drift_result: dict[str, Any],
) -> dict[str, Any]:
    """Assess one current snapshot from persisted Layer B registry records.

    This adapter accepts no client-supplied identity, provenance or dependency
    fields. Callers must resolve all records from owned server persistence.
    """

    if identity.adapter_version != HAWM_STATE_IDENTITY_ADAPTER_VERSION:
        return unresolved_evidence_provenance(
            "IDENTITY_ADAPTER_VERSION_UNSUPPORTED",
            current_snapshot_id=current.snapshot_id,
        )

    if (
        identity.snapshot_id != current.snapshot_id
        or identity.conversation_id != current.conversation_id
        or identity.state_id != current.snapshot_id
    ):
        return _adapter_invalid(
            "STATE_IDENTITY_BINDING_MISMATCH",
            current_snapshot_id=current.snapshot_id,
            registration=registration,
        )

    if (
        registration.adapter_version
        != EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION
    ):
        return unresolved_evidence_provenance(
            "EVIDENCE_REGISTRY_ADAPTER_VERSION_UNSUPPORTED",
            current_snapshot_id=current.snapshot_id,
        )

    if (
        registration.snapshot_id != current.snapshot_id
        or registration.conversation_id != current.conversation_id
        or registration.state_id != current.snapshot_id
    ):
        return _adapter_invalid(
            "EVIDENCE_REGISTRATION_BINDING_MISMATCH",
            current_snapshot_id=current.snapshot_id,
            registration=registration,
        )

    for receipt in provenance_receipts:
        if (
            receipt.adapter_version
            != EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION
        ):
            return unresolved_evidence_provenance(
                "EVIDENCE_PROVENANCE_RECEIPT_VERSION_UNSUPPORTED",
                current_snapshot_id=current.snapshot_id,
            )
        if (
            receipt.snapshot_id != current.snapshot_id
            or receipt.conversation_id != current.conversation_id
            or receipt.state_id != current.snapshot_id
        ):
            return _adapter_invalid(
                "EVIDENCE_PROVENANCE_RECEIPT_BINDING_MISMATCH",
                current_snapshot_id=current.snapshot_id,
                registration=registration,
            )

    if dependency_receipt is not None:
        if (
            dependency_receipt.adapter_version
            != EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION
        ):
            return unresolved_evidence_provenance(
                "EVIDENCE_DEPENDENCY_RECEIPT_VERSION_UNSUPPORTED",
                current_snapshot_id=current.snapshot_id,
            )
        if (
            dependency_receipt.snapshot_id != current.snapshot_id
            or dependency_receipt.conversation_id != current.conversation_id
            or dependency_receipt.state_id != current.snapshot_id
        ):
            return _adapter_invalid(
                "EVIDENCE_DEPENDENCY_RECEIPT_BINDING_MISMATCH",
                current_snapshot_id=current.snapshot_id,
                registration=registration,
            )

    drift_status = drift_result.get("status")
    if drift_status not in {
        "NO_DRIFT",
        "MATERIAL_DRIFT",
        "UNRESOLVED",
    }:
        return unresolved_evidence_provenance(
            "EVIDENCE_DRIFT_STATUS_UNSUPPORTED",
            current_snapshot_id=current.snapshot_id,
        )
    if drift_result.get("current_snapshot_id") != current.snapshot_id:
        return _adapter_invalid(
            "EVIDENCE_DRIFT_CURRENT_SNAPSHOT_MISMATCH",
            current_snapshot_id=current.snapshot_id,
            registration=registration,
        )

    provenance_payloads = [
        {
            key: value
            for key, value in asdict(receipt).items()
            if key
            in {
                "receipt_id",
                "state_id",
                "evidence_id",
                "source_id",
                "status",
            }
        }
        for receipt in provenance_receipts
    ]
    dependency_payload = None
    if dependency_receipt is not None:
        dependency_payload = {
            key: value
            for key, value in asdict(dependency_receipt).items()
            if key
            in {
                "receipt_id",
                "state_id",
                "evidence_ids",
                "failure_domains",
                "status",
            }
        }

    result = assess_evidence_provenance(
        state_id=current.snapshot_id,
        evidence_set=registration.evidence_set,
        provenance_receipts=provenance_payloads,
        dependency_receipt=dependency_payload,
        missing_evidence=registration.missing_evidence,
        drift_state=drift_status,
    )
    result["adapter_version"] = PRO_BETA_EVIDENCE_PROVENANCE_ADAPTER_VERSION
    result["adapter_boundary"] = PRO_BETA_EVIDENCE_PROVENANCE_BOUNDARY
    result["registry_source"] = PERSISTED_EVIDENCE_SOURCE
    result["drift_source"] = PERSISTED_DRIFT_SOURCE
    result["registration_id"] = registration.registration_id
    result["read_only"] = True
    return result
