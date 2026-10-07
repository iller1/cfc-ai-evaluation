from __future__ import annotations

import unittest

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
    EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION,
    ProBetaService,
)


def evidence_records():
    return [
        {
            "evidence_id": "E1",
            "source_id": "S1",
            "validity": "CURRENT",
            "scope_status": "MATCH",
            "failure_domain_id": "FD1",
        },
        {
            "evidence_id": "E2",
            "source_id": "S2",
            "validity": "CURRENT",
            "scope_status": "MATCH",
            "failure_domain_id": "FD2",
        },
    ]


class EvidenceProvenanceRegistryTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryPersistence()
        self.user_a = UserAccount(new_id("usr"), "auth|evidence-a", "a@example.com")
        self.user_b = UserAccount(new_id("usr"), "auth|evidence-b", "b@example.com")
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

    def save_snapshot(self):
        return self.service.save_hawm_snapshot(
            self.auth_a,
            self.conversation_a.conversation_id,
            {"goal": "registered evidence state"},
            "USER_WORKING_STATE",
        )

    def register_set(self, snapshot_id):
        return self.service.register_evidence_set(
            self.auth_a,
            self.conversation_a.conversation_id,
            snapshot_id,
            evidence_set=evidence_records(),
            missing_evidence=[],
        )

    def test_registration_binds_exact_snapshot_and_state(self):
        snapshot = self.save_snapshot()

        registration = self.register_set(snapshot.snapshot_id)

        self.assertEqual(registration.snapshot_id, snapshot.snapshot_id)
        self.assertEqual(registration.state_id, snapshot.snapshot_id)
        self.assertEqual(
            registration.conversation_id,
            self.conversation_a.conversation_id,
        )
        self.assertEqual(
            registration.adapter_version,
            EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION,
        )
        self.assertEqual(registration.evidence_set, evidence_records())

    def test_legacy_snapshot_without_identity_anchor_cannot_register(self):
        legacy = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=self.conversation_a.conversation_id,
            state={"goal": "legacy"},
            last_verified_state="USER_WORKING_STATE",
        )
        self.store.add_hawm_snapshot(self.user_a.user_id, legacy)

        with self.assertRaises(NotFoundError):
            self.register_set(legacy.snapshot_id)

    def test_malformed_evidence_record_fails_closed(self):
        snapshot = self.save_snapshot()
        malformed = evidence_records()
        del malformed[0]["source_id"]

        with self.assertRaisesRegex(
            ValueError,
            "EVIDENCE_RECORD_SCHEMA_INVALID",
        ):
            self.service.register_evidence_set(
                self.auth_a,
                self.conversation_a.conversation_id,
                snapshot.snapshot_id,
                evidence_set=malformed,
                missing_evidence=[],
            )

    def test_provenance_receipt_must_match_registered_source(self):
        snapshot = self.save_snapshot()
        self.register_set(snapshot.snapshot_id)

        with self.assertRaisesRegex(
            ValueError,
            "EVIDENCE_PROVENANCE_SOURCE_MISMATCH",
        ):
            self.service.register_evidence_provenance_receipt(
                self.auth_a,
                self.conversation_a.conversation_id,
                snapshot.snapshot_id,
                evidence_id="E1",
                source_id="S-WRONG",
                status="ESTABLISHED",
            )

    def test_exact_provenance_receipts_round_trip(self):
        snapshot = self.save_snapshot()
        self.register_set(snapshot.snapshot_id)

        first = self.service.register_evidence_provenance_receipt(
            self.auth_a,
            self.conversation_a.conversation_id,
            snapshot.snapshot_id,
            evidence_id="E1",
            source_id="S1",
            status="ESTABLISHED",
        )
        second = self.service.register_evidence_provenance_receipt(
            self.auth_a,
            self.conversation_a.conversation_id,
            snapshot.snapshot_id,
            evidence_id="E2",
            source_id="S2",
            status="ESTABLISHED",
        )

        rows = self.service.list_evidence_provenance_receipts(
            self.auth_a,
            self.conversation_a.conversation_id,
            snapshot.snapshot_id,
        )

        self.assertEqual(
            {row.receipt_id for row in rows},
            {first.receipt_id, second.receipt_id},
        )
        self.assertTrue(
            all(row.state_id == snapshot.snapshot_id for row in rows)
        )

    def test_dependency_receipt_must_cover_exact_set_when_resolved(self):
        snapshot = self.save_snapshot()
        self.register_set(snapshot.snapshot_id)

        with self.assertRaisesRegex(
            ValueError,
            "RESOLVED_DEPENDENCY_COVERAGE_MISMATCH",
        ):
            self.service.register_evidence_dependency_receipt(
                self.auth_a,
                self.conversation_a.conversation_id,
                snapshot.snapshot_id,
                evidence_ids=["E1"],
                failure_domains={"E1": "FD1"},
                status="RESOLVED",
            )

    def test_exact_dependency_receipt_round_trip(self):
        snapshot = self.save_snapshot()
        self.register_set(snapshot.snapshot_id)

        receipt = self.service.register_evidence_dependency_receipt(
            self.auth_a,
            self.conversation_a.conversation_id,
            snapshot.snapshot_id,
            evidence_ids=["E1", "E2"],
            failure_domains={"E1": "FD1", "E2": "FD2"},
            status="RESOLVED",
        )
        loaded = self.service.get_evidence_dependency_receipt(
            self.auth_a,
            self.conversation_a.conversation_id,
            snapshot.snapshot_id,
        )

        self.assertEqual(loaded.receipt_id, receipt.receipt_id)
        self.assertEqual(loaded.state_id, snapshot.snapshot_id)
        self.assertEqual(
            loaded.failure_domains,
            {"E1": "FD1", "E2": "FD2"},
        )

    def test_duplicate_registration_is_rejected(self):
        snapshot = self.save_snapshot()
        self.register_set(snapshot.snapshot_id)

        with self.assertRaisesRegex(
            ValueError,
            "EVIDENCE_SET_REGISTRATION_ALREADY_EXISTS",
        ):
            self.register_set(snapshot.snapshot_id)

    def test_registry_reads_are_conversation_owned(self):
        snapshot = self.save_snapshot()
        self.register_set(snapshot.snapshot_id)

        with self.assertRaises(OwnershipError):
            self.service.get_evidence_set_registration(
                self.auth_b,
                self.conversation_a.conversation_id,
                snapshot.snapshot_id,
            )
        with self.assertRaises(OwnershipError):
            self.service.list_evidence_provenance_receipts(
                self.auth_b,
                self.conversation_a.conversation_id,
                snapshot.snapshot_id,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
