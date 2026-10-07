from __future__ import annotations

import os
import unittest
from pathlib import Path

from pro_beta.contracts import (
    AuditReportRecord,
    BenchmarkManualLabel,
    BenchmarkRun,
    CFCRun,
    FoundingBetaMeasurement,
    Conversation,
    HAWMSnapshot,
    HAWMSnapshotIdentity,
    EvidenceSetRegistration,
    EvidenceProvenanceReceipt,
    EvidenceDependencyReceipt,
    ExecutionReceiptRecord,
    Message,
    UserAccount,
    Workspace,
    new_id,
)
from pro_beta.persistence import NotFoundError, OwnershipError
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
                    usage_events, founding_beta_measurements, benchmark_runs,
                    audit_reports, execution_receipts, cfc_runs, hawm_snapshots, messages,
                    conversations, workspaces, users
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

    def test_postgres_founding_beta_measurement_round_trip_without_content(self):
        item = FoundingBetaMeasurement(
            measurement_id=new_id("fbm"),
            workspace_id=self.workspace_a.workspace_id,
            system_version="founding-beta-rc1",
            workflow_type="document_review",
            case_id="case-001",
            cfc_result="UNRESOLVED",
            reason_code="UPSTREAM_STATE_INCOMPLETE",
            hawm_state="UNRESOLVED_PRESENTED",
            human_assessment="AGREE",
            final_action="ESCALATED",
            problem_type="UPSTREAM_STATE_ISSUE",
            comment="sanitized",
        )
        self.store.add_founding_beta_measurement(self.user_a.user_id, item)
        rows = self.store.list_founding_beta_measurements(
            self.user_a.user_id, self.workspace_a.workspace_id
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].reason_code, "UPSTREAM_STATE_INCOMPLETE")
        self.assertFalse(hasattr(rows[0], "content"))
        with self.assertRaises(OwnershipError):
            self.store.list_founding_beta_measurements(
                self.user_b.user_id, self.workspace_a.workspace_id
            )

    def test_postgres_founding_beta_measurement_purge(self):
        item = FoundingBetaMeasurement(
            measurement_id=new_id("fbm"),
            workspace_id=self.workspace_a.workspace_id,
            system_version="rc1",
            workflow_type="research",
            case_id="delete-001",
            cfc_result="STOP",
            reason_code="TEST",
            hawm_state="STOP_PRESENTED",
            human_assessment="AGREE",
            final_action="DID_NOT_ACT",
            problem_type="NONE",
        )
        self.store.add_founding_beta_measurement(self.user_a.user_id, item)
        with self.assertRaises(OwnershipError):
            self.store.delete_founding_beta_measurements(
                self.user_b.user_id, self.workspace_a.workspace_id
            )
        deleted = self.store.delete_founding_beta_measurements(
            self.user_a.user_id, self.workspace_a.workspace_id
        )
        self.assertEqual(deleted, 1)
        self.assertEqual(
            self.store.list_founding_beta_measurements(
                self.user_a.user_id, self.workspace_a.workspace_id
            ),
            [],
        )

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
            provider="claude",
            model="claude-sonnet-4-5",
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
            provider="claude",
            model="claude-sonnet-4-5",
        )
        self.store.append_message(self.user_a.user_id, msg)
        rows = self.store.list_messages(
            self.user_a.user_id, self.conversation_a.conversation_id
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].content, "ordinary reply")
        self.assertEqual(rows[0].authority, "MODEL_REPLY_UNCHECKED")
        self.assertEqual(rows[0].cfc_status, "NOT_CONNECTED_C2")
        self.assertEqual(rows[0].provider, "claude")
        self.assertEqual(rows[0].model, "claude-sonnet-4-5")

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

    def test_postgres_hawm_snapshot_identity_round_trip(self):
        snap = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=self.conversation_a.conversation_id,
            state={"goal": "identity-anchor"},
            last_verified_state="USER_WORKING_STATE",
        )
        self.store.add_hawm_snapshot(self.user_a.user_id, snap)
        identity = HAWMSnapshotIdentity(
            snapshot_id=snap.snapshot_id,
            conversation_id=self.conversation_a.conversation_id,
            case_id="HAWM_PRO_BETA_STATE",
            arm_id="HAWM_WORKING_STATE",
            state_id=snap.snapshot_id,
            lineage_id=self.conversation_a.conversation_id,
            previous_state_id=None,
            registered_snapshot_fingerprint="a" * 64,
            adapter_version="HAWM_STATE_IDENTITY_ADAPTER_V0_1",
        )
        self.store.add_hawm_snapshot_identity(self.user_a.user_id, identity)
        loaded = self.store.get_hawm_snapshot_identity(
            self.user_a.user_id,
            self.conversation_a.conversation_id,
            snap.snapshot_id,
        )
        self.assertEqual(loaded.snapshot_id, snap.snapshot_id)
        self.assertEqual(loaded.registered_snapshot_fingerprint, "a" * 64)
        with self.assertRaises(OwnershipError):
            self.store.get_hawm_snapshot_identity(
                self.user_b.user_id,
                self.conversation_a.conversation_id,
                snap.snapshot_id,
            )

    def test_postgres_evidence_provenance_registry_round_trip(self):
        snap = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=self.conversation_a.conversation_id,
            state={"goal": "evidence-registry"},
            last_verified_state="USER_WORKING_STATE",
        )
        self.store.add_hawm_snapshot(self.user_a.user_id, snap)
        identity = HAWMSnapshotIdentity(
            snapshot_id=snap.snapshot_id,
            conversation_id=self.conversation_a.conversation_id,
            case_id="HAWM_PRO_BETA_STATE",
            arm_id="HAWM_WORKING_STATE",
            state_id=snap.snapshot_id,
            lineage_id=self.conversation_a.conversation_id,
            previous_state_id=None,
            registered_snapshot_fingerprint="b" * 64,
            adapter_version="HAWM_STATE_IDENTITY_ADAPTER_V0_1",
        )
        self.store.add_hawm_snapshot_identity(self.user_a.user_id, identity)

        registration = EvidenceSetRegistration(
            registration_id=new_id("evidence_set"),
            snapshot_id=snap.snapshot_id,
            conversation_id=self.conversation_a.conversation_id,
            state_id=snap.snapshot_id,
            evidence_set=[
                {
                    "evidence_id": "E1",
                    "source_id": "S1",
                    "validity": "CURRENT",
                    "scope_status": "MATCH",
                    "failure_domain_id": "FD1",
                }
            ],
            missing_evidence=[],
            adapter_version="EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_V0_1",
        )
        self.store.add_evidence_set_registration(
            self.user_a.user_id, registration
        )

        provenance = EvidenceProvenanceReceipt(
            receipt_id=new_id("evidence_prov"),
            snapshot_id=snap.snapshot_id,
            conversation_id=self.conversation_a.conversation_id,
            state_id=snap.snapshot_id,
            evidence_id="E1",
            source_id="S1",
            status="ESTABLISHED",
            adapter_version="EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_V0_1",
        )
        self.store.add_evidence_provenance_receipt(
            self.user_a.user_id, provenance
        )

        dependency = EvidenceDependencyReceipt(
            receipt_id=new_id("evidence_dep"),
            snapshot_id=snap.snapshot_id,
            conversation_id=self.conversation_a.conversation_id,
            state_id=snap.snapshot_id,
            evidence_ids=["E1"],
            failure_domains={"E1": "FD1"},
            status="RESOLVED",
            adapter_version="EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_V0_1",
        )
        self.store.add_evidence_dependency_receipt(
            self.user_a.user_id, dependency
        )

        loaded_registration = self.store.get_evidence_set_registration(
            self.user_a.user_id,
            self.conversation_a.conversation_id,
            snap.snapshot_id,
        )
        loaded_provenance = self.store.list_evidence_provenance_receipts(
            self.user_a.user_id,
            self.conversation_a.conversation_id,
            snap.snapshot_id,
        )
        loaded_dependency = self.store.get_evidence_dependency_receipt(
            self.user_a.user_id,
            self.conversation_a.conversation_id,
            snap.snapshot_id,
        )

        self.assertEqual(loaded_registration.evidence_set, registration.evidence_set)
        self.assertEqual(loaded_provenance[0].source_id, "S1")
        self.assertEqual(loaded_dependency.failure_domains, {"E1": "FD1"})

        with self.assertRaises(OwnershipError):
            self.store.get_evidence_set_registration(
                self.user_b.user_id,
                self.conversation_a.conversation_id,
                snap.snapshot_id,
            )

    def test_postgres_evidence_registration_requires_identity_anchor(self):
        snap = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=self.conversation_a.conversation_id,
            state={"goal": "snapshot-without-identity"},
            last_verified_state="USER_WORKING_STATE",
        )
        self.store.add_hawm_snapshot(self.user_a.user_id, snap)
        registration = EvidenceSetRegistration(
            registration_id=new_id("evidence_set"),
            snapshot_id=snap.snapshot_id,
            conversation_id=self.conversation_a.conversation_id,
            state_id=snap.snapshot_id,
            evidence_set=[],
            missing_evidence=[],
            adapter_version="EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_V0_1",
        )

        with self.assertRaisesRegex(
            NotFoundError,
            "HAWM_SNAPSHOT_IDENTITY_NOT_FOUND",
        ):
            self.store.add_evidence_set_registration(
                self.user_a.user_id, registration
            )

        from psycopg.errors import ForeignKeyViolation
        with self.assertRaises(ForeignKeyViolation):
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    insert into evidence_set_registrations (
                        registration_id, snapshot_id, conversation_id, state_id,
                        evidence_set, missing_evidence, adapter_version
                    ) values (%s,%s,%s,%s,'[]'::jsonb,'[]'::jsonb,%s)
                    """,
                    (
                        new_id("evidence_set"),
                        snap.snapshot_id,
                        self.conversation_a.conversation_id,
                        snap.snapshot_id,
                        "EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_V0_1",
                    ),
                )
        self.connection.rollback()

    def test_postgres_evidence_registry_rejects_cross_conversation_snapshot(self):
        snap_b = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=self.conversation_b.conversation_id,
            state={"goal": "other-owner"},
            last_verified_state="USER_WORKING_STATE",
        )
        self.store.add_hawm_snapshot(self.user_b.user_id, snap_b)
        identity_b = HAWMSnapshotIdentity(
            snapshot_id=snap_b.snapshot_id,
            conversation_id=self.conversation_b.conversation_id,
            case_id="HAWM_PRO_BETA_STATE",
            arm_id="HAWM_WORKING_STATE",
            state_id=snap_b.snapshot_id,
            lineage_id=self.conversation_b.conversation_id,
            previous_state_id=None,
            registered_snapshot_fingerprint="c" * 64,
            adapter_version="HAWM_STATE_IDENTITY_ADAPTER_V0_1",
        )
        self.store.add_hawm_snapshot_identity(self.user_b.user_id, identity_b)

        registration = EvidenceSetRegistration(
            registration_id=new_id("evidence_set"),
            snapshot_id=snap_b.snapshot_id,
            conversation_id=self.conversation_a.conversation_id,
            state_id=snap_b.snapshot_id,
            evidence_set=[],
            missing_evidence=[],
            adapter_version="EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_V0_1",
        )

        with self.assertRaises(OwnershipError):
            self.store.add_evidence_set_registration(
                self.user_a.user_id, registration
            )

    def _execution_fixture(self):
        snap = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=self.conversation_a.conversation_id,
            state={"goal": "execution"},
            last_verified_state="USER_WORKING_STATE",
        )
        self.store.add_hawm_snapshot(self.user_a.user_id, snap)
        identity = HAWMSnapshotIdentity(
            snapshot_id=snap.snapshot_id,
            conversation_id=self.conversation_a.conversation_id,
            case_id="HAWM_PRO_BETA_STATE",
            arm_id="HAWM_WORKING_STATE",
            state_id=snap.snapshot_id,
            lineage_id=self.conversation_a.conversation_id,
            previous_state_id=None,
            registered_snapshot_fingerprint="d" * 64,
            adapter_version="HAWM_STATE_IDENTITY_ADAPTER_V0_1",
        )
        self.store.add_hawm_snapshot_identity(self.user_a.user_id, identity)
        run = CFCRun(
            run_id=new_id("cfc"),
            conversation_id=self.conversation_a.conversation_id,
            case_id="HAWM_STRUCTURED_CUSTOM",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"decision": "STOP"},
            hawm_snapshot_id=snap.snapshot_id,
        )
        self.store.add_cfc_run(self.user_a.user_id, run)
        receipt = ExecutionReceiptRecord(
            receipt_id=new_id("exec"),
            conversation_id=self.conversation_a.conversation_id,
            action_id="PRO_BETA_EXECUTION_PREFLIGHT",
            controller_run_id=run.run_id,
            controller_decision="HOLD",
            controller_state_id=snap.snapshot_id,
            controller_state_version=identity.registered_snapshot_fingerprint,
            pre_execution_state_id=snap.snapshot_id,
            pre_execution_state_version=identity.registered_snapshot_fingerprint,
            idempotency_key=new_id("idem"),
            cfc_authority_state="NOT_ESTABLISHED",
            current_authority_state="NOT_ESTABLISHED",
            human_review_required=False,
            human_review_approved=False,
            transaction_required=False,
            transaction_supported=False,
            attempted=False,
            executed=False,
            execution_status="BLOCKED",
            effect_handle=None,
            blockers=["SYNTHETIC_CFC_NOT_REAL_ACTION_AUTHORITY"],
            reason="SYNTHETIC_CFC_NOT_REAL_ACTION_AUTHORITY",
            adapter_version="EXECUTION_GATE_RECEIPT_ADAPTER_V0_1",
        )
        return snap, identity, run, receipt

    def test_postgres_execution_receipt_round_trip(self):
        snap, identity, run, receipt = self._execution_fixture()

        self.store.add_execution_receipt(self.user_a.user_id, receipt)
        rows = self.store.list_execution_receipts(
            self.user_a.user_id,
            self.conversation_a.conversation_id,
        )

        self.assertEqual(len(rows), 1)
        loaded = rows[0]
        self.assertEqual(loaded.receipt_id, receipt.receipt_id)
        self.assertEqual(loaded.controller_run_id, run.run_id)
        self.assertEqual(loaded.controller_state_id, snap.snapshot_id)
        self.assertEqual(
            loaded.controller_state_version,
            identity.registered_snapshot_fingerprint,
        )
        self.assertFalse(loaded.attempted)
        self.assertFalse(loaded.executed)
        self.assertEqual(loaded.execution_status, "BLOCKED")

        with self.assertRaises(OwnershipError):
            self.store.list_execution_receipts(
                self.user_b.user_id,
                self.conversation_a.conversation_id,
            )

    def test_postgres_execution_receipt_rejects_wrong_run_state(self):
        snap, identity, run, receipt = self._execution_fixture()

        other = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=self.conversation_a.conversation_id,
            state={"goal": "other-state"},
            last_verified_state="USER_WORKING_STATE",
        )
        self.store.add_hawm_snapshot(self.user_a.user_id, other)
        other_identity = HAWMSnapshotIdentity(
            snapshot_id=other.snapshot_id,
            conversation_id=self.conversation_a.conversation_id,
            case_id="HAWM_PRO_BETA_STATE",
            arm_id="HAWM_WORKING_STATE",
            state_id=other.snapshot_id,
            lineage_id=self.conversation_a.conversation_id,
            previous_state_id=snap.snapshot_id,
            registered_snapshot_fingerprint="e" * 64,
            adapter_version="HAWM_STATE_IDENTITY_ADAPTER_V0_1",
        )
        self.store.add_hawm_snapshot_identity(
            self.user_a.user_id, other_identity
        )
        wrong = ExecutionReceiptRecord(
            **{
                **receipt.__dict__,
                "receipt_id": new_id("exec"),
                "controller_state_id": other.snapshot_id,
                "controller_state_version": (
                    other_identity.registered_snapshot_fingerprint
                ),
                "pre_execution_state_id": other.snapshot_id,
                "pre_execution_state_version": (
                    other_identity.registered_snapshot_fingerprint
                ),
                "idempotency_key": new_id("idem"),
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "EXECUTION_CONTROLLER_RUN_STATE_MISMATCH",
        ):
            self.store.add_execution_receipt(
                self.user_a.user_id, wrong
            )

    def test_postgres_direct_insert_rejects_wrong_state_version(self):
        snap, identity, run, receipt = self._execution_fixture()
        from psycopg.errors import ForeignKeyViolation

        with self.assertRaises(ForeignKeyViolation):
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    insert into execution_receipts (
                      receipt_id, conversation_id, action_id, controller_run_id,
                      controller_decision, controller_state_id,
                      controller_state_version, pre_execution_state_id,
                      pre_execution_state_version, idempotency_key,
                      cfc_authority_state, current_authority_state,
                      human_review_required, human_review_approved,
                      transaction_required, transaction_supported,
                      attempted, executed, execution_status, effect_handle,
                      blockers, reason, adapter_version
                    ) values (
                      %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                      false,false,false,false,false,false,'BLOCKED',null,
                      '[]'::jsonb,%s,%s
                    )
                    """,
                    (
                        new_id("exec"),
                        self.conversation_a.conversation_id,
                        "PRO_BETA_EXECUTION_PREFLIGHT",
                        run.run_id,
                        "HOLD",
                        snap.snapshot_id,
                        "f" * 64,
                        snap.snapshot_id,
                        identity.registered_snapshot_fingerprint,
                        new_id("idem"),
                        "NOT_ESTABLISHED",
                        "NOT_ESTABLISHED",
                        "WRONG_VERSION",
                        "EXECUTION_GATE_RECEIPT_ADAPTER_V0_1",
                    ),
                )
        self.connection.rollback()

    def test_postgres_direct_insert_rejects_execution_flag_laundering(self):
        snap, identity, run, receipt = self._execution_fixture()
        from psycopg.errors import CheckViolation

        with self.assertRaises(CheckViolation):
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    insert into execution_receipts (
                      receipt_id, conversation_id, action_id, controller_run_id,
                      controller_decision, controller_state_id,
                      controller_state_version, pre_execution_state_id,
                      pre_execution_state_version, idempotency_key,
                      cfc_authority_state, current_authority_state,
                      human_review_required, human_review_approved,
                      transaction_required, transaction_supported,
                      attempted, executed, execution_status, effect_handle,
                      blockers, reason, adapter_version
                    ) values (
                      %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                      false,false,false,false,true,false,'BLOCKED',null,
                      '[]'::jsonb,%s,%s
                    )
                    """,
                    (
                        new_id("exec"),
                        self.conversation_a.conversation_id,
                        "PRO_BETA_EXECUTION_PREFLIGHT",
                        run.run_id,
                        "HOLD",
                        snap.snapshot_id,
                        identity.registered_snapshot_fingerprint,
                        snap.snapshot_id,
                        identity.registered_snapshot_fingerprint,
                        new_id("idem"),
                        "NOT_ESTABLISHED",
                        "NOT_ESTABLISHED",
                        "FLAG_LAUNDERING",
                        "EXECUTION_GATE_RECEIPT_ADAPTER_V0_1",
                    ),
                )
        self.connection.rollback()

    def test_postgres_execution_idempotency_key_is_unique_per_conversation(self):
        snap, identity, run, receipt = self._execution_fixture()
        self.store.add_execution_receipt(self.user_a.user_id, receipt)
        second = ExecutionReceiptRecord(
            **{
                **receipt.__dict__,
                "receipt_id": new_id("exec"),
            }
        )

        from psycopg.errors import UniqueViolation
        with self.assertRaises(UniqueViolation):
            self.store.add_execution_receipt(
                self.user_a.user_id, second
            )
        self.connection.rollback()

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

    def test_postgres_run_has_durable_owned_snapshot_reference(self):
        from pro_beta.persistence import NotFoundError
        snap_a = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=self.conversation_a.conversation_id,
            state={"goal": "actual run input"},
            last_verified_state="USER_WORKING_STATE",
        )
        snap_b = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=self.conversation_b.conversation_id,
            state={"goal": "other owner"},
            last_verified_state="USER_WORKING_STATE",
        )
        self.store.add_hawm_snapshot(self.user_a.user_id, snap_a)
        self.store.add_hawm_snapshot(self.user_b.user_id, snap_b)
        run = CFCRun(
            run_id=new_id("cfc"),
            conversation_id=self.conversation_a.conversation_id,
            case_id="HAWM_STRUCTURED_CUSTOM",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"decision": "STOP"},
            hawm_snapshot_id=snap_a.snapshot_id,
        )
        self.store.add_cfc_run(self.user_a.user_id, run)
        rows = self.store.list_cfc_runs(
            self.user_a.user_id, self.conversation_a.conversation_id
        )
        self.assertEqual(rows[-1].hawm_snapshot_id, snap_a.snapshot_id)
        with self.connection.cursor() as cur:
            cur.execute(
                "select hawm_snapshot_id from cfc_runs where run_id = %s",
                (run.run_id,),
            )
            self.assertEqual(cur.fetchone()[0], snap_a.snapshot_id)
        with self.assertRaises(OwnershipError):
            self.store.add_cfc_run(
                self.user_a.user_id,
                CFCRun(
                    run_id=new_id("cfc"),
                    conversation_id=self.conversation_a.conversation_id,
                    case_id="HAWM_STRUCTURED_CUSTOM",
                    controller_anchor="0.2.90rc1",
                    controller_result={}, presentation={},
                    hawm_snapshot_id=snap_b.snapshot_id,
                ),
            )
        with self.assertRaises(NotFoundError):
            self.store.add_cfc_run(
                self.user_a.user_id,
                CFCRun(
                    run_id=new_id("cfc"),
                    conversation_id=self.conversation_a.conversation_id,
                    case_id="HAWM_STRUCTURED_CUSTOM",
                    controller_anchor="0.2.90rc1",
                    controller_result={}, presentation={},
                    hawm_snapshot_id="hawm_does_not_exist",
                ),
            )

        # Test the DATABASE boundary even if an adapter bypasses its check.
        from psycopg.errors import ForeignKeyViolation
        with self.assertRaises(ForeignKeyViolation):
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    insert into cfc_runs (
                        run_id, conversation_id, case_id, controller_anchor,
                        controller_result, presentation, hawm_snapshot_id
                    ) values (%s,%s,%s,%s,'{}'::jsonb,'{}'::jsonb,%s)
                    """,
                    (
                        new_id("cfc"), self.conversation_a.conversation_id,
                        "HAWM_STRUCTURED_CUSTOM", "0.2.90rc1",
                        snap_b.snapshot_id,
                    ),
                )
        self.connection.rollback()
        # Failed cross-conversation insert must not erase the valid committed run.
        self.assertEqual(
            self.store.list_cfc_runs(
                self.user_a.user_id, self.conversation_a.conversation_id
            )[0].hawm_snapshot_id,
            snap_a.snapshot_id,
        )

    def test_postgres_nullable_legacy_runs_survive_repeat_schema_bootstrap(self):
        from pro_beta.db_bootstrap import ensure_schema
        legacy = CFCRun(
            run_id=new_id("cfc"),
            conversation_id=self.conversation_a.conversation_id,
            case_id="HAWM_STRUCTURED_CUSTOM",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"decision": "STOP"},
        )
        self.store.add_cfc_run(self.user_a.user_id, legacy)
        ensure_schema(os.environ["PRO_BETA_TEST_DATABASE_URL"])
        self.assertIsNone(
            self.store.list_cfc_runs(
                self.user_a.user_id, self.conversation_a.conversation_id
            )[0].hawm_snapshot_id
        )

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

    def test_postgres_benchmark_run_round_trip(self):
        run = BenchmarkRun(
            benchmark_run_id=new_id("bench"),
            conversation_id=self.conversation_a.conversation_id,
            benchmark_version="CFC_HAWM_NL_CLOSURE_BENCHMARK_V1",
            case_id="B09_NATURAL_LANGUAGE_UNKNOWN_FRESHNESS",
            benchmark_type="FIXED_NL_BENCHMARK_ISOLATED",
            context_boundary="ISOLATED_NO_CONVERSATION_HISTORY_NO_HAWM",
            expected_control_state="CLOSURE_BLOCKED_UNRESOLVED",
            invariant="Unknown freshness must not become stale.",
            mode="STANDARD",
            status="PARTIAL_PROVIDER_FAILURE",
            results=[
                {
                    "provider": "claude",
                    "model": "claude-sonnet-4-5",
                    "text": "No",
                    "elapsed_ms": 100,
                }
            ],
            failed_providers=[
                {
                    "provider": "gemini",
                    "model": "gemini-3.8-flash",
                    "error": "GEMINI_RATE_LIMIT",
                    "elapsed_ms": 20,
                }
            ],
        )
        self.store.add_benchmark_run(self.user_a.user_id, run)
        rows = self.store.list_benchmark_runs(
            self.user_a.user_id, self.conversation_a.conversation_id
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].case_id, run.case_id)
        self.assertEqual(rows[0].status, "PARTIAL_PROVIDER_FAILURE")
        self.assertFalse(rows[0].automatic_semantic_scoring)
        self.assertEqual(rows[0].results[0]["provider"], "claude")
        self.assertEqual(rows[0].failed_providers[0]["error"], "GEMINI_RATE_LIMIT")

    def test_postgres_manual_benchmark_label_upsert(self):
        run = BenchmarkRun(
            benchmark_run_id=new_id("bench"),
            conversation_id=self.conversation_a.conversation_id,
            benchmark_version="CFC_HAWM_NL_CLOSURE_BENCHMARK_V1",
            case_id="B09_NATURAL_LANGUAGE_UNKNOWN_FRESHNESS",
            benchmark_type="FIXED_NL_BENCHMARK_ISOLATED",
            context_boundary="ISOLATED_NO_CONVERSATION_HISTORY_NO_HAWM",
            expected_control_state="CLOSURE_BLOCKED_UNRESOLVED",
            invariant="Unknown freshness must not become stale.",
            mode="STANDARD",
            status="COMPLETE",
            results=[
                {
                    "provider": "claude",
                    "model": "claude-sonnet-4-5",
                    "text": "No",
                    "elapsed_ms": 100,
                }
            ],
            failed_providers=[],
        )
        self.store.add_benchmark_run(self.user_a.user_id, run)
        first = BenchmarkManualLabel(
            label_id=new_id("benchlabel"),
            benchmark_run_id=run.benchmark_run_id,
            provider="claude",
            model="claude-sonnet-4-5",
            label="CONSISTENT",
            note="first",
        )
        self.store.upsert_benchmark_manual_label(self.user_a.user_id, first)
        second = BenchmarkManualLabel(
            label_id=new_id("benchlabel"),
            benchmark_run_id=run.benchmark_run_id,
            provider="claude",
            model="claude-sonnet-4-5",
            label="AMBIGUOUS",
            note="revised",
        )
        self.store.upsert_benchmark_manual_label(self.user_a.user_id, second)
        rows = self.store.list_benchmark_manual_labels(
            self.user_a.user_id, run.benchmark_run_id
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].label, "AMBIGUOUS")
        self.assertEqual(rows[0].note, "revised")

    def test_postgres_user_lists_only_own_workspaces(self):
        rows = self.store.list_workspaces(self.user_a.user_id)
        self.assertEqual([w.workspace_id for w in rows], [self.workspace_a.workspace_id])


if __name__ == "__main__":
    unittest.main(verbosity=2)
