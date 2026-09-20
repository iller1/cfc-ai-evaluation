from __future__ import annotations

import os
import unittest
from pathlib import Path

from pro_beta.contracts import (
    AuditReportRecord,
    CFCRun,
    Conversation,
    HAWMSnapshot,
    Message,
    UserAccount,
    Workspace,
    new_id,
)
from pro_beta.persistence import OwnershipError
from pro_beta.postgres_persistence import PostgresPersistence

try:
    import psycopg
except ImportError:  # local/offline environments may not install the adapter
    psycopg = None


@unittest.skipIf(psycopg is None, "psycopg is not installed")
class PostgresPersistenceIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dsn = os.environ.get("PRO_BETA_TEST_DATABASE_URL")
        if not dsn:
            raise unittest.SkipTest("PRO_BETA_TEST_DATABASE_URL is not set")
        cls.connection = psycopg.connect(dsn)
        schema = Path("pro_beta/schema.sql").read_text(encoding="utf-8")
        with cls.connection.cursor() as cur:
            cur.execute(schema)
        cls.connection.commit()

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def setUp(self):
        with self.connection.cursor() as cur:
            cur.execute(
                """
                truncate table
                    usage_events, audit_reports, cfc_runs, hawm_snapshots,
                    messages, conversations, workspaces, users
                restart identity cascade
                """
            )
        self.connection.commit()
        self.store = PostgresPersistence(self.connection)

        self.user_a = UserAccount(new_id("usr"), "auth|pg-a", "a@example.com")
        self.user_b = UserAccount(new_id("usr"), "auth|pg-b", "b@example.com")
        self.store.create_user(self.user_a)
        self.store.create_user(self.user_b)

        self.workspace_a = Workspace(new_id("ws"), self.user_a.user_id, "A")
        self.workspace_b = Workspace(new_id("ws"), self.user_b.user_id, "B")
        self.store.create_workspace(self.user_a.user_id, self.workspace_a)
        self.store.create_workspace(self.user_b.user_id, self.workspace_b)

        self.conversation_a = Conversation(
            new_id("conv"), self.workspace_a.workspace_id, "A conversation"
        )
        self.conversation_b = Conversation(
            new_id("conv"), self.workspace_b.workspace_id, "B conversation"
        )
        self.store.create_conversation(self.user_a.user_id, self.conversation_a)
        self.store.create_conversation(self.user_b.user_id, self.conversation_b)

    def test_postgres_blocks_cross_user_workspace_read(self):
        with self.assertRaises(OwnershipError):
            self.store.get_workspace(
                self.user_a.user_id, self.workspace_b.workspace_id
            )

    def test_postgres_blocks_cross_user_conversation_write(self):
        msg = Message(
            message_id=new_id("msg"),
            conversation_id=self.conversation_b.conversation_id,
            role="assistant",
            content="must not persist",
            authority="MODEL_REPLY_UNCHECKED",
            cfc_status="NOT_CONNECTED_C2",
            mode="STANDARD",
        )
        with self.assertRaises(OwnershipError):
            self.store.append_message(self.user_a.user_id, msg)

    def test_postgres_lists_only_owned_workspace_conversations(self):
        rows = self.store.list_conversations(
            self.user_a.user_id, self.workspace_a.workspace_id
        )
        self.assertEqual(
            [c.conversation_id for c in rows],
            [self.conversation_a.conversation_id],
        )
        with self.assertRaises(OwnershipError):
            self.store.list_conversations(
                self.user_a.user_id, self.workspace_b.workspace_id
            )

    def test_postgres_user_message_round_trip_preserves_boundary(self):
        msg = Message(
            message_id=new_id("msg"),
            conversation_id=self.conversation_a.conversation_id,
            role="user",
            content="hello",
            authority="USER_INPUT",
            cfc_status="NOT_APPLICABLE",
            mode="STANDARD",
        )
        self.store.append_message(self.user_a.user_id, msg)
        rows = self.store.list_messages(
            self.user_a.user_id, self.conversation_a.conversation_id
        )
        self.assertEqual(rows[0].authority, "USER_INPUT")
        self.assertEqual(rows[0].cfc_status, "NOT_APPLICABLE")

    def test_postgres_message_round_trip_preserves_boundary(self):
        msg = Message(
            message_id=new_id("msg"),
            conversation_id=self.conversation_a.conversation_id,
            role="assistant",
            content="ordinary reply",
            authority="MODEL_REPLY_UNCHECKED",
            cfc_status="NOT_CONNECTED_C2",
            mode="STANDARD",
        )
        self.store.append_message(self.user_a.user_id, msg)
        rows = self.store.list_messages(
            self.user_a.user_id, self.conversation_a.conversation_id
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].content, "ordinary reply")
        self.assertEqual(rows[0].authority, "MODEL_REPLY_UNCHECKED")
        self.assertEqual(rows[0].cfc_status, "NOT_CONNECTED_C2")

    def test_postgres_hawm_json_round_trip(self):
        snap = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=self.conversation_a.conversation_id,
            state={"UNRESOLVED": ["claim-1"], "NEXT_ACTION": "collect evidence"},
            last_verified_state="ordinary_model_reply_unchecked",
        )
        self.store.add_hawm_snapshot(self.user_a.user_id, snap)
        with self.connection.cursor() as cur:
            cur.execute(
                "select state from hawm_snapshots where snapshot_id = %s",
                (snap.snapshot_id,),
            )
            state = cur.fetchone()[0]
        self.assertEqual(state["UNRESOLVED"], ["claim-1"])

    def test_postgres_lists_hawm_snapshots_in_order(self):
        first = HAWMSnapshot(
            snapshot_id="hawm_1",
            conversation_id=self.conversation_a.conversation_id,
            state={"goal": "first"},
            last_verified_state="USER_WORKING_STATE",
            created_at="2026-01-01T00:00:00+00:00",
        )
        second = HAWMSnapshot(
            snapshot_id="hawm_2",
            conversation_id=self.conversation_a.conversation_id,
            state={"goal": "second"},
            last_verified_state="USER_WORKING_STATE",
            created_at="2026-01-01T00:00:01+00:00",
        )
        self.store.add_hawm_snapshot(self.user_a.user_id, first)
        self.store.add_hawm_snapshot(self.user_a.user_id, second)
        rows = self.store.list_hawm_snapshots(
            self.user_a.user_id, self.conversation_a.conversation_id
        )
        self.assertEqual([r.snapshot_id for r in rows], ["hawm_1", "hawm_2"])
        self.assertEqual(rows[-1].state["goal"], "second")

    def test_postgres_cfc_keeps_raw_result_separate_from_presentation(self):
        run = CFCRun(
            run_id=new_id("cfc"),
            conversation_id=self.conversation_a.conversation_id,
            case_id="CASE_01_UNRESOLVED_POSITIVE",
            controller_anchor="0.2.90rc1",
            controller_result={
                "control_closure": False,
                "claim_states": [{"status": "UNRESOLVED"}],
            },
            presentation={"claim_state": "UNRESOLVED", "decision": "STOP"},
            replay_matches_reference=True,
        )
        self.store.add_cfc_run(self.user_a.user_id, run)
        with self.connection.cursor() as cur:
            cur.execute(
                """
                select controller_result, presentation
                from cfc_runs where run_id = %s
                """,
                (run.run_id,),
            )
            raw, presentation = cur.fetchone()
        self.assertFalse(raw["control_closure"])
        self.assertEqual(presentation["decision"], "STOP")
        self.assertNotEqual(raw, presentation)

    def test_postgres_lists_cfc_runs_in_order(self):
        first = CFCRun(
            run_id="cfc_1",
            conversation_id=self.conversation_a.conversation_id,
            case_id="CASE_01_UNRESOLVED_POSITIVE",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"decision": "STOP"},
            replay_matches_reference=True,
            created_at="2026-01-01T00:00:00+00:00",
        )
        second = CFCRun(
            run_id="cfc_2",
            conversation_id=self.conversation_a.conversation_id,
            case_id="CASE_07_VALID_POSITIVE_CLOSURE",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": True},
            presentation={"decision": "ALLOW"},
            replay_matches_reference=True,
            created_at="2026-01-01T00:00:01+00:00",
        )
        self.store.add_cfc_run(self.user_a.user_id, first)
        self.store.add_cfc_run(self.user_a.user_id, second)
        rows = self.store.list_cfc_runs(
            self.user_a.user_id, self.conversation_a.conversation_id
        )
        self.assertEqual([r.run_id for r in rows], ["cfc_1", "cfc_2"])
        self.assertEqual(rows[-1].presentation["decision"], "ALLOW")

    def test_postgres_audit_report_metadata_round_trip(self):
        run = CFCRun(
            run_id=new_id("cfc"),
            conversation_id=self.conversation_a.conversation_id,
            case_id="HAWM_STRUCTURED_CUSTOM",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": True},
            presentation={"claim_state": "VERIFIED", "decision": "ALLOW"},
        )
        self.store.add_cfc_run(self.user_a.user_id, run)
        report = AuditReportRecord(
            report_id=new_id("report"),
            conversation_id=self.conversation_a.conversation_id,
            cfc_run_id=run.run_id,
            status="GENERATED_JSON_MARKDOWN",
            artifact_path=None,
        )
        saved = self.store.add_audit_report(self.user_a.user_id, report)
        self.assertEqual(saved.report_id, report.report_id)
        with self.connection.cursor() as cur:
            cur.execute(
                """
                select conversation_id, cfc_run_id, status, artifact_path
                from audit_reports where report_id = %s
                """,
                (report.report_id,),
            )
            row = cur.fetchone()
        self.assertEqual(row[0], self.conversation_a.conversation_id)
        self.assertEqual(row[1], run.run_id)
        self.assertEqual(row[2], "GENERATED_JSON_MARKDOWN")
        self.assertIsNone(row[3])

    def test_postgres_user_lists_only_own_workspaces(self):
        rows = self.store.list_workspaces(self.user_a.user_id)
        self.assertEqual([w.workspace_id for w in rows], [self.workspace_a.workspace_id])


if __name__ == "__main__":
    unittest.main(verbosity=2)
