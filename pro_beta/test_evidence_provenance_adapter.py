from __future__ import annotations

from dataclasses import replace
import unittest

from pro_beta.contracts import (
    EvidenceDependencyReceipt,
    EvidenceProvenanceReceipt,
    EvidenceSetRegistration,
    HAWMSnapshot,
    HAWMSnapshotIdentity,
)
from pro_beta.evidence_provenance_adapter import (
    PRO_BETA_EVIDENCE_PROVENANCE_ADAPTER_VERSION,
    assess_persisted_evidence_provenance,
)
from pro_beta.service import (
    EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION,
    HAWM_STATE_IDENTITY_ADAPTER_VERSION,
)


def current_snapshot():
    return HAWMSnapshot(
        snapshot_id="hawm-current",
        conversation_id="conv-1",
        state={"goal": "evidence"},
        last_verified_state="USER_WORKING_STATE",
    )


def identity():
    return HAWMSnapshotIdentity(
        snapshot_id="hawm-current",
        conversation_id="conv-1",
        case_id="HAWM_PRO_BETA_STATE",
        arm_id="HAWM_WORKING_STATE",
        state_id="hawm-current",
        lineage_id="conv-1",
        previous_state_id="hawm-prev",
        registered_snapshot_fingerprint="a" * 64,
        adapter_version=HAWM_STATE_IDENTITY_ADAPTER_VERSION,
    )


def registration():
    return EvidenceSetRegistration(
        registration_id="evidence-set-1",
        snapshot_id="hawm-current",
        conversation_id="conv-1",
        state_id="hawm-current",
        evidence_set=[
            {
                "evidence_id": "E1",
                "source_id": "S1",
                "validity": "CURRENT",
                "scope_status": "MATCH",
                "failure_domain_id": "FD1",
            },
            {
                "evidence_id": "E2",
                "source_id": "S2",
                "validity": "CURRENT",
                "scope_status": "MATCH",
                "failure_domain_id": "FD2",
            },
        ],
        missing_evidence=[],
        adapter_version=EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION,
    )


def provenance_receipts():
    return [
        EvidenceProvenanceReceipt(
            receipt_id="prov-1",
            snapshot_id="hawm-current",
            conversation_id="conv-1",
            state_id="hawm-current",
            evidence_id="E1",
            source_id="S1",
            status="ESTABLISHED",
            adapter_version=EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION,
        ),
        EvidenceProvenanceReceipt(
            receipt_id="prov-2",
            snapshot_id="hawm-current",
            conversation_id="conv-1",
            state_id="hawm-current",
            evidence_id="E2",
            source_id="S2",
            status="ESTABLISHED",
            adapter_version=EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION,
        ),
    ]


def dependency_receipt():
    return EvidenceDependencyReceipt(
        receipt_id="dep-1",
        snapshot_id="hawm-current",
        conversation_id="conv-1",
        state_id="hawm-current",
        evidence_ids=["E1", "E2"],
        failure_domains={"E1": "FD1", "E2": "FD2"},
        status="RESOLVED",
        adapter_version=EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION,
    )


def drift(status="NO_DRIFT", current_id="hawm-current"):
    return {
        "status": status,
        "current_snapshot_id": current_id,
    }


class EvidenceProvenanceAdapterTests(unittest.TestCase):
    def test_exact_persisted_state_is_applicable(self):
        result = assess_persisted_evidence_provenance(
            current=current_snapshot(),
            identity=identity(),
            registration=registration(),
            provenance_receipts=provenance_receipts(),
            dependency_receipt=dependency_receipt(),
            drift_result=drift(),
        )

        self.assertEqual(result["status"], "EVIDENCE_APPLICABLE")
        self.assertEqual(
            result["reason"],
            "EXPLICIT_EVIDENCE_PROVENANCE_STATE_APPLICABLE",
        )
        self.assertEqual(
            result["adapter_version"],
            PRO_BETA_EVIDENCE_PROVENANCE_ADAPTER_VERSION,
        )
        self.assertTrue(result["read_only"])
        self.assertEqual(
            result["authorization_effect"],
            "DOES_NOT_AUTHORIZE_CLOSURE",
        )

    def test_missing_dependency_receipt_remains_unknown(self):
        result = assess_persisted_evidence_provenance(
            current=current_snapshot(),
            identity=identity(),
            registration=registration(),
            provenance_receipts=provenance_receipts(),
            dependency_receipt=None,
            drift_result=drift(),
        )

        self.assertEqual(result["status"], "EVIDENCE_UNKNOWN")
        self.assertEqual(
            result["evidence"]["dependency_state"],
            "UNKNOWN",
        )

    def test_wrong_registration_binding_is_invalid(self):
        wrong = replace(registration(), state_id="hawm-other")

        result = assess_persisted_evidence_provenance(
            current=current_snapshot(),
            identity=identity(),
            registration=wrong,
            provenance_receipts=provenance_receipts(),
            dependency_receipt=dependency_receipt(),
            drift_result=drift(),
        )

        self.assertEqual(result["status"], "EVIDENCE_INVALID")
        self.assertEqual(
            result["reason"],
            "EVIDENCE_REGISTRATION_BINDING_MISMATCH",
        )

    def test_provenance_receipt_from_other_state_is_invalid(self):
        receipts = provenance_receipts()
        receipts[0] = replace(
            receipts[0],
            snapshot_id="hawm-other",
            state_id="hawm-other",
        )

        result = assess_persisted_evidence_provenance(
            current=current_snapshot(),
            identity=identity(),
            registration=registration(),
            provenance_receipts=receipts,
            dependency_receipt=dependency_receipt(),
            drift_result=drift(),
        )

        self.assertEqual(result["status"], "EVIDENCE_INVALID")
        self.assertEqual(
            result["reason"],
            "EVIDENCE_PROVENANCE_RECEIPT_BINDING_MISMATCH",
        )

    def test_dependency_receipt_from_other_state_is_invalid(self):
        receipt = replace(
            dependency_receipt(),
            snapshot_id="hawm-other",
            state_id="hawm-other",
        )

        result = assess_persisted_evidence_provenance(
            current=current_snapshot(),
            identity=identity(),
            registration=registration(),
            provenance_receipts=provenance_receipts(),
            dependency_receipt=receipt,
            drift_result=drift(),
        )

        self.assertEqual(result["status"], "EVIDENCE_INVALID")
        self.assertEqual(
            result["reason"],
            "EVIDENCE_DEPENDENCY_RECEIPT_BINDING_MISMATCH",
        )

    def test_drift_for_other_snapshot_is_invalid(self):
        result = assess_persisted_evidence_provenance(
            current=current_snapshot(),
            identity=identity(),
            registration=registration(),
            provenance_receipts=provenance_receipts(),
            dependency_receipt=dependency_receipt(),
            drift_result=drift(current_id="hawm-other"),
        )

        self.assertEqual(result["status"], "EVIDENCE_INVALID")
        self.assertEqual(
            result["reason"],
            "EVIDENCE_DRIFT_CURRENT_SNAPSHOT_MISMATCH",
        )

    def test_material_drift_is_partial_and_blocks(self):
        result = assess_persisted_evidence_provenance(
            current=current_snapshot(),
            identity=identity(),
            registration=registration(),
            provenance_receipts=provenance_receipts(),
            dependency_receipt=dependency_receipt(),
            drift_result=drift(status="MATERIAL_DRIFT"),
        )

        self.assertEqual(result["status"], "EVIDENCE_PARTIAL")
        self.assertTrue(result["requires_review"])
        self.assertIn("DRIFT_NOT_CLEAR", result["diagnostics"])

    def test_unsupported_registry_version_is_unresolved(self):
        wrong = replace(registration(), adapter_version="OLD")

        result = assess_persisted_evidence_provenance(
            current=current_snapshot(),
            identity=identity(),
            registration=wrong,
            provenance_receipts=provenance_receipts(),
            dependency_receipt=dependency_receipt(),
            drift_result=drift(),
        )

        self.assertEqual(result["status"], "EVIDENCE_UNKNOWN")
        self.assertEqual(
            result["reason"],
            "EVIDENCE_REGISTRY_ADAPTER_VERSION_UNSUPPORTED",
        )

    def test_identity_mismatch_is_invalid(self):
        wrong_identity = replace(identity(), state_id="hawm-other")

        result = assess_persisted_evidence_provenance(
            current=current_snapshot(),
            identity=wrong_identity,
            registration=registration(),
            provenance_receipts=provenance_receipts(),
            dependency_receipt=dependency_receipt(),
            drift_result=drift(),
        )

        self.assertEqual(result["status"], "EVIDENCE_INVALID")
        self.assertEqual(
            result["reason"],
            "STATE_IDENTITY_BINDING_MISMATCH",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
