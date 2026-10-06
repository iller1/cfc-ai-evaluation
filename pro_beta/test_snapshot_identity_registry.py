from __future__ import annotations

import unittest

from control_stack.state_integrity import (
    STATE_INVALID,
    assess_state_integrity,
    state_fingerprint,
)
from pro_beta.auth_boundary import AuthContext
from pro_beta.contracts import (
    Conversation,
    HAWMSnapshot,
    UserAccount,
    Workspace,
    new_id,
)
from pro_beta.persistence import InMemoryPersistence, NotFoundError, OwnershipError
from pro_beta.service import (
    HAWM_STATE_IDENTITY_ADAPTER_VERSION,
    HAWM_STATE_IDENTITY_ARM_ID,
    HAWM_STATE_IDENTITY_CASE_ID,
    ProBetaService,
)


class HAWMSnapshotIdentityRegistryTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryPersistence()
        self.user_a = UserAccount(new_id("usr"), "auth|identity-a", "a@example.com")
        self.user_b = UserAccount(new_id("usr"), "auth|identity-b", "b@example.com")
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

    def test_save_creates_exact_identity_anchor(self):
        state = {"goal": "inspect", "cfc_structured": {"scope": "EXPECTED"}}
        snapshot = self.service.save_hawm_snapshot(
            self.auth_a,
            self.conversation_a.conversation_id,
            state,
            "USER_WORKING_STATE",
        )
        identity = self.service.get_hawm_snapshot_identity(
            self.auth_a,
            self.conversation_a.conversation_id,
            snapshot.snapshot_id,
        )
        self.assertEqual(identity.snapshot_id, snapshot.snapshot_id)
        self.assertEqual(identity.state_id, snapshot.snapshot_id)
        self.assertEqual(identity.lineage_id, self.conversation_a.conversation_id)
        self.assertIsNone(identity.previous_state_id)
        self.assertEqual(identity.case_id, HAWM_STATE_IDENTITY_CASE_ID)
        self.assertEqual(identity.arm_id, HAWM_STATE_IDENTITY_ARM_ID)
        self.assertEqual(identity.adapter_version, HAWM_STATE_IDENTITY_ADAPTER_VERSION)
        self.assertEqual(
            identity.registered_snapshot_fingerprint,
            state_fingerprint(state),
        )

    def test_second_snapshot_records_exact_predecessor(self):
        first = self.service.save_hawm_snapshot(
            self.auth_a,
            self.conversation_a.conversation_id,
            {"goal": "first"},
            "USER_WORKING_STATE",
        )
        second = self.service.save_hawm_snapshot(
            self.auth_a,
            self.conversation_a.conversation_id,
            {"goal": "second"},
            "USER_WORKING_STATE",
        )
        identity = self.service.get_hawm_snapshot_identity(
            self.auth_a,
            self.conversation_a.conversation_id,
            second.snapshot_id,
        )
        self.assertEqual(identity.previous_state_id, first.snapshot_id)

    def test_legacy_snapshot_is_not_backfilled(self):
        legacy = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=self.conversation_a.conversation_id,
            state={"goal": "legacy"},
            last_verified_state="USER_WORKING_STATE",
        )
        self.store.add_hawm_snapshot(self.user_a.user_id, legacy)
        with self.assertRaises(NotFoundError):
            self.service.get_hawm_snapshot_identity(
                self.auth_a,
                self.conversation_a.conversation_id,
                legacy.snapshot_id,
            )

    def test_same_snapshot_id_changed_payload_fails_closed(self):
        snapshot = self.service.save_hawm_snapshot(
            self.auth_a,
            self.conversation_a.conversation_id,
            {"goal": "original", "value": 1},
            "USER_WORKING_STATE",
        )
        identity = self.service.get_hawm_snapshot_identity(
            self.auth_a,
            self.conversation_a.conversation_id,
            snapshot.snapshot_id,
        )
        observed = {
            "case_id": identity.case_id,
            "arm_id": identity.arm_id,
            "state_id": identity.state_id,
            "snapshot_id": identity.snapshot_id,
            "lineage_id": identity.lineage_id,
            "previous_state_id": identity.previous_state_id,
            "state_payload": {"goal": "tampered", "value": 2},
        }
        expectation = {
            "case_id": identity.case_id,
            "arm_id": identity.arm_id,
            "current_snapshot_id": identity.snapshot_id,
            "lineage_id": identity.lineage_id,
            "expected_previous_state_id": identity.previous_state_id,
            "registered_snapshot_fingerprint": identity.registered_snapshot_fingerprint,
        }
        result = assess_state_integrity(observed, expectation)
        self.assertEqual(result["status"], STATE_INVALID)
        self.assertEqual(result["reason"], "SNAPSHOT_FINGERPRINT_MISMATCH")
        self.assertEqual(
            result["propagation_effect"],
            "BLOCK_STATE_CARRY_FORWARD_STATE_INTEGRITY_REQUIRED",
        )
        self.assertEqual(result["authorization_effect"], "DOES_NOT_AUTHORIZE_CLOSURE")

    def test_identity_read_is_conversation_scoped(self):
        snapshot = self.service.save_hawm_snapshot(
            self.auth_a,
            self.conversation_a.conversation_id,
            {"goal": "owned"},
            "USER_WORKING_STATE",
        )
        with self.assertRaises(OwnershipError):
            self.service.get_hawm_snapshot_identity(
                self.auth_b,
                self.conversation_a.conversation_id,
                snapshot.snapshot_id,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
