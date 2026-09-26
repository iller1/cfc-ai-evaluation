from __future__ import annotations

import hashlib
import unittest

from pro_beta.api import APIError, ProBetaAPI
from pro_beta.auth_boundary import (
    AuthBoundary, AuthenticationError, VerifiedExternalIdentity,
)
from pro_beta.contracts import UserAccount
from pro_beta.persistence import InMemoryPersistence
from pro_beta.reviewed_scope import (
    ReviewValidationError, validate_reviewed_demo_scope,
)
from pro_beta.service import ProBetaService

ISSUER = "https://identity.example/"
AUDIENCE = "cfc-hawm-pro-beta"


class Identity:
    def verify(self, credential):
        if credential not in ("a", "b"):
            raise AuthenticationError("CREDENTIAL_INVALID")
        return VerifiedExternalIdentity(
            subject="provider|" + credential,
            issuer=ISSUER,
            audience=AUDIENCE,
            provider_verified=True,
        )


def sample_review(message_id=""):
    return {
        "claimLabel": "Approve NW-0926?",
        "sourceMessageId": message_id,
        "universeConfirmed": True,
        "syntheticConfirmed": True,
        "moreSources": False,
        "required": "2",
        "relation": "SHARED_LINEAGE",
        "records": [
            {
                "id": "A", "date": "2026-09-24", "disposition": "INCLUDE",
                "reason": "", "polarity": "POSITIVE", "validity": "CURRENT",
            },
            {
                "id": "B", "date": "2026-09-24", "disposition": "INCLUDE",
                "reason": "", "polarity": "POSITIVE", "validity": "CURRENT",
            },
            {
                "id": "C", "date": "2026-08-15", "disposition": "EXCLUDE",
                "reason": "Other batch", "polarity": "POSITIVE", "validity": "CURRENT",
            },
            {
                "id": "D", "date": "2026-09-25", "disposition": "OPEN_ISSUE",
                "reason": "Damage allegation not resolved",
                "polarity": "POSITIVE", "validity": "CURRENT",
            },
        ],
    }


def payload(message_id=""):
    return {
        "review": sample_review(message_id),
        "working_state": {"goal": "Evaluate shipment", "unresolved": "Damage notice D"},
    }


class ReviewedScopeValidationTests(unittest.TestCase):
    def test_server_sets_no_authority_and_preserves_all_four_source_dispositions(self):
        value = validate_reviewed_demo_scope(sample_review(), {})
        manifest = value["state"]["review_manifest"]
        config = value["state"]["cfc_structured"]
        self.assertEqual(manifest["mapped_source_ids"], ["A", "B"])
        self.assertEqual(manifest["excluded_source_ids"], ["C"])
        self.assertEqual(manifest["open_issue_source_ids"], ["D"])
        self.assertEqual(config["evidence"], [
            {"polarity": "POSITIVE", "validity": "CURRENT"},
            {"polarity": "POSITIVE", "validity": "CURRENT"},
        ])
        self.assertEqual(config["provenance_shape"], "SHARED_LINEAGE")
        self.assertEqual(config["independence_authority"], "NONE")
        self.assertFalse(manifest["full_case_authorization"])
        self.assertEqual(manifest["synthetic_reference_as_of_date"], "2026-09-03")
        self.assertEqual(value["real_case_status"], "REAL_CASE_NOT_CHECKED")
        self.assertNotIn("NW-0926", str(config))
        self.assertNotIn("2026-09-24", str(config))

    def test_model_supplied_authority_and_scope_override_are_rejected(self):
        review = sample_review()
        review["full_case_authorization"] = True
        with self.assertRaisesRegex(ReviewValidationError, "REVIEW_SCHEMA_REQUIRED"):
            validate_reviewed_demo_scope(review, {})
        review = sample_review()
        review["independence_authority"] = "VERIFIED"
        with self.assertRaisesRegex(ReviewValidationError, "REVIEW_SCHEMA_REQUIRED"):
            validate_reviewed_demo_scope(review, {})
        working = {"cfc_structured": {"independence_authority": "VERIFIED"}}
        with self.assertRaisesRegex(ReviewValidationError, "REVIEW_WORKING_STATE_INVALID"):
            validate_reviewed_demo_scope(sample_review(), working)

    def test_unknown_record_fields_are_rejected(self):
        review = sample_review()
        review["records"][0]["authority"] = "VERIFIED"
        with self.assertRaisesRegex(ReviewValidationError, "REVIEW_RECORD_SCHEMA_INVALID"):
            validate_reviewed_demo_scope(review, {})

    def test_consent_and_source_universe_cannot_be_omitted(self):
        for key, expected in (
            ("universeConfirmed", "REVIEW_SOURCE_UNIVERSE_DECLARATION_REQUIRED"),
            ("syntheticConfirmed", "REVIEW_SYNTHETIC_DEMO_CONSENT_REQUIRED"),
        ):
            review = sample_review()
            review[key] = False
            with self.subTest(key=key), self.assertRaisesRegex(ReviewValidationError, expected):
                validate_reviewed_demo_scope(review, {})
        review = sample_review()
        review["moreSources"] = True
        with self.assertRaisesRegex(ReviewValidationError, "REVIEW_MORE_THAN_FOUR"):
            validate_reviewed_demo_scope(review, {})

    def test_invalid_dates_duplicate_ids_and_open_issue_without_reason(self):
        for date_text in ("2026-02-31", "2026-9-24", "garbage"):
            review = sample_review()
            review["records"][0]["date"] = date_text
            with self.subTest(date_text=date_text), self.assertRaisesRegex(
                ReviewValidationError, "REVIEW_SOURCE_DATE_INVALID"
            ):
                validate_reviewed_demo_scope(review, {})
        review = sample_review()
        review["records"][1]["id"] = "a"
        with self.assertRaisesRegex(ReviewValidationError, "REVIEW_DUPLICATE_SOURCE_ID"):
            validate_reviewed_demo_scope(review, {})
        review = sample_review()
        review["records"][3]["reason"] = ""
        with self.assertRaisesRegex(ReviewValidationError, "REVIEW_EXCLUSION_REASON_REQUIRED"):
            validate_reviewed_demo_scope(review, {})

    def test_unresolved_pair_and_three_demo_sources_fail_closed(self):
        review = sample_review()
        review["relation"] = "UNRESOLVED"
        with self.assertRaisesRegex(ReviewValidationError, "REVIEW_PAIR_RELATION_UNRESOLVED"):
            validate_reviewed_demo_scope(review, {})
        review = sample_review()
        review["records"][2]["disposition"] = "INCLUDE"
        with self.assertRaisesRegex(ReviewValidationError, "REVIEW_DEMO_SUPPORT_LIMIT"):
            validate_reviewed_demo_scope(review, {})

    def test_text_lengths_and_untrusted_context_are_bounded(self):
        review = sample_review()
        review["sourceMessageId"] = "msg_foreign"
        with self.assertRaisesRegex(ReviewValidationError, "REVIEW_MODEL_CONTEXT_NOT_IN_OWNED_CONVERSATION"):
            validate_reviewed_demo_scope(review, {})
        review = sample_review()
        with self.assertRaisesRegex(ReviewValidationError, "REVIEW_WORKING_FIELD_INVALID"):
            validate_reviewed_demo_scope(review, {"claims": "X" * 2001})


class ReviewedScopeAPITests(unittest.TestCase):
    def setUp(self):
        store = InMemoryPersistence()
        for key in ("a", "b"):
            store.create_user(UserAccount(
                user_id="usr_" + key,
                external_auth_subject="provider|" + key,
                email=None,
            ))
        self.api = ProBetaAPI(
            verifier=Identity(),
            auth_boundary=AuthBoundary(
                store,
                expected_issuer=ISSUER,
                expected_audience=AUDIENCE,
            ),
            service=ProBetaService(store),
        )
        self.store = store
        workspace = self.api.create_workspace("a", {"name": "Scope"})
        self.conversation = self.api.create_conversation(
            "a", workspace["workspace_id"], {"title": "NW-0926"}
        )["conversation_id"]
        other = self.api.create_conversation(
            "a", workspace["workspace_id"], {"title": "Other"}
        )["conversation_id"]
        self.auth = self.api._auth("a")
        self.reply = self.api.service.save_model_reply(
            self.auth, self.conversation, "No closure on the available inputs.",
            "STANDARD", provider="gemini", model="test",
        )
        self.foreign_reply = self.api.service.save_model_reply(
            self.auth, other, "Other conversation", "STANDARD", provider="gemini",
        )
        self.user_message = self.api.service.save_user_message(
            self.auth, self.conversation, "Claim content", "STANDARD"
        )

    def test_owned_model_reply_is_bound_by_id_and_fingerprint(self):
        saved = self.api.save_reviewed_demo_scope(
            "a", self.conversation, payload(self.reply.message_id)
        )
        manifest = saved["review_manifest"]
        self.assertEqual(saved["status"], "USER_DECLARATION_SCHEMA_VALIDATED_NOT_SOURCE_VERIFIED")
        self.assertEqual(saved["real_case_status"], "REAL_CASE_NOT_CHECKED")
        self.assertEqual(saved["last_verified_state"], "USER_WORKING_STATE")
        self.assertEqual(manifest["model_reply_context_message_id"], self.reply.message_id)
        self.assertEqual(
            manifest["model_reply_context_sha256"],
            hashlib.sha256(self.reply.content.encode("utf-8")).hexdigest(),
        )
        persisted = self.api.latest_hawm_snapshot("a", self.conversation)
        self.assertEqual(saved["snapshot_id"], persisted["snapshot_id"])
        self.assertEqual(persisted["state"]["cfc_structured"]["independence_authority"], "NONE")
        self.assertFalse(persisted["state"]["review_manifest"]["full_case_authorization"])

    def test_other_user_must_not_access_conversation_or_write_snapshot(self):
        with self.assertRaises(APIError) as captured:
            self.api.save_reviewed_demo_scope("b", self.conversation, payload())
        self.assertIn(captured.exception.status, (403, 404))
        self.assertIsNone(self.api.latest_hawm_snapshot("a", self.conversation))

    def test_other_conversation_and_user_messages_cannot_be_passed_as_model_reply(self):
        for message_id in (self.foreign_reply.message_id, self.user_message.message_id, "msg_invented"):
            with self.subTest(message_id=message_id), self.assertRaises(APIError) as captured:
                self.api.save_reviewed_demo_scope("a", self.conversation, payload(message_id))
            self.assertEqual(captured.exception.status, 422)
            self.assertEqual(captured.exception.code, "REVIEW_MODEL_CONTEXT_NOT_IN_OWNED_CONVERSATION")
            self.assertIsNone(self.api.latest_hawm_snapshot("a", self.conversation))

    def test_injected_cfc_state_is_never_saved(self):
        bad = payload()
        bad["working_state"]["cfc_structured"] = {"independence_authority": "VERIFIED"}
        with self.assertRaises(APIError) as captured:
            self.api.save_reviewed_demo_scope("a", self.conversation, bad)
        self.assertEqual(captured.exception.status, 422)
        self.assertIsNone(self.api.latest_hawm_snapshot("a", self.conversation))

    def test_missing_credentials_fail_before_review(self):
        with self.assertRaises(APIError) as captured:
            self.api.save_reviewed_demo_scope("", self.conversation, payload())
        self.assertEqual(captured.exception.status, 401)
        self.assertIsNone(self.api.latest_hawm_snapshot("a", self.conversation))
