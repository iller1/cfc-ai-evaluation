from __future__ import annotations

from dataclasses import asdict
import copy
import unittest

from pro_beta.auth_boundary import AuthContext
from pro_beta.contracts import Conversation, UserAccount, Workspace, new_id
from pro_beta.persistence import InMemoryPersistence
from pro_beta.service import ProBetaService
from pro_beta.state_integrity_acceptance import (
    STATE_INTEGRITY_ACCEPTANCE_BOUNDARY,
    run_state_integrity_adversarial_acceptance,
)


class StateIntegrityAdversarialAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryPersistence()
        self.user = UserAccount(new_id("usr"), "auth|si-accept", "a@example.com")
        self.store.create_user(self.user)
        self.workspace = Workspace(new_id("ws"), self.user.user_id, "SI")
        self.store.create_workspace(self.user.user_id, self.workspace)
        self.conversation = Conversation(
            new_id("conv"), self.workspace.workspace_id, "SI acceptance"
        )
        self.store.create_conversation(self.user.user_id, self.conversation)
        self.auth = AuthContext(
            user_id=self.user.user_id,
            external_auth_subject=self.user.external_auth_subject,
            issuer="test",
            audience="test",
        )
        self.service = ProBetaService(self.store)

    def test_all_server_derived_adversarial_variants_fail_closed(self):
        first = self.service.save_hawm_snapshot(
            self.auth,
            self.conversation.conversation_id,
            {"goal": "first"},
            "USER_WORKING_STATE",
        )
        second = self.service.save_hawm_snapshot(
            self.auth,
            self.conversation.conversation_id,
            {"goal": "second", "cfc_structured": {"scope": "EXPECTED"}},
            "USER_WORKING_STATE",
        )
        snapshots = self.service.list_hawm_snapshots(
            self.auth, self.conversation.conversation_id
        )
        identity = self.service.get_hawm_snapshot_identity(
            self.auth,
            self.conversation.conversation_id,
            second.snapshot_id,
        )
        before_snapshot = copy.deepcopy(asdict(snapshots[-1]))
        before_identity = copy.deepcopy(asdict(identity))

        result = run_state_integrity_adversarial_acceptance(
            current=snapshots[-1],
            previous=snapshots[-2],
            identity=identity,
        )

        self.assertEqual(result["status"], "ACCEPTANCE_PASS")
        self.assertEqual(result["baseline_status"], "STATE_VALID")
        self.assertTrue(result["read_only"])
        self.assertEqual(result["persistence_actions"], [])
        self.assertFalse(result["cfc_executed"])
        self.assertEqual(
            result["authorization_effect"],
            "DOES_NOT_AUTHORIZE_CLOSURE",
        )
        self.assertEqual(result["boundary"], STATE_INTEGRITY_ACCEPTANCE_BOUNDARY)

        expected = {
            "CROSS_CASE_SUBSTITUTION": ("STATE_INVALID", "CASE_ID_MISMATCH"),
            "CROSS_ARM_SUBSTITUTION": ("STATE_INVALID", "ARM_ID_MISMATCH"),
            "LINEAGE_SUBSTITUTION": ("STATE_INVALID", "LINEAGE_ID_MISMATCH"),
            "STALE_SNAPSHOT": ("STATE_UNRESOLVED", "CURRENT_SNAPSHOT_MISMATCH"),
            "SAME_SNAPSHOT_CHANGED_PAYLOAD": (
                "STATE_INVALID",
                "SNAPSHOT_FINGERPRINT_MISMATCH",
            ),
            "PREDECESSOR_MISMATCH": (
                "STATE_UNRESOLVED",
                "PREDECESSOR_MISMATCH",
            ),
        }
        self.assertEqual({item["case"] for item in result["cases"]}, set(expected))
        for item in result["cases"]:
            self.assertTrue(item["pass"])
            self.assertEqual(
                (item["status"], item["reason"]),
                expected[item["case"]],
            )
            self.assertEqual(
                item["authorization_effect"],
                "DOES_NOT_AUTHORIZE_CLOSURE",
            )

        current_after = self.service.latest_hawm_snapshot(
            self.auth, self.conversation.conversation_id
        )
        identity_after = self.service.get_hawm_snapshot_identity(
            self.auth,
            self.conversation.conversation_id,
            second.snapshot_id,
        )
        self.assertEqual(asdict(current_after), before_snapshot)
        self.assertEqual(asdict(identity_after), before_identity)
        self.assertEqual(first.snapshot_id, snapshots[-2].snapshot_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
