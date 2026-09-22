from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pro_beta.auth_boundary import (
    AuthenticationError,
    VerifiedExternalIdentity,
)


@dataclass(frozen=True)
class ClerkConfig:
    issuer: str
    jwks_url: str
    authorized_parties: tuple[str, ...]
    logical_audience: str = "cfc-hawm-pro-beta"

    def validate(self) -> None:
        if not self.issuer.strip():
            raise AuthenticationError("CLERK_ISSUER_REQUIRED")
        if not self.jwks_url.strip():
            raise AuthenticationError("CLERK_JWKS_URL_REQUIRED")
        if not self.authorized_parties:
            raise AuthenticationError("CLERK_AUTHORIZED_PARTIES_REQUIRED")
        if any(not party.strip() for party in self.authorized_parties):
            raise AuthenticationError("CLERK_AUTHORIZED_PARTY_INVALID")


class ClerkIdentityVerifier:
    """Verify Clerk session JWTs without storing the token.

    Clerk session tokens do not require a custom aud claim. We verify signature,
    issuer, expiry/not-before/issued-at and subject, then enforce the Clerk azp
    claim against an explicit allowlist of frontend origins.
    """

    def __init__(
        self,
        config: ClerkConfig,
        *,
        decoder: Callable[[str], dict[str, Any]] | None = None,
    ) -> None:
        config.validate()
        self.config = config
        self._decoder = decoder or self._build_decoder(config)

    @staticmethod
    def _build_decoder(
        config: ClerkConfig,
    ) -> Callable[[str], dict[str, Any]]:
        try:
            import jwt
        except ImportError as exc:
            raise AuthenticationError("PYJWT_NOT_INSTALLED") from exc

        jwks_client = jwt.PyJWKClient(config.jwks_url)

        def decode(token: str) -> dict[str, Any]:
            try:
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                return jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    issuer=config.issuer,
                    options={
                        "require": ["exp", "iat", "sub"],
                        "verify_signature": True,
                        "verify_exp": True,
                        "verify_iat": True,
                        "verify_nbf": True,
                        "verify_iss": True,
                        "verify_aud": False,
                    },
                )
            except Exception as exc:
                raise AuthenticationError("IDENTITY_TOKEN_INVALID") from exc

        return decode

    def verify(self, credential: str) -> VerifiedExternalIdentity:
        token = credential.strip()
        if token.lower().startswith("bearer "):
            token = token[7:].strip()
        if not token:
            raise AuthenticationError("AUTH_CREDENTIAL_REQUIRED")

        try:
            claims = self._decoder(token)
        except AuthenticationError:
            raise
        except Exception as exc:
            raise AuthenticationError("IDENTITY_TOKEN_INVALID") from exc

        subject = str(claims.get("sub") or "").strip()
        issuer = str(claims.get("iss") or "").strip()
        azp = claims.get("azp")

        if not subject:
            raise AuthenticationError("IDENTITY_SUBJECT_MISSING")
        if issuer != self.config.issuer:
            raise AuthenticationError("IDENTITY_ISSUER_MISMATCH")
        if azp is not None and str(azp) not in self.config.authorized_parties:
            raise AuthenticationError("CLERK_AUTHORIZED_PARTY_MISMATCH")

        email = claims.get("email")
        email_verified = claims.get("email_verified")
        return VerifiedExternalIdentity(
            subject=subject,
            issuer=issuer,
            audience=self.config.logical_audience,
            email=str(email) if email is not None else None,
            email_verified=(
                bool(email_verified)
                if isinstance(email_verified, bool)
                else None
            ),
            provider_verified=True,
        )
