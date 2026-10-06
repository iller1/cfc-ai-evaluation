from __future__ import annotations

from dataclasses import replace
import unittest

from pro_beta.api import ProBetaAPI
from pro_beta.auth_boundary import AuthBoundary, VerifiedExternalIdentity
from pro_beta.contracts import HAWMSnapshot, UserAccount
from pro_beta.persistence import InMemoryPersistence
from pro_beta.service import ProBetaService

ISSUER = "https://identity.example/"
AUDIENCE = "cfc-hawm-pro-beta"


class FakeVerifier:
    def verify(self, credential: str) -> VerifiedExternalIdentity:
        return VerifiedExternalIdentity(
            subject="provider|a",
            issuer=ISSUER,
            audience=AUDIENCE,
            provider_verified=True,
        )


class StateIntegrityAdapterTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryPersistence()
        self.account = UserAccount("usr_a", "provider|a", "a@example.com")
        self.store.create_user(self.account)
        boundary = AuthBoundary(
            self.store,
            expected_issuer=ISSUER,
            expected_audience=AUDIENCE,
        )
        self.api = ProBetaAPI(
            verifier=FakeVerifier(),
            auth_boundary=boundary,
            service=ProBetaService(self.store),
        )
        ws = self.api.create_workspace("token-a", {"name": "SI"})
        conv = self.api.create_conversation(
            "token-a", ws["workspace_id"], {"title": "SI"}
        )
        self.conversation_id = conv["conversation_id"]

    def save(self, state):
        return self.api.save_hawm_snapshot(
            "token-a",
            self.conversation_id,
            {"state": state, "last_verified_state": "USER_WORKING_STATE"},
        )

    def test_exact_current_state_is_valid(self):
        snap = self.save({"goal": "exact"})
        result = self.api.assess_state_integrity(
            "token-a", self.conversation_id
        )
        self.assertEqual(result["status"], "STATE_VALID")
        self.assertEqual(result["snapshot_id"], snap["snapshot_id"])
        self.assertEqual(
            result["expectation_source"],
            "PERSISTED_HAWM_SNAPSHOT_IDENTITY",
        )
        self.assertEqual(
            result["authorization_effect"],
            "DOES_NOT_AUTHORIZE_CLOSURE",
        )
        self.assertTrue(result["read_only"])

    def test_legacy_snapshot_without_receipt_is_unresolved(self):
        self.store.add_hawm_snapshot(
            self.account.user_id,
            HAWMSnapshot(
                "hawm_legacy",
                self.conversation_id,
                {"goal": "legacy"},
                "USER_WORKING_STATE",
            ),
        )
        result = self.api.assess_state_integrity(
            "token-a", self.conversation_id
        )
        self.assertEqual(result["status"], "STATE_UNRESOLVED")
        self.assertEqual(
            result["reason"], "SNAPSHOT_IDENTITY_NOT_REGISTERED"
        )

    def test_changed_payload_under_same_snapshot_id_is_invalid(self):
        snap = self.save({"goal": "original"})
        current = self.store.hawm_snapshots[snap["snapshot_id"]]
        self.store.hawm_snapshots[snap["snapshot_id"]] = replace(
            current, state={"goal": "tampered"}
        )
        result = self.api.assess_state_integrity(
            "token-a", self.conversation_id
        )
        self.assertEqual(result["status"], "STATE_INVALID")
        self.assertEqual(
            result["reason"], "SNAPSHOT_FINGERPRINT_MISMATCH"
        )

    def test_adversarial_acceptance_api_passes_from_server_derived_state(self):
        self.save({"goal": "first"})
        snap = self.save({"goal": "second"})
        before = self.store.hawm_snapshots[snap["snapshot_id"]]

        result = self.api.assess_state_integrity_adversarial_acceptance(
            "token-a", self.conversation_id
        )

        self.assertEqual(result["status"], "ACCEPTANCE_PASS")
        self.assertEqual(result["baseline_status"], "STATE_VALID")
        self.assertTrue(result["read_only"])
        self.assertEqual(result["persistence_actions"], [])
        self.assertFalse(result["cfc_executed"])
        self.assertEqual(len(result["cases"]), 6)
        self.assertTrue(all(item["pass"] for item in result["cases"]))
        self.assertEqual(
            self.store.hawm_snapshots[snap["snapshot_id"]],
            before,
        )

    def test_adversarial_acceptance_legacy_snapshot_is_unresolved(self):
        self.store.add_hawm_snapshot(
            self.account.user_id,
            HAWMSnapshot(
                "hawm_legacy_acceptance",
                self.conversation_id,
                {"goal": "legacy"},
                "USER_WORKING_STATE",
            ),
        )

        result = self.api.assess_state_integrity_adversarial_acceptance(
            "token-a", self.conversation_id
        )

        self.assertEqual(result["status"], "ACCEPTANCE_UNRESOLVED")
        self.assertEqual(
            result["reason"], "SNAPSHOT_IDENTITY_NOT_REGISTERED"
        )
        self.assertTrue(result["read_only"])
        self.assertFalse(result["cfc_executed"])

    def test_predecessor_is_derived_from_persisted_history(self):
        first = self.save({"goal": "first"})
        second = self.save({"goal": "second"})
        receipt = self.store.hawm_snapshot_identities[second["snapshot_id"]]
        self.store.hawm_snapshot_identities[second["snapshot_id"]] = replace(
            receipt, previous_state_id="hawm_wrong"
        )
        result = self.api.assess_state_integrity(
            "token-a", self.conversation_id
        )
        self.assertEqual(result["status"], "STATE_UNRESOLVED")
        self.assertEqual(result["reason"], "PREDECESSOR_MISMATCH")
        self.assertEqual(result["previous_state_id"], first["snapshot_id"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
