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

    def test_user_cannot_select_another_user_by_payload(self):
        created = self.api.create_workspace(
            "token-a",
            {"name": "A workspace", "user_id": "usr_b"},
        )
        self.assertEqual(created["user_id"], "usr_a")

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
