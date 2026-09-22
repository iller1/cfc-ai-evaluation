from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pro_beta.auth_boundary import (
    AuthenticationError,
    VerifiedExternalIdentity,
)


@dataclass(frozen=True)
class OIDCConfig:
    issuer: str
    audience: str
    jwks_url: str

    def validate(self) -> None:
        if not self.issuer.strip():
            raise AuthenticationError("OIDC_ISSUER_REQUIRED")
        if not self.audience.strip():
            raise AuthenticationError("OIDC_AUDIENCE_REQUIRED")
        if not self.jwks_url.strip():
            raise AuthenticationError("OIDC_JWKS_URL_REQUIRED")


class OIDCIdentityVerifier:
    """Provider-neutral OIDC/JWT verifier.

    Signature, issuer, audience, expiry and standard JWT validity checks are
    delegated to PyJWT using the provider's JWKS endpoint. No token is stored.
    """

    def __init__(
        self,
        config: OIDCConfig,
        *,
        decoder: Callable[[str], dict[str, Any]] | None = None,
    ) -> None:
        config.validate()
        self.config = config
        self._decoder = decoder or self._build_decoder(config)

    @staticmethod
    def _build_decoder(
        config: OIDCConfig,
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
                    algorithms=["RS256", "ES256"],
                    audience=config.audience,
                    issuer=config.issuer,
                    options={
                        "require": ["exp", "iat", "sub"],
                        "verify_signature": True,
                        "verify_exp": True,
                        "verify_iat": True,
                        "verify_aud": True,
                        "verify_iss": True,
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
        audience_claim = claims.get("aud")
        if isinstance(audience_claim, list):
            audience_ok = self.config.audience in {
                str(item) for item in audience_claim
            }
            audience = self.config.audience if audience_ok else ""
        else:
            audience = str(audience_claim or "").strip()

        if not subject:
            raise AuthenticationError("IDENTITY_SUBJECT_MISSING")
        if issuer != self.config.issuer:
            raise AuthenticationError("IDENTITY_ISSUER_MISMATCH")
        if audience != self.config.audience:
            raise AuthenticationError("IDENTITY_AUDIENCE_MISMATCH")

        email = claims.get("email")
        email_verified = claims.get("email_verified")
        return VerifiedExternalIdentity(
            subject=subject,
            issuer=issuer,
            audience=self.config.audience,
            email=str(email) if email is not None else None,
            email_verified=(
                bool(email_verified)
                if isinstance(email_verified, bool)
                else None
            ),
            provider_verified=True,
        )
