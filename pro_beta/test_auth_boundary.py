from __future__ import annotations

import unittest

from pro_beta.auth_boundary import (
    AuthBoundary,
    AuthenticationError,
    VerifiedExternalIdentity,
)
from pro_beta.contracts import (
    Conversation,
    UserAccount,
    Workspace,
    new_id,
)
from pro_beta.persistence import InMemoryPersistence, OwnershipError


ISSUER = "https://identity.example/"
AUDIENCE = "cfc-hawm-pro-beta"


class AuthBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryPersistence()
        self.account_a = UserAccount(
            user_id=new_id("usr"),
            external_auth_subject="provider|user-a",
            email="a@example.com",
        )
        self.account_b = UserAccount(
            user_id=new_id("usr"),
            external_auth_subject="provider|user-b",
            email="b@example.com",
        )
        self.store.create_user(self.account_a)
        self.store.create_user(self.account_b)
        self.auth = AuthBoundary(
            self.store,
            expected_issuer=ISSUER,
            expected_audience=AUDIENCE,
        )

    def identity(
        self,
        subject="provider|user-a",
        *,
        verified=True,
        issuer=ISSUER,
        audience=AUDIENCE,
    ):
        return VerifiedExternalIdentity(
            subject=subject,
            issuer=issuer,
            audience=audience,
            email="a@example.com",
            email_verified=True,
            provider_verified=verified,
        )

    def test_verified_identity_maps_to_internal_user(self):
        ctx = self.auth.resolve(self.identity())
        self.assertEqual(ctx.user_id, self.account_a.user_id)
        self.assertEqual(
            ctx.external_auth_subject, self.account_a.external_auth_subject
        )

    def test_unverified_identity_fails_closed(self):
        with self.assertRaisesRegex(
            AuthenticationError, "IDENTITY_NOT_VERIFIED"
        ):
            self.auth.resolve(self.identity(verified=False))

    def test_missing_subject_fails_closed(self):
        with self.assertRaisesRegex(
            AuthenticationError, "IDENTITY_SUBJECT_MISSING"
        ):
            self.auth.resolve(self.identity(subject=""))

    def test_wrong_issuer_fails_closed(self):
        with self.assertRaisesRegex(
            AuthenticationError, "IDENTITY_ISSUER_MISMATCH"
        ):
            self.auth.resolve(
                self.identity(issuer="https://wrong.example/")
            )

    def test_wrong_audience_fails_closed(self):
        with self.assertRaisesRegex(
            AuthenticationError, "IDENTITY_AUDIENCE_MISMATCH"
        ):
            self.auth.resolve(self.identity(audience="other-app"))

    def test_unknown_external_subject_is_not_auto_created(self):
        with self.assertRaisesRegex(
            AuthenticationError, "ACCOUNT_NOT_PROVISIONED"
        ):
            self.auth.resolve(self.identity(subject="provider|unknown"))
        self.assertEqual(len(self.store.users), 2)

    def test_auth_context_drives_existing_ownership_boundary(self):
        workspace_b = Workspace(
            workspace_id=new_id("ws"),
            user_id=self.account_b.user_id,
            name="B private workspace",
        )
        self.store.create_workspace(self.account_b.user_id, workspace_b)
        conversation_b = Conversation(
            conversation_id=new_id("conv"),
            workspace_id=workspace_b.workspace_id,
            title="B private conversation",
        )
        self.store.create_conversation(
            self.account_b.user_id, conversation_b
        )

        ctx_a = self.auth.resolve(self.identity(subject="provider|user-a"))
        with self.assertRaises(OwnershipError):
            self.store.get_conversation(
                ctx_a.user_id, conversation_b.conversation_id
            )

    def test_email_is_not_used_as_account_authority(self):
        identity = VerifiedExternalIdentity(
            subject="provider|user-a",
            issuer=ISSUER,
            audience=AUDIENCE,
            email="b@example.com",
            email_verified=True,
            provider_verified=True,
        )
        ctx = self.auth.resolve(identity)
        self.assertEqual(ctx.user_id, self.account_a.user_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
