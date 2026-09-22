from __future__ import annotations

import unittest

from pro_beta.auth_boundary import AuthContext
from pro_beta.contracts import UserAccount
from pro_beta.persistence import InMemoryPersistence, OwnershipError
from pro_beta.service import ProBetaService


class ProBetaServiceTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryPersistence()
        self.account_a = UserAccount(
            user_id="usr_a",
            external_auth_subject="provider|a",
            email="a@example.com",
        )
        self.account_b = UserAccount(
            user_id="usr_b",
            external_auth_subject="provider|b",
            email="b@example.com",
        )
        self.store.create_user(self.account_a)
        self.store.create_user(self.account_b)
        self.auth_a = AuthContext(
            user_id=self.account_a.user_id,
            external_auth_subject=self.account_a.external_auth_subject,
            issuer="https://identity.example/",
            audience="cfc-hawm-pro-beta",
        )
        self.auth_b = AuthContext(
            user_id=self.account_b.user_id,
            external_auth_subject=self.account_b.external_auth_subject,
            issuer="https://identity.example/",
            audience="cfc-hawm-pro-beta",
        )
        self.service = ProBetaService(self.store)

    def test_authenticated_user_can_create_workspace_and_conversation(self):
        workspace = self.service.create_workspace(self.auth_a, "Research")
        conversation = self.service.create_conversation(
            self.auth_a, workspace.workspace_id, "Question 1"
        )
        self.assertEqual(workspace.user_id, self.account_a.user_id)
        self.assertEqual(
            conversation.workspace_id, workspace.workspace_id
        )

    def test_service_does_not_allow_cross_user_conversation_access(self):
        workspace_b = self.service.create_workspace(self.auth_b, "B")
        conversation_b = self.service.create_conversation(
            self.auth_b, workspace_b.workspace_id, "Private"
        )
        with self.assertRaises(OwnershipError):
            self.service.get_conversation(
                self.auth_a, conversation_b.conversation_id
            )

    def test_model_reply_boundary_is_hardcoded_at_service_layer(self):
        workspace = self.service.create_workspace(self.auth_a, "A")
        conversation = self.service.create_conversation(
            self.auth_a, workspace.workspace_id, "Chat"
        )
        reply = self.service.save_model_reply(
            self.auth_a,
            conversation.conversation_id,
            "ordinary model response",
            "STANDARD",
        )
        self.assertEqual(reply.authority, "MODEL_REPLY_UNCHECKED")
        self.assertEqual(reply.cfc_status, "NOT_CONNECTED_C2")

    def test_user_message_is_not_mislabeled_as_model_or_cfc(self):
        workspace = self.service.create_workspace(self.auth_a, "A")
        conversation = self.service.create_conversation(
            self.auth_a, workspace.workspace_id, "Chat"
        )
        message = self.service.save_user_message(
            self.auth_a,
            conversation.conversation_id,
            "my input",
            "STANDARD",
        )
        self.assertEqual(message.authority, "USER_INPUT")
        self.assertEqual(message.cfc_status, "NOT_APPLICABLE")

    def test_hawm_snapshot_round_trip_stays_inside_owner_boundary(self):
        workspace = self.service.create_workspace(self.auth_a, "A")
        conversation = self.service.create_conversation(
            self.auth_a, workspace.workspace_id, "Chat"
        )
        snapshot = self.service.save_hawm_snapshot(
            self.auth_a,
            conversation.conversation_id,
            {"UNRESOLVED": ["claim-1"]},
            "ordinary_model_reply_unchecked",
        )
        self.assertEqual(snapshot.state["UNRESOLVED"], ["claim-1"])
        with self.assertRaises(OwnershipError):
            self.store.list_hawm_snapshots(
                self.auth_b.user_id, conversation.conversation_id
            )

    def test_cfc_run_requires_separate_explicit_save_path(self):
        workspace = self.service.create_workspace(self.auth_a, "A")
        conversation = self.service.create_conversation(
            self.auth_a, workspace.workspace_id, "Chat"
        )
        run = self.service.save_cfc_run(
            self.auth_a,
            conversation.conversation_id,
            case_id="CASE_01_UNRESOLVED_POSITIVE",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"claim_state": "UNRESOLVED", "decision": "STOP"},
            replay_matches_reference=True,
        )
        self.assertFalse(run.controller_result["control_closure"])
        self.assertEqual(run.presentation["decision"], "STOP")
        messages = self.service.list_messages(
            self.auth_a, conversation.conversation_id
        )
        self.assertEqual(messages, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
