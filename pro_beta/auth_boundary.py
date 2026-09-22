from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from pro_beta.contracts import UserAccount
from pro_beta.persistence import NotFoundError


class AuthenticationError(PermissionError):
    """External identity is missing, unverified, or not accepted."""


class AccountLookup(Protocol):
    def get_user_by_external_auth_subject(
        self, external_auth_subject: str
    ) -> UserAccount: ...


@dataclass(frozen=True)
class VerifiedExternalIdentity:
    """Identity after verification by an external authentication provider.

    This object is intentionally downstream of token/JWT verification. The
    CFC + HAWM application does not validate passwords and does not treat raw
    bearer tokens as trusted identity records.
    """

    subject: str
    issuer: str
    audience: str
    email: str | None = None
    email_verified: bool | None = None
    provider_verified: bool = False


@dataclass(frozen=True)
class AuthContext:
    user_id: str
    external_auth_subject: str
    issuer: str
    audience: str


class AuthBoundary:
    """Map externally verified identity to the internal Pro Beta account."""

    def __init__(
        self,
        accounts: AccountLookup,
        *,
        expected_issuer: str,
        expected_audience: str,
    ) -> None:
        self.accounts = accounts
        self.expected_issuer = expected_issuer
        self.expected_audience = expected_audience

    def resolve(self, identity: VerifiedExternalIdentity) -> AuthContext:
        if not identity.provider_verified:
            raise AuthenticationError("IDENTITY_NOT_VERIFIED")
        if not identity.subject.strip():
            raise AuthenticationError("IDENTITY_SUBJECT_MISSING")
        if identity.issuer != self.expected_issuer:
            raise AuthenticationError("IDENTITY_ISSUER_MISMATCH")
        if identity.audience != self.expected_audience:
            raise AuthenticationError("IDENTITY_AUDIENCE_MISMATCH")

        try:
            account = self.accounts.get_user_by_external_auth_subject(
                identity.subject
            )
        except NotFoundError as exc:
            raise AuthenticationError("ACCOUNT_NOT_PROVISIONED") from exc

        return AuthContext(
            user_id=account.user_id,
            external_auth_subject=account.external_auth_subject,
            issuer=identity.issuer,
            audience=identity.audience,
        )
