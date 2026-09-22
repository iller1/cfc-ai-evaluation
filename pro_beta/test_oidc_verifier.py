from __future__ import annotations

import unittest

from pro_beta.auth_boundary import AuthenticationError
from pro_beta.oidc_verifier import OIDCConfig, OIDCIdentityVerifier


class OIDCIdentityVerifierTests(unittest.TestCase):
    def config(self):
        return OIDCConfig(
            issuer="https://id.example/",
            audience="cfc-hawm-pro-beta",
            jwks_url="https://id.example/.well-known/jwks.json",
        )

    def test_verified_claims_map_to_external_identity(self):
        verifier = OIDCIdentityVerifier(
            self.config(),
            decoder=lambda token: {
                "sub": "provider|abc",
                "iss": "https://id.example/",
                "aud": "cfc-hawm-pro-beta",
                "email": "user@example.com",
                "email_verified": True,
            },
        )
        identity = verifier.verify("Bearer token-value")
        self.assertTrue(identity.provider_verified)
        self.assertEqual(identity.subject, "provider|abc")
        self.assertEqual(identity.audience, "cfc-hawm-pro-beta")
        self.assertEqual(identity.email, "user@example.com")

    def test_audience_array_is_supported(self):
        verifier = OIDCIdentityVerifier(
            self.config(),
            decoder=lambda token: {
                "sub": "provider|abc",
                "iss": "https://id.example/",
                "aud": ["other", "cfc-hawm-pro-beta"],
            },
        )
        identity = verifier.verify("token-value")
        self.assertEqual(identity.audience, "cfc-hawm-pro-beta")

    def test_wrong_issuer_fails_closed(self):
        verifier = OIDCIdentityVerifier(
            self.config(),
            decoder=lambda token: {
                "sub": "provider|abc",
                "iss": "https://wrong.example/",
                "aud": "cfc-hawm-pro-beta",
            },
        )
        with self.assertRaisesRegex(
            AuthenticationError, "IDENTITY_ISSUER_MISMATCH"
        ):
            verifier.verify("token-value")

    def test_wrong_audience_fails_closed(self):
        verifier = OIDCIdentityVerifier(
            self.config(),
            decoder=lambda token: {
                "sub": "provider|abc",
                "iss": "https://id.example/",
                "aud": "wrong-audience",
            },
        )
        with self.assertRaisesRegex(
            AuthenticationError, "IDENTITY_AUDIENCE_MISMATCH"
        ):
            verifier.verify("token-value")

    def test_missing_subject_fails_closed(self):
        verifier = OIDCIdentityVerifier(
            self.config(),
            decoder=lambda token: {
                "iss": "https://id.example/",
                "aud": "cfc-hawm-pro-beta",
            },
        )
        with self.assertRaisesRegex(
            AuthenticationError, "IDENTITY_SUBJECT_MISSING"
        ):
            verifier.verify("token-value")

    def test_decoder_failure_becomes_authentication_error(self):
        def bad_decoder(token):
            raise ValueError("bad token")

        verifier = OIDCIdentityVerifier(
            self.config(),
            decoder=bad_decoder,
        )
        with self.assertRaisesRegex(
            AuthenticationError, "IDENTITY_TOKEN_INVALID"
        ):
            verifier.verify("token-value")

    def test_incomplete_config_fails_closed(self):
        with self.assertRaisesRegex(
            AuthenticationError, "OIDC_ISSUER_REQUIRED"
        ):
            OIDCIdentityVerifier(
                OIDCConfig(
                    issuer="",
                    audience="cfc-hawm-pro-beta",
                    jwks_url="https://id.example/jwks",
                ),
                decoder=lambda token: {},
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
