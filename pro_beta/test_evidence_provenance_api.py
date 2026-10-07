from __future__ import annotations

from dataclasses import replace
import copy
import unittest
from unittest.mock import patch

from pro_beta.api import APIError, ProBetaAPI
from pro_beta.auth_boundary import AuthBoundary, VerifiedExternalIdentity
from pro_beta.contracts import UserAccount
from pro_beta.persistence import InMemoryPersistence
from pro_beta.service import ProBetaService


ISSUER = "https://identity.example/"
AUDIENCE = "cfc-hawm-pro-beta"


class FakeVerifier:
    def verify(self, credential: str) -> VerifiedExternalIdentity:
        subjects = {
            "token-a": "provider|a",
            "token-b": "provider|b",
        }
        if credential not in subjects:
            raise RuntimeError("unexpected credential")
        return VerifiedExternalIdentity(
            subject=subjects[credential],
            issuer=ISSUER,
            audience=AUDIENCE,
            provider_verified=True,
        )


def structured_state():
    return {
        "goal": "Layer B assessment",
        "cfc_structured": {
            "conclusion": "POSITIVE",
            "required_independent_supports": 1,
            "provenance_shape": "DISTINCT",
            "independence_authority": "NONE",
            "scope": "EXPECTED",
            "evidence": [
                {"polarity": "POSITIVE", "validity": "CURRENT"},
            ],
        },
    }


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


class EvidenceProvenanceAPITests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryPersistence()
        self.account_a = UserAccount("usr-a", "provider|a", "a@example.com")
        self.account_b = UserAccount("usr-b", "provider|b", "b@example.com")
        self.store.create_user(self.account_a)
        self.store.create_user(self.account_b)

        self.service = ProBetaService(self.store)
        boundary = AuthBoundary(
            self.store,
            expected_issuer=ISSUER,
            expected_audience=AUDIENCE,
        )
        self.api = ProBetaAPI(
            verifier=FakeVerifier(),
            auth_boundary=boundary,
            service=self.service,
        )

        self.workspace_a = self.api.create_workspace(
            "token-a", {"name": "Evidence A"}
        )
        self.conversation_a = self.api.create_conversation(
            "token-a",
            self.workspace_a["workspace_id"],
            {"title": "Evidence A"},
        )
        self.workspace_b = self.api.create_workspace(
            "token-b", {"name": "Evidence B"}
        )
        self.api.create_conversation(
            "token-b",
            self.workspace_b["workspace_id"],
            {"title": "Evidence B"},
        )

    def _save_snapshot(self):
        return self.api.save_hawm_snapshot(
            "token-a",
            self.conversation_a["conversation_id"],
            {
                "state": structured_state(),
                "last_verified_state": "USER_WORKING_STATE",
            },
        )

    def _auth_a(self):
        return self.api._auth("token-a")

    def _register_set(self, snapshot_id):
        return self.service.register_evidence_set(
            self._auth_a(),
            self.conversation_a["conversation_id"],
            snapshot_id,
            evidence_set=evidence_records(),
            missing_evidence=[],
        )

    def _register_provenance(self, snapshot_id):
        for evidence_id, source_id in [("E1", "S1"), ("E2", "S2")]:
            self.service.register_evidence_provenance_receipt(
                self._auth_a(),
                self.conversation_a["conversation_id"],
                snapshot_id,
                evidence_id=evidence_id,
                source_id=source_id,
                status="ESTABLISHED",
            )

    def _register_dependency(self, snapshot_id):
        return self.service.register_evidence_dependency_receipt(
            self._auth_a(),
            self.conversation_a["conversation_id"],
            snapshot_id,
            evidence_ids=["E1", "E2"],
            failure_domains={"E1": "FD1", "E2": "FD2"},
            status="RESOLVED",
        )

    def _bind_baseline_run(self, snapshot_id):
        return self.service.save_cfc_run(
            self._auth_a(),
            self.conversation_a["conversation_id"],
            case_id="LAYER_B_TEST_BINDING_ONLY",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"decision": "STOP"},
            replay_matches_reference=None,
            hawm_snapshot_id=snapshot_id,
        )

    def test_no_registry_fails_closed_after_valid_state_integrity(self):
        snap = self._save_snapshot()

        result = self.api.assess_evidence_provenance(
            "token-a", self.conversation_a["conversation_id"]
        )

        self.assertEqual(result["status"], "EVIDENCE_UNKNOWN")
        self.assertEqual(
            result["reason"],
            "EVIDENCE_SET_REGISTRATION_NOT_FOUND",
        )
        self.assertEqual(result["state_id"], snap["snapshot_id"])
        self.assertEqual(result["state_integrity_status"], "STATE_VALID")
        self.assertTrue(result["read_only"])
        self.assertEqual(
            result["authorization_effect"],
            "DOES_NOT_AUTHORIZE_CLOSURE",
        )

    def test_state_integrity_invalid_blocks_before_registry(self):
        snap = self._save_snapshot()
        current = self.store.hawm_snapshots[snap["snapshot_id"]]
        self.store.hawm_snapshots[snap["snapshot_id"]] = replace(
            current,
            state={"goal": "tampered", "cfc_structured": structured_state()["cfc_structured"]},
        )

        result = self.api.assess_evidence_provenance(
            "token-a", self.conversation_a["conversation_id"]
        )

        self.assertEqual(result["status"], "EVIDENCE_UNKNOWN")
        self.assertEqual(result["reason"], "STATE_INTEGRITY_NOT_VALID")
        self.assertEqual(result["state_integrity_status"], "STATE_INVALID")

    def test_current_snapshot_change_during_assessment_fails_closed(self):
        snap = self._save_snapshot()

        with patch.object(
            self.api,
            "assess_state_integrity",
            return_value={
                "status": "STATE_VALID",
                "snapshot_id": "hawm-newer",
                "state_id": "hawm-newer",
                "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
            },
        ):
            result = self.api.assess_evidence_provenance(
                "token-a", self.conversation_a["conversation_id"]
            )

        self.assertEqual(result["status"], "EVIDENCE_UNKNOWN")
        self.assertEqual(
            result["reason"],
            "CURRENT_SNAPSHOT_CHANGED_DURING_ASSESSMENT",
        )
        self.assertEqual(result["state_id"], snap["snapshot_id"])
        self.assertEqual(result["state_integrity_status"], "STATE_VALID")
        self.assertEqual(
            result["state_integrity_snapshot_id"],
            "hawm-newer",
        )

    def test_missing_dependency_receipt_remains_unknown(self):
        snap = self._save_snapshot()
        self._register_set(snap["snapshot_id"])
        self._register_provenance(snap["snapshot_id"])
        self._bind_baseline_run(snap["snapshot_id"])

        result = self.api.assess_evidence_provenance(
            "token-a", self.conversation_a["conversation_id"]
        )

        self.assertEqual(result["status"], "EVIDENCE_UNKNOWN")
        self.assertEqual(result["evidence"]["provenance_state"], "ESTABLISHED")
        self.assertEqual(result["evidence"]["dependency_state"], "UNKNOWN")
        self.assertEqual(result["evidence"]["drift_state"], "NO_DRIFT")
        self.assertEqual(result["state_integrity_status"], "STATE_VALID")

    def test_no_bound_cfc_baseline_keeps_drift_unresolved(self):
        snap = self._save_snapshot()
        self._register_set(snap["snapshot_id"])
        self._register_provenance(snap["snapshot_id"])
        self._register_dependency(snap["snapshot_id"])

        result = self.api.assess_evidence_provenance(
            "token-a", self.conversation_a["conversation_id"]
        )

        self.assertEqual(result["status"], "EVIDENCE_UNKNOWN")
        self.assertEqual(result["evidence"]["drift_state"], "UNRESOLVED")
        self.assertIn("DRIFT_NOT_CLEAR", result["diagnostics"])

    def test_complete_persisted_path_is_applicable_and_read_only(self):
        snap = self._save_snapshot()
        self._register_set(snap["snapshot_id"])
        self._register_provenance(snap["snapshot_id"])
        self._register_dependency(snap["snapshot_id"])
        self._bind_baseline_run(snap["snapshot_id"])

        before = {
            "snapshots": copy.deepcopy(self.store.hawm_snapshots),
            "identities": copy.deepcopy(self.store.hawm_snapshot_identities),
            "registrations": copy.deepcopy(self.store.evidence_set_registrations),
            "provenance": copy.deepcopy(self.store.evidence_provenance_receipts),
            "dependencies": copy.deepcopy(self.store.evidence_dependency_receipts),
            "runs": copy.deepcopy(self.store.cfc_runs),
        }

        result = self.api.assess_evidence_provenance(
            "token-a", self.conversation_a["conversation_id"]
        )

        self.assertEqual(result["status"], "EVIDENCE_APPLICABLE")
        self.assertEqual(
            result["reason"],
            "EXPLICIT_EVIDENCE_PROVENANCE_STATE_APPLICABLE",
        )
        self.assertEqual(result["state_integrity_status"], "STATE_VALID")
        self.assertEqual(result["registry_source"], "PERSISTED_EVIDENCE_PROVENANCE_REGISTRY")
        self.assertEqual(result["drift_source"], "PERSISTED_CFC_RUN_BOUND_EVIDENCE_DRIFT")
        self.assertTrue(result["read_only"])
        self.assertFalse(result["requires_review"])
        self.assertEqual(
            result["authorization_effect"],
            "DOES_NOT_AUTHORIZE_CLOSURE",
        )

        self.assertEqual(self.store.hawm_snapshots, before["snapshots"])
        self.assertEqual(self.store.hawm_snapshot_identities, before["identities"])
        self.assertEqual(
            self.store.evidence_set_registrations,
            before["registrations"],
        )
        self.assertEqual(
            self.store.evidence_provenance_receipts,
            before["provenance"],
        )
        self.assertEqual(
            self.store.evidence_dependency_receipts,
            before["dependencies"],
        )
        self.assertEqual(self.store.cfc_runs, before["runs"])

    def test_cross_user_read_is_forbidden(self):
        self._save_snapshot()

        with self.assertRaises(APIError) as ctx:
            self.api.assess_evidence_provenance(
                "token-b", self.conversation_a["conversation_id"]
            )

        self.assertEqual(ctx.exception.status, 403)


if __name__ == "__main__":
    unittest.main(verbosity=2)
