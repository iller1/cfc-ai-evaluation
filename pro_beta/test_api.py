from __future__ import annotations

import unittest
from unittest.mock import patch

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
from pro_beta.model_provider import ProviderError


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

    def test_structured_hawm_cfc_quarantines_active_conflict(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "HAWM CFC conflict"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Active conflict"},
        )
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {
                    "cfc_structured": {
                        "conclusion": "POSITIVE",
                        "required_independent_supports": 1,
                        "provenance_shape": "DISTINCT",
                        "independence_authority": "NONE",
                        "scope": "EXPECTED",
                        "evidence": [
                            {"polarity": "POSITIVE", "validity": "CURRENT"},
                            {"polarity": "NEGATIVE", "validity": "CURRENT"},
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
        self.assertEqual(run["presentation"]["claim_state"], "QUARANTINED")
        self.assertEqual(run["presentation"]["decision"], "STOP")
        self.assertFalse(run["controller_result"]["control_closure"])
        self.assertIn(
            "global_consistency_valid",
            run["presentation"]["false_gates"],
        )
        self.assertEqual(
            run["presentation"]["reason"],
            "direct contradiction",
        )

    def test_structured_hawm_cfc_stale_evidence_is_unresolved(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "HAWM CFC stale"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Stale evidence"},
        )
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {
                    "cfc_structured": {
                        "conclusion": "POSITIVE",
                        "required_independent_supports": 1,
                        "provenance_shape": "DISTINCT",
                        "independence_authority": "NONE",
                        "scope": "EXPECTED",
                        "evidence": [
                            {"polarity": "POSITIVE", "validity": "STALE"}
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
        self.assertEqual(run["presentation"]["claim_state"], "UNRESOLVED")
        self.assertEqual(run["presentation"]["decision"], "STOP")
        self.assertFalse(run["controller_result"]["control_closure"])
        self.assertIn(
            "decision_support_closure_valid",
            run["presentation"]["false_gates"],
        )

    def test_structured_hawm_cfc_wrong_scope_blocks_closure(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "HAWM CFC scope"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Wrong scope"},
        )
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {
                    "cfc_structured": {
                        "conclusion": "POSITIVE",
                        "required_independent_supports": 1,
                        "provenance_shape": "DISTINCT",
                        "independence_authority": "NONE",
                        "scope": "WRONG",
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
        self.assertEqual(run["presentation"]["claim_state"], "VERIFIED")
        self.assertEqual(run["presentation"]["decision"], "STOP")
        self.assertFalse(run["controller_result"]["control_closure"])
        self.assertIn(
            "scope_adequacy_valid",
            run["presentation"]["false_gates"],
        )

    def test_structured_hawm_cfc_independence_authority_ab(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "HAWM CFC independence"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Independence A/B"},
        )

        base_state = {
            "conclusion": "POSITIVE",
            "required_independent_supports": 2,
            "provenance_shape": "DISTINCT",
            "scope": "EXPECTED",
            "evidence": [
                {"polarity": "POSITIVE", "validity": "CURRENT"},
                {"polarity": "POSITIVE", "validity": "CURRENT"},
            ],
        }

        without_authority = dict(base_state)
        without_authority["independence_authority"] = "NONE"
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {"cfc_structured": without_authority},
                "last_verified_state": "USER_WORKING_STATE",
            },
        )
        run_without = self.api.run_structured_hawm_cfc(
            "token-a", conversation["conversation_id"]
        )
        self.assertEqual(run_without["presentation"]["decision"], "STOP")
        self.assertFalse(run_without["controller_result"]["control_closure"])
        self.assertIn(
            "claim_specific_support_policy_valid",
            run_without["presentation"]["false_gates"],
        )
        self.assertIn(
            "support_set_common_mode_coverage_valid",
            run_without["presentation"]["false_gates"],
        )

        with_authority = dict(base_state)
        with_authority["independence_authority"] = "VERIFIED"
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {"cfc_structured": with_authority},
                "last_verified_state": "USER_WORKING_STATE",
            },
        )
        run_with = self.api.run_structured_hawm_cfc(
            "token-a", conversation["conversation_id"]
        )
        self.assertEqual(run_with["presentation"]["claim_state"], "VERIFIED")
        self.assertEqual(run_with["presentation"]["decision"], "ALLOW")
        self.assertTrue(run_with["controller_result"]["control_closure"])

    def test_structured_hawm_cfc_shared_lineage_blocks_two_supports(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "HAWM CFC shared lineage"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Shared lineage"},
        )
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {
                    "cfc_structured": {
                        "conclusion": "POSITIVE",
                        "required_independent_supports": 2,
                        "provenance_shape": "SHARED_LINEAGE",
                        "independence_authority": "NONE",
                        "scope": "EXPECTED",
                        "evidence": [
                            {"polarity": "POSITIVE", "validity": "CURRENT"},
                            {"polarity": "POSITIVE", "validity": "CURRENT"},
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

    def test_audit_report_export_preserves_boundaries(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "Audit"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Audit conversation"},
        )
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {
                    "goal": "preserve state",
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
        self.api.run_structured_hawm_cfc(
            "token-a", conversation["conversation_id"]
        )

        exported = self.api.create_audit_report(
            "token-a", conversation["conversation_id"]
        )
        record = exported["report_record"]
        document = exported["document"]
        markdown = exported["markdown"]

        self.assertEqual(record["status"], "GENERATED_JSON_MARKDOWN")
        self.assertIsNone(record["artifact_path"])
        self.assertEqual(
            document["report_version"], "HAWM_CFC_AUDIT_REPORT_V1"
        )
        self.assertEqual(
            document["boundaries"]["ordinary_model_reply"],
            "MODEL_REPLY_UNCHECKED",
        )
        self.assertEqual(
            document["boundaries"]["ordinary_model_cfc"],
            "NOT_CONNECTED_C2",
        )
        self.assertEqual(
            document["boundaries"]["cfc_bridge"],
            "STRUCTURED_HAWM_FIELDS_ONLY_NO_NATURAL_LANGUAGE_INFERENCE",
        )
        self.assertEqual(
            document["hawm_snapshot"]["state"]["goal"],
            "preserve state",
        )
        self.assertEqual(
            document["cfc_run"]["presentation"]["decision"],
            "ALLOW",
        )
        self.assertIn("Raw frozen-controller result", markdown)
        self.assertIn("MODEL_REPLY_UNCHECKED", markdown)
        self.assertIn("does not turn free-text HAWM content", markdown)

    def test_audit_report_requires_hawm_or_cfc(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "Empty audit"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Empty"},
        )
        with self.assertRaises(APIError) as ctx:
            self.api.create_audit_report(
                "token-a", conversation["conversation_id"]
            )
        self.assertEqual(ctx.exception.code, "HAWM_OR_CFC_REQUIRED")

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

    def test_byok_openai_chat_persists_only_messages_not_key(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "BYOK"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "OpenAI"},
        )
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {"goal": "answer carefully"},
                "last_verified_state": "USER_WORKING_STATE",
            },
        )

        with patch(
            "pro_beta.model_provider.openai_call",
            return_value={
                "text": "model answer",
                "finish_reason": "STOP",
                "truncated": False,
                "provider": "openai",
                "model": "gpt-5.6-terra",
                "mode": "STANDARD",
                "authority": "MODEL_REPLY_UNCHECKED",
                "cfc_status": "NOT_CONNECTED_C2",
            },
        ) as mocked:
            result = self.api.chat_with_openai(
                "token-a",
                conversation["conversation_id"],
                {
                    "text": "hello",
                    "api_key": "secret-test-key",
                    "model": "gpt-5.6-terra",
                    "mode": "STANDARD",
                },
            )

        self.assertFalse(result["api_key_persisted"])
        self.assertEqual(result["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(result["cfc_status"], "NOT_CONNECTED_C2")
        rows = self.api.list_messages(
            "token-a", conversation["conversation_id"]
        )
        self.assertEqual([row["content"] for row in rows], ["hello", "model answer"])
        self.assertEqual(rows[1]["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(rows[1]["cfc_status"], "NOT_CONNECTED_C2")
        self.assertEqual(rows[1]["provider"], "openai")
        self.assertEqual(rows[1]["model"], "gpt-5.6-terra")
        self.assertNotIn("secret-test-key", repr(rows))
        call = mocked.call_args.kwargs
        self.assertEqual(call["api_key"], "secret-test-key")
        self.assertEqual(call["hawm_state"]["goal"], "answer carefully")

    def test_byok_claude_chat_persists_only_messages_not_key(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "BYOK"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Claude"},
        )
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {"goal": "answer carefully"},
                "last_verified_state": "USER_WORKING_STATE",
            },
        )

        with patch(
            "pro_beta.model_provider.claude_call",
            return_value={
                "text": "model answer",
                "finish_reason": "STOP",
                "truncated": False,
                "provider": "claude",
                "model": "claude-sonnet-4-5",
                "mode": "STANDARD",
                "authority": "MODEL_REPLY_UNCHECKED",
                "cfc_status": "NOT_CONNECTED_C2",
            },
        ) as mocked:
            result = self.api.chat_with_claude(
                "token-a",
                conversation["conversation_id"],
                {
                    "text": "hello",
                    "api_key": "secret-test-key",
                    "model": "claude-sonnet-4-5",
                    "mode": "STANDARD",
                },
            )

        self.assertFalse(result["api_key_persisted"])
        self.assertEqual(result["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(result["cfc_status"], "NOT_CONNECTED_C2")
        rows = self.api.list_messages(
            "token-a", conversation["conversation_id"]
        )
        self.assertEqual([row["content"] for row in rows], ["hello", "model answer"])
        self.assertEqual(rows[1]["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(rows[1]["cfc_status"], "NOT_CONNECTED_C2")
        self.assertEqual(rows[1]["provider"], "claude")
        self.assertEqual(rows[1]["model"], "claude-sonnet-4-5")
        self.assertNotIn("secret-test-key", repr(rows))
        call = mocked.call_args.kwargs
        self.assertEqual(call["api_key"], "secret-test-key")
        self.assertEqual(call["hawm_state"]["goal"], "answer carefully")

    def test_byok_gemini_chat_persists_only_messages_not_key(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "BYOK"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Gemini"},
        )
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {"goal": "answer carefully"},
                "last_verified_state": "USER_WORKING_STATE",
            },
        )

        with patch(
            "pro_beta.model_provider.gemini_call",
            return_value={
                "text": "model answer",
                "finish_reason": "STOP",
                "truncated": False,
                "provider": "gemini",
                "model": "gemini-3.8-flash",
                "mode": "STANDARD",
                "authority": "MODEL_REPLY_UNCHECKED",
                "cfc_status": "NOT_CONNECTED_C2",
            },
        ) as mocked:
            result = self.api.chat_with_gemini(
                "token-a",
                conversation["conversation_id"],
                {
                    "text": "hello",
                    "api_key": "secret-test-key",
                    "model": "gemini-3.8-flash",
                    "mode": "STANDARD",
                },
            )

        self.assertFalse(result["api_key_persisted"])
        self.assertEqual(result["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(result["cfc_status"], "NOT_CONNECTED_C2")
        rows = self.api.list_messages(
            "token-a", conversation["conversation_id"]
        )
        self.assertEqual([row["content"] for row in rows], ["hello", "model answer"])
        self.assertEqual(rows[1]["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(rows[1]["cfc_status"], "NOT_CONNECTED_C2")
        self.assertEqual(rows[1]["provider"], "gemini")
        self.assertEqual(rows[1]["model"], "gemini-3.8-flash")
        self.assertNotIn("secret-test-key", repr(rows))
        call = mocked.call_args.kwargs
        self.assertEqual(call["api_key"], "secret-test-key")
        self.assertEqual(call["hawm_state"]["goal"], "answer carefully")

    def test_compare_models_uses_same_context_and_persists_one_prompt(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "Compare"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Three models"},
        )
        self.api.save_hawm_snapshot(
            "token-a",
            conversation["conversation_id"],
            {
                "state": {"goal": "compare fairly"},
                "last_verified_state": "USER_WORKING_STATE",
            },
        )

        gemini_result = {
            "text": "gemini answer",
            "finish_reason": "STOP",
            "truncated": False,
            "provider": "gemini",
            "model": "gemini-3.8-flash",
            "mode": "STANDARD",
            "authority": "MODEL_REPLY_UNCHECKED",
            "cfc_status": "NOT_CONNECTED_C2",
        }
        claude_result = {
            "text": "claude answer",
            "finish_reason": "STOP",
            "truncated": False,
            "provider": "claude",
            "model": "claude-sonnet-4-5",
            "mode": "STANDARD",
            "authority": "MODEL_REPLY_UNCHECKED",
            "cfc_status": "NOT_CONNECTED_C2",
        }
        openai_result = {
            "text": "openai answer",
            "finish_reason": "completed",
            "truncated": False,
            "provider": "openai",
            "model": "gpt-5.6-terra",
            "mode": "STANDARD",
            "authority": "MODEL_REPLY_UNCHECKED",
            "cfc_status": "NOT_CONNECTED_C2",
        }

        with patch(
            "pro_beta.model_provider.gemini_call",
            return_value=gemini_result,
        ) as gemini_mock, patch(
            "pro_beta.model_provider.claude_call",
            return_value=claude_result,
        ) as claude_mock, patch(
            "pro_beta.model_provider.openai_call",
            return_value=openai_result,
        ) as openai_mock:
            result = self.api.compare_models(
                "token-a",
                conversation["conversation_id"],
                {
                    "text": "same prompt",
                    "mode": "STANDARD",
                    "gemini_api_key": "g-key",
                    "claude_api_key": "c-key",
                    "openai_api_key": "o-key",
                    "gemini_model": "gemini-3.8-flash",
                    "claude_model": "claude-sonnet-4-5",
                    "openai_model": "gpt-5.6-terra",
                },
            )

        self.assertEqual(
            result["benchmark_type"],
            "SAME_PROMPT_SAME_HISTORY_SAME_HAWM",
        )
        self.assertFalse(result["api_keys_persisted"])
        self.assertEqual(result["authority"], "MODEL_REPLY_UNCHECKED")
        self.assertEqual(result["cfc_status"], "NOT_CONNECTED_C2")
        self.assertEqual(
            [row["provider"] for row in result["results"]],
            ["gemini", "claude", "openai"],
        )
        for row in result["results"]:
            self.assertIn("elapsed_ms", row)

        rows = self.api.list_messages(
            "token-a", conversation["conversation_id"]
        )
        self.assertEqual(
            [row["content"] for row in rows],
            ["same prompt", "gemini answer", "claude answer", "openai answer"],
        )
        self.assertEqual(
            [row["provider"] for row in rows[1:]],
            ["gemini", "claude", "openai"],
        )
        self.assertNotIn("g-key", repr(rows))
        self.assertNotIn("c-key", repr(rows))
        self.assertNotIn("o-key", repr(rows))

        calls = [
            gemini_mock.call_args.kwargs,
            claude_mock.call_args.kwargs,
            openai_mock.call_args.kwargs,
        ]
        for call in calls:
            self.assertEqual(call["text"], "same prompt")
            self.assertEqual(call["mode"], "STANDARD")
            self.assertEqual(call["history"], [])
            self.assertEqual(call["hawm_state"]["goal"], "compare fairly")

    def test_compare_models_keeps_partial_results_when_one_provider_fails(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "Compare partial"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Provider outage"},
        )

        with patch(
            "pro_beta.model_provider.gemini_call",
            side_effect=ProviderError("GEMINI_HTTP_503"),
        ), patch(
            "pro_beta.model_provider.claude_call",
            return_value={
                "text": "claude answer",
                "finish_reason": "STOP",
                "truncated": False,
                "provider": "claude",
                "model": "claude-sonnet-4-5",
                "mode": "STANDARD",
                "authority": "MODEL_REPLY_UNCHECKED",
                "cfc_status": "NOT_CONNECTED_C2",
            },
        ), patch(
            "pro_beta.model_provider.openai_call",
            return_value={
                "text": "openai answer",
                "finish_reason": "completed",
                "truncated": False,
                "provider": "openai",
                "model": "gpt-5.6-terra",
                "mode": "STANDARD",
                "authority": "MODEL_REPLY_UNCHECKED",
                "cfc_status": "NOT_CONNECTED_C2",
            },
        ):
            result = self.api.compare_models(
                "token-a",
                conversation["conversation_id"],
                {
                    "text": "same prompt",
                    "mode": "STANDARD",
                    "gemini_api_key": "g-key",
                    "claude_api_key": "c-key",
                    "openai_api_key": "o-key",
                },
            )

        self.assertEqual(result["benchmark_status"], "PARTIAL_PROVIDER_FAILURE")
        self.assertEqual(
            [row["provider"] for row in result["results"]],
            ["claude", "openai"],
        )
        self.assertEqual(result["failed_providers"][0]["provider"], "gemini")
        self.assertEqual(result["failed_providers"][0]["error"], "GEMINI_HTTP_503")
        rows = self.api.list_messages(
            "token-a", conversation["conversation_id"]
        )
        self.assertEqual(
            [row["content"] for row in rows],
            ["same prompt", "claude answer", "openai answer"],
        )

    def test_compare_models_requires_all_three_keys(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "Compare missing"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Missing key"},
        )
        with self.assertRaises(APIError) as ctx:
            self.api.compare_models(
                "token-a",
                conversation["conversation_id"],
                {
                    "text": "same prompt",
                    "gemini_api_key": "g-key",
                    "claude_api_key": "c-key",
                },
            )
        self.assertEqual(
            ctx.exception.code,
            "COMPARE_API_KEYS_REQUIRED_OPENAI",
        )

    def test_byok_openai_chat_requires_key(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "BYOK missing key"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "OpenAI"},
        )
        with self.assertRaises(APIError) as ctx:
            self.api.chat_with_openai(
                "token-a",
                conversation["conversation_id"],
                {"text": "hello"},
            )
        self.assertEqual(ctx.exception.code, "OPENAI_API_KEY_REQUIRED")

    def test_byok_claude_chat_requires_key(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "BYOK missing key"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Claude"},
        )
        with self.assertRaises(APIError) as ctx:
            self.api.chat_with_claude(
                "token-a",
                conversation["conversation_id"],
                {"text": "hello"},
            )
        self.assertEqual(ctx.exception.code, "CLAUDE_API_KEY_REQUIRED")

    def test_byok_gemini_chat_requires_key(self):
        workspace = self.api.create_workspace(
            "token-a", {"name": "BYOK missing key"}
        )
        conversation = self.api.create_conversation(
            "token-a",
            workspace["workspace_id"],
            {"title": "Gemini"},
        )
        with self.assertRaises(APIError) as ctx:
            self.api.chat_with_gemini(
                "token-a",
                conversation["conversation_id"],
                {"text": "hello"},
            )
        self.assertEqual(ctx.exception.code, "GEMINI_API_KEY_REQUIRED")

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
