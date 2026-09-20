from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from pro_beta.api import MissingIdentityVerifier
from pro_beta.auth_boundary import AuthenticationError
from pro_beta.clerk_verifier import ClerkConfig, ClerkIdentityVerifier
from pro_beta.runtime_auth import build_identity_verifier_from_environment


class ClerkIdentityVerifierTests(unittest.TestCase):
    def config(self):
        return ClerkConfig(
            issuer="https://example.clerk.accounts.dev",
            jwks_url=(
                "https://example.clerk.accounts.dev/"
                ".well-known/jwks.json"
            ),
            authorized_parties=("https://app.example.com",),
        )

    def test_valid_clerk_claims_are_verified(self):
        verifier = ClerkIdentityVerifier(
            self.config(),
            decoder=lambda token: {
                "sub": "user_123",
                "iss": "https://example.clerk.accounts.dev",
                "azp": "https://app.example.com",
            },
        )
        identity = verifier.verify("Bearer abc")
        self.assertTrue(identity.provider_verified)
        self.assertEqual(identity.subject, "user_123")
        self.assertEqual(identity.audience, "cfc-hawm-pro-beta")

    def test_wrong_authorized_party_fails_closed(self):
        verifier = ClerkIdentityVerifier(
            self.config(),
            decoder=lambda token: {
                "sub": "user_123",
                "iss": "https://example.clerk.accounts.dev",
                "azp": "https://evil.example",
            },
        )
        with self.assertRaisesRegex(
            AuthenticationError,
            "CLERK_AUTHORIZED_PARTY_MISMATCH",
        ):
            verifier.verify("abc")

    def test_missing_azp_is_allowed_for_clerk_privacy_case(self):
        verifier = ClerkIdentityVerifier(
            self.config(),
            decoder=lambda token: {
                "sub": "user_123",
                "iss": "https://example.clerk.accounts.dev",
            },
        )
        identity = verifier.verify("abc")
        self.assertEqual(identity.subject, "user_123")

    def test_wrong_issuer_fails_closed(self):
        verifier = ClerkIdentityVerifier(
            self.config(),
            decoder=lambda token: {
                "sub": "user_123",
                "iss": "https://wrong.example",
                "azp": "https://app.example.com",
            },
        )
        with self.assertRaisesRegex(
            AuthenticationError,
            "IDENTITY_ISSUER_MISMATCH",
        ):
            verifier.verify("abc")

    def test_runtime_defaults_to_missing_verifier(self):
        with patch.dict(os.environ, {}, clear=True):
            verifier = build_identity_verifier_from_environment()
        self.assertIsInstance(verifier, MissingIdentityVerifier)

    def test_runtime_builds_clerk_from_environment(self):
        env = {
            "PRO_BETA_AUTH_PROVIDER": "clerk",
            "CLERK_ISSUER": "https://example.clerk.accounts.dev",
            "CLERK_JWKS_URL": (
                "https://example.clerk.accounts.dev/"
                ".well-known/jwks.json"
            ),
            "CLERK_AUTHORIZED_PARTIES": (
                "http://localhost:3000,https://app.example.com"
            ),
        }
        with patch.dict(os.environ, env, clear=True):
            verifier = build_identity_verifier_from_environment()
        self.assertIsInstance(verifier, ClerkIdentityVerifier)
        self.assertEqual(
            verifier.config.authorized_parties,
            ("http://localhost:3000", "https://app.example.com"),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
