from __future__ import annotations

import unittest

from control_stack.execution_gate import execute_with_gate
from pro_beta.auth_boundary import AuthContext
from pro_beta.contracts import (
    Conversation,
    UserAccount,
    Workspace,
    new_id,
)
from pro_beta.persistence import InMemoryPersistence, OwnershipError
from pro_beta.service import (
    EXECUTION_GATE_REGISTRY_ADAPTER_VERSION,
    ProBetaService,
)


class ExecutionGateRegistryTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryPersistence()
        self.user_a = UserAccount(new_id("usr"), "auth|exec-a", "a@example.com")
        self.user_b = UserAccount(new_id("usr"), "auth|exec-b", "b@example.com")
        self.store.create_user(self.user_a)
        self.store.create_user(self.user_b)

        self.workspace_a = Workspace(new_id("ws"), self.user_a.user_id, "A")
        self.workspace_b = Workspace(new_id("ws"), self.user_b.user_id, "B")
        self.store.create_workspace(self.user_a.user_id, self.workspace_a)
        self.store.create_workspace(self.user_b.user_id, self.workspace_b)

        self.conversation_a = Conversation(
            new_id("conv"), self.workspace_a.workspace_id, "A"
        )
        self.conversation_b = Conversation(
            new_id("conv"), self.workspace_b.workspace_id, "B"
        )
        self.store.create_conversation(self.user_a.user_id, self.conversation_a)
        self.store.create_conversation(self.user_b.user_id, self.conversation_b)

        self.auth_a = AuthContext(
            user_id=self.user_a.user_id,
            external_auth_subject=self.user_a.external_auth_subject,
            issuer="test",
            audience="test",
        )
        self.auth_b = AuthContext(
            user_id=self.user_b.user_id,
            external_auth_subject=self.user_b.external_auth_subject,
            issuer="test",
            audience="test",
        )
        self.service = ProBetaService(self.store)

    def _snapshot_and_run(self):
        snapshot = self.service.save_hawm_snapshot(
            self.auth_a,
            self.conversation_a.conversation_id,
            {"goal": "execution-preflight", "value": 1},
            "USER_WORKING_STATE",
        )
        run = self.service.save_cfc_run(
            self.auth_a,
            self.conversation_a.conversation_id,
            case_id="EXECUTION_BINDING_ONLY",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"decision": "STOP"},
            hawm_snapshot_id=snapshot.snapshot_id,
        )
        return snapshot, run

    def _intent(self, *, idempotency_key="idem-1", receipt_id="receipt-1"):
        snapshot, run = self._snapshot_and_run()
        intent = self.service.register_execution_intent(
            self.auth_a,
            self.conversation_a.conversation_id,
            action_id="action-1",
            controller_run_id=run.run_id,
            action_payload={"operation": "synthetic-demo"},
            idempotency_key=idempotency_key,
            receipt_id=receipt_id,
        )
        return snapshot, run, intent

    def test_intent_binds_run_state_version_and_receipt(self):
        snapshot, run, intent = self._intent()
        identity = self.service.get_hawm_snapshot_identity(
            self.auth_a,
            self.conversation_a.conversation_id,
            snapshot.snapshot_id,
        )

        self.assertEqual(intent.controller_run_id, run.run_id)
        self.assertEqual(intent.state_id, snapshot.snapshot_id)
        self.assertEqual(
            intent.state_version,
            identity.registered_snapshot_fingerprint,
        )
        self.assertEqual(intent.receipt_id, "receipt-1")
        self.assertEqual(
            intent.adapter_version,
            EXECUTION_GATE_REGISTRY_ADAPTER_VERSION,
        )
        self.assertEqual(len(intent.action_payload_fingerprint), 64)

    def test_unbound_cfc_run_cannot_create_intent(self):
        self.service.save_hawm_snapshot(
            self.auth_a,
            self.conversation_a.conversation_id,
            {"goal": "state"},
            "USER_WORKING_STATE",
        )
        run = self.service.save_cfc_run(
            self.auth_a,
            self.conversation_a.conversation_id,
            case_id="UNBOUND",
            controller_anchor="0.2.90rc1",
            controller_result={},
            presentation={"decision": "STOP"},
            hawm_snapshot_id=None,
        )

        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_INTENT_REQUIRES_BOUND_CFC_RUN",
        ):
            self.service.register_execution_intent(
                self.auth_a,
                self.conversation_a.conversation_id,
                action_id="action-1",
                controller_run_id=run.run_id,
                action_payload={},
                idempotency_key="idem-1",
            )

    def test_duplicate_idempotency_key_is_rejected(self):
        _, run, _ = self._intent()

        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_IDEMPOTENCY_KEY_ALREADY_REGISTERED",
        ):
            self.service.register_execution_intent(
                self.auth_a,
                self.conversation_a.conversation_id,
                action_id="action-2",
                controller_run_id=run.run_id,
                action_payload={"operation": "other"},
                idempotency_key="idem-1",
                receipt_id="receipt-2",
            )

    def test_duplicate_receipt_identity_is_rejected(self):
        _, run, _ = self._intent()

        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_RECEIPT_ID_ALREADY_REGISTERED",
        ):
            self.service.register_execution_intent(
                self.auth_a,
                self.conversation_a.conversation_id,
                action_id="action-2",
                controller_run_id=run.run_id,
                action_payload={"operation": "other"},
                idempotency_key="idem-2",
                receipt_id="receipt-1",
            )

    def test_cross_user_registry_read_is_forbidden(self):
        _, _, intent = self._intent()

        with self.assertRaises(OwnershipError):
            self.service.get_execution_intent(
                self.auth_b,
                self.conversation_a.conversation_id,
                intent.intent_id,
            )

    def test_blocked_preflight_cannot_be_recorded_as_execution_receipt(self):
        snapshot, _, intent = self._intent()
        result = execute_with_gate(
            executor=lambda payload: {
                "outcome": "EXECUTED",
                "effect_handle": "must-not-run",
            },
            action_id=intent.action_id,
            controller_run_id=intent.controller_run_id,
            controller_decision="STOP",
            controller_blockers=[],
            controller_state_id=intent.state_id,
            current_state_id=snapshot.snapshot_id,
            controller_state_version=intent.state_version,
            current_state_version=intent.state_version,
            cfc_authority_state="NOT_ESTABLISHED",
            current_authority_state="NOT_ESTABLISHED",
            idempotency_key=intent.idempotency_key,
            receipt_id=intent.receipt_id,
            prior_execution_receipts=[],
        )

        self.assertFalse(result["execution"]["attempted"])
        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_RECEIPT_REQUIRES_ATTEMPT",
        ):
            self.service.record_execution_receipt(
                self.auth_a,
                self.conversation_a.conversation_id,
                intent.intent_id,
                gate_result=result,
            )

    def test_actual_attempt_result_round_trips_as_append_only_receipt(self):
        snapshot, _, intent = self._intent()
        result = execute_with_gate(
            executor=lambda payload: {
                "outcome": "UNKNOWN",
                "effect_handle": "provider-request-1",
            },
            action_id=intent.action_id,
            controller_run_id=intent.controller_run_id,
            controller_decision="CONTINUE",
            controller_blockers=[],
            controller_state_id=intent.state_id,
            current_state_id=snapshot.snapshot_id,
            controller_state_version=intent.state_version,
            current_state_version=intent.state_version,
            cfc_authority_state="ESTABLISHED",
            current_authority_state="ESTABLISHED",
            idempotency_key=intent.idempotency_key,
            receipt_id=intent.receipt_id,
            prior_execution_receipts=[],
        )

        receipt = self.service.record_execution_receipt(
            self.auth_a,
            self.conversation_a.conversation_id,
            intent.intent_id,
            gate_result=result,
        )

        self.assertEqual(receipt.receipt_id, intent.receipt_id)
        self.assertEqual(receipt.execution_status, "OUTCOME_UNKNOWN")
        self.assertTrue(receipt.attempted)
        self.assertIsNone(receipt.executed)
        self.assertEqual(receipt.effect_handle, "provider-request-1")

        rows = self.service.list_execution_receipts(
            self.auth_a,
            self.conversation_a.conversation_id,
        )
        self.assertEqual([row.receipt_id for row in rows], [intent.receipt_id])

        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_INTENT_RECEIPT_ALREADY_EXISTS",
        ):
            self.service.record_execution_receipt(
                self.auth_a,
                self.conversation_a.conversation_id,
                intent.intent_id,
                gate_result=result,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
