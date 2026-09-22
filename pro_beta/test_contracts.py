from __future__ import annotations

import unittest

from pro_beta.contracts import (
    CFCRun,
    Conversation,
    HAWMSnapshot,
    Message,
    UserAccount,
    Workspace,
    new_id,
    public_dict,
)


class ProBetaContractsTests(unittest.TestCase):
    def test_account_uses_external_auth_subject_not_password(self):
        account = UserAccount(
            user_id=new_id("usr"),
            external_auth_subject="auth0|example",
            email="test@example.com",
        )
        data = public_dict(account)
        self.assertIn("external_auth_subject", data)
        self.assertNotIn("password", data)
        self.assertNotIn("password_hash", data)

    def test_message_preserves_unchecked_boundary(self):
        msg = Message(
            message_id=new_id("msg"),
            conversation_id=new_id("conv"),
            role="assistant",
            content="example",
            authority="MODEL_REPLY_UNCHECKED",
            cfc_status="NOT_CONNECTED_C2",
            mode="STANDARD",
        )
        data = public_dict(msg)
        self.assertEqual(data["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(data["cfc_status"], "NOT_CONNECTED_C2")

    def test_hawm_snapshot_is_explicit_state_record(self):
        snap = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=new_id("conv"),
            state={"UNRESOLVED": ["claim-1"], "NEXT_ACTION": "collect evidence"},
            last_verified_state="ordinary_model_reply_unchecked",
        )
        data = public_dict(snap)
        self.assertEqual(data["state"]["UNRESOLVED"], ["claim-1"])

    def test_cfc_run_keeps_raw_controller_result_and_presentation(self):
        run = CFCRun(
            run_id=new_id("cfc"),
            conversation_id=new_id("conv"),
            case_id="CASE_01_UNRESOLVED_POSITIVE",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"claim_state": "UNRESOLVED", "decision": "STOP"},
            replay_matches_reference=True,
        )
        data = public_dict(run)
        self.assertFalse(data["controller_result"]["control_closure"])
        self.assertEqual(data["presentation"]["claim_state"], "UNRESOLVED")

    def test_ids_are_namespaced(self):
        self.assertTrue(new_id("usr").startswith("usr_"))
        self.assertTrue(new_id("ws").startswith("ws_"))

    def test_workspace_and_conversation_bind_to_owner_chain(self):
        user_id = new_id("usr")
        workspace = Workspace(workspace_id=new_id("ws"), user_id=user_id, name="Pilot")
        conversation = Conversation(
            conversation_id=new_id("conv"),
            workspace_id=workspace.workspace_id,
            title="First analysis",
        )
        self.assertEqual(workspace.user_id, user_id)
        self.assertEqual(conversation.workspace_id, workspace.workspace_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
