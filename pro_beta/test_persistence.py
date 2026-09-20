from __future__ import annotations

import unittest

from pro_beta.contracts import (
    AuditReportRecord,
    CFCRun,
    Conversation,
    HAWMSnapshot,
    Message,
    UsageEvent,
    UserAccount,
    Workspace,
    new_id,
)
from pro_beta.persistence import InMemoryPersistence, NotFoundError, OwnershipError


class ProBetaPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryPersistence()

        self.user_a = UserAccount(
            user_id=new_id("usr"),
            external_auth_subject="auth|a",
            email="a@example.com",
        )
        self.user_b = UserAccount(
            user_id=new_id("usr"),
            external_auth_subject="auth|b",
            email="b@example.com",
        )
        self.store.create_user(self.user_a)
        self.store.create_user(self.user_b)

        self.workspace_a = Workspace(
            workspace_id=new_id("ws"),
            user_id=self.user_a.user_id,
            name="A workspace",
        )
        self.workspace_b = Workspace(
            workspace_id=new_id("ws"),
            user_id=self.user_b.user_id,
            name="B workspace",
        )
        self.store.create_workspace(self.user_a.user_id, self.workspace_a)
        self.store.create_workspace(self.user_b.user_id, self.workspace_b)

        self.conversation_a = Conversation(
            conversation_id=new_id("conv"),
            workspace_id=self.workspace_a.workspace_id,
            title="A conversation",
        )
        self.conversation_b = Conversation(
            conversation_id=new_id("conv"),
            workspace_id=self.workspace_b.workspace_id,
            title="B conversation",
        )
        self.store.create_conversation(self.user_a.user_id, self.conversation_a)
        self.store.create_conversation(self.user_b.user_id, self.conversation_b)

    def test_user_a_cannot_read_user_b_workspace(self):
        with self.assertRaises(OwnershipError):
            self.store.get_workspace(
                self.user_a.user_id, self.workspace_b.workspace_id
            )

    def test_user_a_cannot_read_user_b_conversation(self):
        with self.assertRaises(OwnershipError):
            self.store.get_conversation(
                self.user_a.user_id, self.conversation_b.conversation_id
            )

    def test_user_a_cannot_append_message_to_user_b_conversation(self):
        msg = Message(
            message_id=new_id("msg"),
            conversation_id=self.conversation_b.conversation_id,
            role="assistant",
            content="should not persist",
            authority="MODEL_REPLY_UNCHECKED",
            cfc_status="NOT_CONNECTED_C2",
            mode="STANDARD",
        )
        with self.assertRaises(OwnershipError):
            self.store.append_message(self.user_a.user_id, msg)
        self.assertNotIn(msg.message_id, self.store.messages)

    def test_message_round_trip_preserves_boundary(self):
        msg = Message(
            message_id=new_id("msg"),
            conversation_id=self.conversation_a.conversation_id,
            role="assistant",
            content="example",
            authority="MODEL_REPLY_UNCHECKED",
            cfc_status="NOT_CONNECTED_C2",
            mode="STANDARD",
        )
        self.store.append_message(self.user_a.user_id, msg)
        rows = self.store.list_messages(
            self.user_a.user_id, self.conversation_a.conversation_id
        )
        self.assertEqual(rows, [msg])
        self.assertEqual(rows[0].authority, "MODEL_REPLY_UNCHECKED")
        self.assertEqual(rows[0].cfc_status, "NOT_CONNECTED_C2")

    def test_hawm_snapshot_is_scoped_to_owned_conversation(self):
        snapshot = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=self.conversation_a.conversation_id,
            state={"UNRESOLVED": ["claim-1"]},
            last_verified_state="ordinary_model_reply_unchecked",
        )
        self.store.add_hawm_snapshot(self.user_a.user_id, snapshot)
        rows = self.store.list_hawm_snapshots(
            self.user_a.user_id, self.conversation_a.conversation_id
        )
        self.assertEqual(rows, [snapshot])

        with self.assertRaises(OwnershipError):
            self.store.list_hawm_snapshots(
                self.user_b.user_id, self.conversation_a.conversation_id
            )

    def test_cfc_run_keeps_raw_result_and_presentation(self):
        run = CFCRun(
            run_id=new_id("cfc"),
            conversation_id=self.conversation_a.conversation_id,
            case_id="CASE_01_UNRESOLVED_POSITIVE",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"claim_state": "UNRESOLVED", "decision": "STOP"},
            replay_matches_reference=True,
        )
        self.store.add_cfc_run(self.user_a.user_id, run)
        rows = self.store.list_cfc_runs(
            self.user_a.user_id, self.conversation_a.conversation_id
        )
        self.assertEqual(rows[0].controller_result["control_closure"], False)
        self.assertEqual(rows[0].presentation["decision"], "STOP")

    def test_audit_report_cannot_bind_cfc_run_from_other_conversation(self):
        foreign_run = CFCRun(
            run_id=new_id("cfc"),
            conversation_id=self.conversation_b.conversation_id,
            case_id="CASE_01_UNRESOLVED_POSITIVE",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"claim_state": "UNRESOLVED", "decision": "STOP"},
        )
        self.store.add_cfc_run(self.user_b.user_id, foreign_run)

        report = AuditReportRecord(
            report_id=new_id("report"),
            conversation_id=self.conversation_a.conversation_id,
            cfc_run_id=foreign_run.run_id,
            status="READY",
        )
        with self.assertRaises(OwnershipError):
            self.store.add_audit_report(self.user_a.user_id, report)

    def test_usage_event_cannot_be_written_for_another_user(self):
        event = UsageEvent(
            event_id=new_id("evt"),
            user_id=self.user_b.user_id,
            event_type="message",
        )
        with self.assertRaises(OwnershipError):
            self.store.add_usage_event(self.user_a.user_id, event)

    def test_missing_workspace_is_not_treated_as_owned(self):
        with self.assertRaises(NotFoundError):
            self.store.get_workspace(self.user_a.user_id, "ws_missing")


if __name__ == "__main__":
    unittest.main(verbosity=2)
