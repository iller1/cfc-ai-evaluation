from __future__ import annotations

import unittest

from pro_beta.contracts import (
    ExecutionIntentRegistration,
    ExecutionReceiptRecord,
)
from pro_beta.execution_gate_preflight import (
    REAL_EXECUTION_AUTHORITY_STATUS,
    assess_persisted_execution_preflight,
)


def state_integrity(
    *,
    status="STATE_VALID",
    snapshot_id="state-1",
    state_id="state-1",
    fingerprint="a" * 64,
):
    return {
        "status": status,
        "snapshot_id": snapshot_id,
        "state_id": state_id,
        "state_fingerprint": fingerprint,
        "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
    }


def intent(
    *,
    state_id="state-1",
    state_version="a" * 64,
    idempotency_key="idem-1",
    receipt_id="receipt-1",
    human_review_required=False,
    transaction_required=False,
):
    return ExecutionIntentRegistration(
        intent_id="intent-1",
        conversation_id="conv-1",
        action_id="action-1",
        controller_run_id="run-1",
        state_id=state_id,
        state_version=state_version,
        idempotency_key=idempotency_key,
        receipt_id=receipt_id,
        action_payload_fingerprint="b" * 64,
        human_review_required=human_review_required,
        transaction_required=transaction_required,
        adapter_version="EXECUTION_GATE_REGISTRY_ADAPTER_V0_1",
    )


def receipt(
    *,
    action_id="action-1",
    idempotency_key="idem-old",
    receipt_id="receipt-old",
):
    return ExecutionReceiptRecord(
        receipt_id=receipt_id,
        intent_id="intent-old",
        conversation_id="conv-1",
        action_id=action_id,
        controller_run_id="run-old",
        state_id="state-old",
        state_version="c" * 64,
        idempotency_key=idempotency_key,
        execution_status="OUTCOME_UNKNOWN",
        attempted=True,
        executed=None,
        effect_handle="provider-request-1",
        adapter_version="EXECUTION_GATE_REGISTRY_ADAPTER_V0_1",
    )


class ExecutionGatePreflightTests(unittest.TestCase):
    def test_exact_intent_still_blocks_without_real_authority(self):
        result = assess_persisted_execution_preflight(
            current_state_id="state-1",
            current_state_version="a" * 64,
            state_integrity_result=state_integrity(),
            intent=intent(),
            prior_receipts=[],
        )

        self.assertEqual(result["preflight_status"], "PREFLIGHT_BLOCKED")
        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertEqual(
            result["authority_status"],
            REAL_EXECUTION_AUTHORITY_STATUS,
        )
        self.assertEqual(result["controller_decision"], "NOT_RUN")
        self.assertIn(
            "CONTROLLER_DECISION_NOT_CONTINUE",
            result["blockers"],
        )
        self.assertIn(
            "CFC_AUTHORITY_NOT_ESTABLISHED",
            result["blockers"],
        )
        self.assertIn(
            "CURRENT_AUTHORITY_NOT_ESTABLISHED",
            result["blockers"],
        )
        self.assertFalse(result["execution"]["attempted"])
        self.assertFalse(result["execution"]["executed"])
        self.assertTrue(result["read_only"])
        self.assertEqual(result["persistence_actions"], [])
        self.assertFalse(result["cfc_executed"])
        self.assertEqual(
            result["authority_effect"],
            "DOES_NOT_CREATE_AUTHORITY",
        )

    def test_stale_intent_state_is_explicit_additional_blocker(self):
        result = assess_persisted_execution_preflight(
            current_state_id="state-2",
            current_state_version="d" * 64,
            state_integrity_result=state_integrity(
                snapshot_id="state-2",
                state_id="state-2",
                fingerprint="d" * 64,
            ),
            intent=intent(),
            prior_receipts=[],
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertIn(
            "PRE_EXECUTION_STATE_ID_MISMATCH",
            result["blockers"],
        )
        self.assertIn(
            "PRE_EXECUTION_STATE_VERSION_MISMATCH",
            result["blockers"],
        )

    def test_state_integrity_must_be_valid(self):
        result = assess_persisted_execution_preflight(
            current_state_id="state-1",
            current_state_version="a" * 64,
            state_integrity_result=state_integrity(status="STATE_INVALID"),
            intent=intent(),
            prior_receipts=[],
        )

        self.assertEqual(
            result["preflight_status"],
            "PREFLIGHT_UNRESOLVED",
        )
        self.assertEqual(result["reason"], "STATE_INTEGRITY_NOT_VALID")
        self.assertFalse(result["execution"]["attempted"])

    def test_state_integrity_fingerprint_must_match_current_version(self):
        result = assess_persisted_execution_preflight(
            current_state_id="state-1",
            current_state_version="a" * 64,
            state_integrity_result=state_integrity(
                fingerprint="e" * 64,
            ),
            intent=intent(),
            prior_receipts=[],
        )

        self.assertEqual(
            result["reason"],
            "STATE_INTEGRITY_RESULT_BINDING_MISMATCH",
        )

    def test_prior_receipt_replay_is_preserved_as_blocker(self):
        result = assess_persisted_execution_preflight(
            current_state_id="state-1",
            current_state_version="a" * 64,
            state_integrity_result=state_integrity(),
            intent=intent(idempotency_key="idem-old"),
            prior_receipts=[
                receipt(idempotency_key="idem-old")
            ],
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertIn(
            "IDEMPOTENCY_REPLAY_BLOCKED",
            result["blockers"],
        )
        self.assertEqual(result["prior_execution_receipt_count"], 1)

    def test_receipt_identity_reuse_is_preserved_as_blocker(self):
        result = assess_persisted_execution_preflight(
            current_state_id="state-1",
            current_state_version="a" * 64,
            state_integrity_result=state_integrity(),
            intent=intent(receipt_id="receipt-old"),
            prior_receipts=[
                receipt(receipt_id="receipt-old")
            ],
        )

        self.assertIn(
            "EXECUTION_RECEIPT_ID_REUSED",
            result["blockers"],
        )

    def test_human_review_and_transaction_requirements_do_not_disappear(self):
        result = assess_persisted_execution_preflight(
            current_state_id="state-1",
            current_state_version="a" * 64,
            state_integrity_result=state_integrity(),
            intent=intent(
                human_review_required=True,
                transaction_required=True,
            ),
            prior_receipts=[],
        )

        self.assertIn("HUMAN_REVIEW_REQUIRED", result["blockers"])
        self.assertIn(
            "TRANSACTION_BOUNDARY_UNAVAILABLE",
            result["blockers"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
