from __future__ import annotations

import copy
import unittest

from control_stack.execution_gate import assess_execution_gate
from pro_beta.auth_boundary import AuthContext
from pro_beta.contracts import (
    Conversation,
    UserAccount,
    Workspace,
    new_id,
)
from pro_beta.persistence import InMemoryPersistence, OwnershipError
from pro_beta.service import (
    EXECUTION_GATE_RECEIPT_ADAPTER_VERSION,
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

    def _snapshot(self, label="execution"):
        snap = self.service.save_hawm_snapshot(
            self.auth_a,
            self.conversation_a.conversation_id,
            {"goal": label},
            "USER_WORKING_STATE",
        )
        identity = self.service.get_hawm_snapshot_identity(
            self.auth_a,
            self.conversation_a.conversation_id,
            snap.snapshot_id,
        )
        return snap, identity

    def _run(self, snapshot_id):
        return self.service.save_cfc_run(
            self.auth_a,
            self.conversation_a.conversation_id,
            case_id="HAWM_STRUCTURED_CUSTOM",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"decision": "STOP"},
            hawm_snapshot_id=snapshot_id,
        )

    def _blocked_gate(
        self,
        *,
        run_id,
        snapshot_id,
        fingerprint,
        receipt_id="exec-receipt-1",
        idempotency_key="idem-1",
    ):
        return assess_execution_gate(
            action_id="PRO_BETA_EXECUTION_PREFLIGHT",
            controller_run_id=run_id,
            controller_decision="HOLD",
            controller_blockers=["SYNTHETIC_CFC_NOT_REAL_ACTION_AUTHORITY"],
            controller_state_id=snapshot_id,
            current_state_id=snapshot_id,
            controller_state_version=fingerprint,
            current_state_version=fingerprint,
            cfc_authority_state="NOT_ESTABLISHED",
            current_authority_state="NOT_ESTABLISHED",
            idempotency_key=idempotency_key,
            receipt_id=receipt_id,
            prior_execution_receipts=[],
            human_review_required=False,
            human_review_approved=False,
            transaction_required=False,
            transaction_supported=False,
        )

    def test_exact_blocked_receipt_round_trip(self):
        snap, identity = self._snapshot()
        run = self._run(snap.snapshot_id)
        gate = self._blocked_gate(
            run_id=run.run_id,
            snapshot_id=snap.snapshot_id,
            fingerprint=identity.registered_snapshot_fingerprint,
        )

        saved = self.service.save_execution_gate_receipt(
            self.auth_a,
            self.conversation_a.conversation_id,
            gate,
        )
        rows = self.service.list_execution_receipts(
            self.auth_a,
            self.conversation_a.conversation_id,
        )

        self.assertEqual(rows, [saved])
        self.assertEqual(saved.controller_run_id, run.run_id)
        self.assertEqual(saved.controller_state_id, snap.snapshot_id)
        self.assertEqual(saved.pre_execution_state_id, snap.snapshot_id)
        self.assertEqual(
            saved.controller_state_version,
            identity.registered_snapshot_fingerprint,
        )
        self.assertFalse(saved.attempted)
        self.assertFalse(saved.executed)
        self.assertEqual(saved.execution_status, "BLOCKED")
        self.assertEqual(
            saved.adapter_version,
            EXECUTION_GATE_RECEIPT_ADAPTER_VERSION,
        )

    def test_unbound_cfc_run_cannot_back_execution_receipt(self):
        snap, identity = self._snapshot()
        run = self.service.save_cfc_run(
            self.auth_a,
            self.conversation_a.conversation_id,
            case_id="PREPARED_SYNTHETIC",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"decision": "STOP"},
            hawm_snapshot_id=None,
        )
        gate = self._blocked_gate(
            run_id=run.run_id,
            snapshot_id=snap.snapshot_id,
            fingerprint=identity.registered_snapshot_fingerprint,
        )

        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_CONTROLLER_RUN_STATE_MISMATCH",
        ):
            self.service.save_execution_gate_receipt(
                self.auth_a,
                self.conversation_a.conversation_id,
                gate,
            )

    def test_cfc_run_bound_to_other_state_is_rejected(self):
        first, first_identity = self._snapshot("first")
        run = self._run(first.snapshot_id)
        second, second_identity = self._snapshot("second")
        gate = self._blocked_gate(
            run_id=run.run_id,
            snapshot_id=second.snapshot_id,
            fingerprint=second_identity.registered_snapshot_fingerprint,
        )

        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_CONTROLLER_RUN_STATE_MISMATCH",
        ):
            self.service.save_execution_gate_receipt(
                self.auth_a,
                self.conversation_a.conversation_id,
                gate,
            )

    def test_wrong_controller_state_version_is_rejected(self):
        snap, identity = self._snapshot()
        run = self._run(snap.snapshot_id)
        gate = self._blocked_gate(
            run_id=run.run_id,
            snapshot_id=snap.snapshot_id,
            fingerprint=identity.registered_snapshot_fingerprint,
        )
        gate["controller_state_version"] = "f" * 64

        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_CONTROLLER_STATE_VERSION_MISMATCH",
        ):
            self.service.save_execution_gate_receipt(
                self.auth_a,
                self.conversation_a.conversation_id,
                gate,
            )

    def test_wrong_pre_execution_state_version_is_rejected(self):
        snap, identity = self._snapshot()
        run = self._run(snap.snapshot_id)
        gate = self._blocked_gate(
            run_id=run.run_id,
            snapshot_id=snap.snapshot_id,
            fingerprint=identity.registered_snapshot_fingerprint,
        )
        gate["current_state_version"] = "e" * 64

        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_PRE_STATE_VERSION_MISMATCH",
        ):
            self.service.save_execution_gate_receipt(
                self.auth_a,
                self.conversation_a.conversation_id,
                gate,
            )

    def test_duplicate_receipt_id_is_rejected(self):
        snap, identity = self._snapshot()
        run = self._run(snap.snapshot_id)
        gate = self._blocked_gate(
            run_id=run.run_id,
            snapshot_id=snap.snapshot_id,
            fingerprint=identity.registered_snapshot_fingerprint,
        )
        self.service.save_execution_gate_receipt(
            self.auth_a,
            self.conversation_a.conversation_id,
            gate,
        )

        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_RECEIPT_ALREADY_EXISTS",
        ):
            self.service.save_execution_gate_receipt(
                self.auth_a,
                self.conversation_a.conversation_id,
                gate,
            )

    def test_duplicate_idempotency_key_is_rejected(self):
        snap, identity = self._snapshot()
        run = self._run(snap.snapshot_id)
        first = self._blocked_gate(
            run_id=run.run_id,
            snapshot_id=snap.snapshot_id,
            fingerprint=identity.registered_snapshot_fingerprint,
            receipt_id="exec-receipt-1",
            idempotency_key="idem-1",
        )
        second = self._blocked_gate(
            run_id=run.run_id,
            snapshot_id=snap.snapshot_id,
            fingerprint=identity.registered_snapshot_fingerprint,
            receipt_id="exec-receipt-2",
            idempotency_key="idem-1",
        )
        self.service.save_execution_gate_receipt(
            self.auth_a,
            self.conversation_a.conversation_id,
            first,
        )

        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_IDEMPOTENCY_KEY_ALREADY_USED",
        ):
            self.service.save_execution_gate_receipt(
                self.auth_a,
                self.conversation_a.conversation_id,
                second,
            )

    def test_malformed_execution_object_is_rejected_before_persistence(self):
        snap, identity = self._snapshot()
        run = self._run(snap.snapshot_id)
        gate = self._blocked_gate(
            run_id=run.run_id,
            snapshot_id=snap.snapshot_id,
            fingerprint=identity.registered_snapshot_fingerprint,
        )
        broken = copy.deepcopy(gate)
        broken["execution"]["execution_status"] = "EXECUTED"
        broken["execution"]["attempted"] = False
        broken["execution"]["executed"] = True
        broken["execution"]["effect_handle"] = "effect-should-not-exist"

        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_GATE_EXECUTION_RECEIPT_INVALID",
        ):
            self.service.save_execution_gate_receipt(
                self.auth_a,
                self.conversation_a.conversation_id,
                broken,
            )
        self.assertEqual(
            self.service.list_execution_receipts(
                self.auth_a,
                self.conversation_a.conversation_id,
            ),
            [],
        )

    def test_registry_reads_are_conversation_owned(self):
        snap, identity = self._snapshot()
        run = self._run(snap.snapshot_id)
        gate = self._blocked_gate(
            run_id=run.run_id,
            snapshot_id=snap.snapshot_id,
            fingerprint=identity.registered_snapshot_fingerprint,
        )
        self.service.save_execution_gate_receipt(
            self.auth_a,
            self.conversation_a.conversation_id,
            gate,
        )

        with self.assertRaises(OwnershipError):
            self.service.list_execution_receipts(
                self.auth_b,
                self.conversation_a.conversation_id,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
