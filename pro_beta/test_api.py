from __future__ import annotations

import unittest

from pro_beta.api import (
    APIError,
    MissingIdentityVerifier,
    ProBetaAPI,
)
from pro_beta.auth_boundary import (
    AuthBoundary,
    AuthenticationError,
    VerifiedExternalIdentity,
)
from pro_beta.contracts import UserAccount
from pro_beta.persistence import InMemoryPersistence
from pro_beta.service import ProBetaService


ISSUER = "https://identity.example/"
AUDIENCE = "cfc-hawm-pro-beta"


class FakeVerifier:
    def __init__(self, identities):
        self.identities = identities

    def verify(self, credential: str) -> VerifiedExternalIdentity:
        try:
            return self.identities[credential]
        except KeyError as exc:
            raise AuthenticationError("CREDENTIAL_INVALID") from exc


class ProBetaAPITests(unittest.TestCase):
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

        verifier = FakeVerifier(
            {
                "token-a": VerifiedExternalIdentity(
                    subject="provider|a",
                    issuer=ISSUER,
                    audience=AUDIENCE,
                    provider_verified=True,
                ),
                "token-b": VerifiedExternalIdentity(
                    subject="provider|b",
                    issuer=ISSUER,
                    audience=AUDIENCE,
                    provider_verified=True,
                ),
                "token-new": VerifiedExternalIdentity(
                    subject="provider|new",
                    issuer=ISSUER,
                    audience=AUDIENCE,
                    email="new@example.com",
                    email_verified=True,
                    provider_verified=True,
                ),
            }
        )
        boundary = AuthBoundary(
            self.store,
            expected_issuer=ISSUER,
            expected_audience=AUDIENCE,
        )
        self.api = ProBetaAPI(
            verifier=verifier,
            auth_boundary=boundary,
            service=ProBetaService(self.store),
        )

    def test_missing_credential_is_401(self):
        with self.assertRaises(APIError) as ctx:
            self.api.list_workspaces("")
        self.assertEqual(ctx.exception.status, 401)
        self.assertEqual(ctx.exception.code, "AUTH_CREDENTIAL_REQUIRED")

    def test_invalid_credential_is_401(self):
        with self.assertRaises(APIError) as ctx:
            self.api.list_workspaces("bad-token")
        self.assertEqual(ctx.exception.status, 401)
        self.assertEqual(ctx.exception.code, "CREDENTIAL_INVALID")

    def test_unconfigured_verifier_fails_closed(self):
        boundary = AuthBoundary(
            self.store,
            expected_issuer=ISSUER,
            expected_audience=AUDIENCE,
        )
        api = ProBetaAPI(
            verifier=MissingIdentityVerifier(),
            auth_boundary=boundary,
            service=ProBetaService(self.store),
        )
        with self.assertRaises(APIError) as ctx:
            api.list_workspaces("anything")
        self.assertEqual(ctx.exception.status, 401)
        self.assertEqual(
            ctx.exception.code, "IDENTITY_VERIFIER_NOT_CONFIGURED"
        )

    def test_explicit_provisioning_creates_verified_account(self):
        result = self.api.provision_account("token-new")
        self.assertTrue(result["created"])
        self.assertEqual(
            result["account"]["external_auth_subject"], "provider|new"
        )
        self.assertEqual(result["account"]["email"], "new@example.com")

        second = self.api.provision_account("token-new")
        self.assertFalse(second["created"])
        self.assertEqual(
            second["account"]["user_id"], result["account"]["user_id"]
        )

    def test_normal_api_still_rejects_unknown_subject_until_provisioned(self):
        fresh = InMemoryPersistence()
        verifier = FakeVerifier(
            {
                "token-new": VerifiedExternalIdentity(
                    subject="provider|new",
                    issuer=ISSUER,
                    audience=AUDIENCE,
                    provider_verified=True,
                )
            }
        )
        api = ProBetaAPI(
            verifier=verifier,
            auth_boundary=AuthBoundary(
                fresh,
                expected_issuer=ISSUER,
                expected_audience=AUDIENCE,
            ),
            service=ProBetaService(fresh),
        )
        with self.assertRaises(APIError) as ctx:
            api.list_workspaces("token-new")
        self.assertEqual(ctx.exception.code, "ACCOUNT_NOT_PROVISIONED")

    def test_user_cannot_select_another_user_by_payload(self):
        created = self.api.create_workspace(
            "token-a",
            {"name": "A workspace", "user_id": "usr_b"},
        )
        self.assertEqual(created["user_id"], "usr_a")

    def test_workspace_conversation_and_user_message_round_trip(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "Project A"}
        )
        conversations = self.api.list_conversations(
            "token-a", workspace["workspace_id"]
        )
        self.assertEqual(conversations, [])

        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "First chat"},
        )
        conversations = self.api.list_conversations(
            "token-a", workspace["workspace_id"]
        )
        self.assertEqual(
            [c["conversation_id"] for c in conversations],
            [conversation["conversation_id"]],
        )

        message = self.api.persist_user_message(
            "token-a",
            conversation["conversation_id"],
            content="hello",
            mode="STANDARD",
        )
        self.assertEqual(message["authority"], "USER_INPUT")
        self.assertEqual(message["cfc_status"], "NOT_APPLICABLE")
        rows = self.api.list_messages(
            "token-a", conversation["conversation_id"]
        )
        self.assertEqual([m["content"] for m in rows], ["hello"])

    def test_hawm_snapshot_round_trip(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "HAWM"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "State"},
        )
        saved = self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {
                    "goal": "finish task",
                    "task": "test persistence",
                    "unresolved": "one point",
                    "next_action": "verify reload",
                },
                "last_verified_state": "USER_WORKING_STATE",
            },
        )
        self.assertEqual(saved["state"]["goal"], "finish task")
        latest = self.api.latest_hawm_snapshot(
            "token-a", conversation["conversation_id"]
        )
        self.assertEqual(latest["snapshot_id"], saved["snapshot_id"])
        self.assertEqual(
            latest["last_verified_state"], "USER_WORKING_STATE"
        )

    def test_prepared_cfc_run_is_separate_and_persisted(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "CFC"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Prepared"},
        )
        run = self.api.run_prepared_cfc_case(
            "token-a",
            conversation["conversation_id"],
            {"case_id": "CASE_01_UNRESOLVED_POSITIVE"},
        )
        self.assertEqual(run["controller_anchor"], "0.2.90rc1")
        self.assertEqual(
            run["boundary"],
            "PREPARED_SYNTHETIC_FIXTURE_NOT_CONVERSATION_ANALYSIS",
        )
        self.assertEqual(run["presentation"]["decision"], "STOP")
        self.assertTrue(run["replay_matches_reference"])

        latest = self.api.latest_cfc_run(
            "token-a", conversation["conversation_id"]
        )
        self.assertEqual(latest["run_id"], run["run_id"])
        self.assertEqual(
            latest["case_id"], "CASE_01_UNRESOLVED_POSITIVE"
        )

    def test_structured_hawm_cfc_bridge_uses_only_explicit_state(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "HAWM CFC"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Structured bridge"},
        )
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {
                    "goal": "free text ignored by CFC mapping",
                    "claims": "also ignored",
                    "cfc_structured": {
                        "conclusion": "POSITIVE",
                        "required_independent_supports": 1,
                        "provenance_shape": "DISTINCT",
                        "independence_authority": "NONE",
                        "scope": "EXPECTED",
                        "evidence": [
                            {"polarity": "POSITIVE", "validity": "CURRENT"}
                        ],
                    },
                },
                "last_verified_state": "USER_WORKING_STATE",
            },
        )
        run = self.api.run_structured_hawm_cfc(
            "token-a", conversation["conversation_id"]
        )
        self.assertEqual(run["case_id"], "HAWM_STRUCTURED_CUSTOM")
        self.assertEqual(run["controller_anchor"], "0.2.90rc1")
        self.assertEqual(
            run["boundary"],
            "STRUCTURED_HAWM_FIELDS_ONLY_NO_NATURAL_LANGUAGE_INFERENCE",
        )
        self.assertEqual(run["mapped_input"]["conclusion"], "POSITIVE")
        self.assertEqual(run["presentation"]["decision"], "ALLOW")
        self.assertNotIn("goal", run["mapped_input"])
        self.assertIsNone(run["replay_matches_reference"])

    def test_structured_hawm_cfc_blocks_when_required_support_is_missing(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "HAWM CFC negative"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Insufficient support"},
        )
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {
                    "cfc_structured": {
                        "conclusion": "POSITIVE",
                        "required_independent_supports": 2,
                        "provenance_shape": "DISTINCT",
                        "independence_authority": "NONE",
                        "scope": "EXPECTED",
                        "evidence": [
                            {"polarity": "POSITIVE", "validity": "CURRENT"}
                        ],
                    }
                },
                "last_verified_state": "USER_WORKING_STATE",
            },
        )
        run = self.api.run_structured_hawm_cfc(
            "token-a", conversation["conversation_id"]
        )
        self.assertEqual(run["controller_anchor"], "0.2.90rc1")
        self.assertEqual(run["presentation"]["claim_state"], "SUPPORTED")
        self.assertEqual(run["presentation"]["decision"], "STOP")
        self.assertFalse(run["controller_result"]["control_closure"])
        self.assertIn(
            "claim_specific_support_policy_valid",
            run["presentation"]["false_gates"],
        )

    def test_structured_hawm_cfc_requires_explicit_mapping(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "HAWM CFC missing"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "No structured state"},
        )
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {"goal": "free text only"},
                "last_verified_state": "USER_WORKING_STATE",
            },
        )
        with self.assertRaises(APIError) as ctx:
            self.api.run_structured_hawm_cfc(
                "token-a", conversation["conversation_id"]
            )
        self.assertEqual(
            ctx.exception.code, "HAWM_CFC_STRUCTURED_STATE_REQUIRED"
        )

    def test_cross_user_conversation_access_returns_403(self):
        workspace_b = self.api.create_workspace(
            "token-b", {"name": "B workspace"}
        )
        conversation_b = self.api.create_conversation(
            "token-b",
            workspace_b["workspace_id"],
            {"title": "Private"},
        )
        with self.assertRaises(APIError) as ctx:
            self.api.get_conversation(
                "token-a", conversation_b["conversation_id"]
            )
        self.assertEqual(ctx.exception.status, 403)

    def test_persisted_model_reply_remains_unchecked(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "A workspace"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Chat"},
        )
        reply = self.api.persist_model_reply(
            "token-a",
            conversation["conversation_id"],
            content="model answer",
            mode="STANDARD",
        )
        self.assertEqual(reply["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(reply["cfc_status"], "NOT_CONNECTED_C2")

    def test_wrong_owner_cannot_list_messages(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "A workspace"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Chat"},
        )
        with self.assertRaises(APIError) as ctx:
            self.api.list_messages(
                "token-b", conversation["conversation_id"]
            )
        self.assertEqual(ctx.exception.status, 403)


if __name__ == "__main__":
    unittest.main(verbosity=2)
