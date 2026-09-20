from __future__ import annotations

from dataclasses import asdict
from typing import Any, Protocol

from pro_beta.auth_boundary import (
    AuthBoundary,
    AuthenticationError,
    VerifiedExternalIdentity,
)
from pro_beta.persistence import NotFoundError, OwnershipError
from pro_beta.service import ProBetaService
from pro_beta.contracts import UserAccount, new_id


class IdentityVerifier(Protocol):
    """Verify an external credential before it reaches AuthBoundary."""

    def verify(self, credential: str) -> VerifiedExternalIdentity: ...


class MissingIdentityVerifier:
    """Fail-closed default used until a real provider adapter is configured."""

    def verify(self, credential: str) -> VerifiedExternalIdentity:
        raise AuthenticationError("IDENTITY_VERIFIER_NOT_CONFIGURED")


class APIError(Exception):
    def __init__(self, status: int, code: str):
        super().__init__(code)
        self.status = status
        self.code = code


class ProBetaAPI:
    """Transport-neutral API facade for Pro Beta v0.1.

    This layer accepts an opaque external credential, asks the configured
    IdentityVerifier to verify it, resolves the resulting identity through the
    AuthBoundary, and only then calls ProBetaService.

    It deliberately has no user_id argument on authenticated operations.
    """

    def __init__(
        self,
        *,
        verifier: IdentityVerifier,
        auth_boundary: AuthBoundary,
        service: ProBetaService,
    ) -> None:
        self.verifier = verifier
        self.auth_boundary = auth_boundary
        self.service = service

    def _auth(self, credential: str):
        if not credential:
            raise APIError(401, "AUTH_CREDENTIAL_REQUIRED")
        try:
            identity = self.verifier.verify(credential)
            return self.auth_boundary.resolve(identity)
        except AuthenticationError as exc:
            raise APIError(401, str(exc)) from exc

    def provision_account(self, credential: str) -> dict:
        """Explicit first-login provisioning.

        Normal authenticated operations remain fail-closed for unknown subjects.
        This endpoint is the one deliberate path that may create an account
        after the external identity has been cryptographically verified.
        """
        if not credential:
            raise APIError(401, "AUTH_CREDENTIAL_REQUIRED")
        try:
            identity = self.verifier.verify(credential)
        except AuthenticationError as exc:
            raise APIError(401, str(exc)) from exc

        if not identity.provider_verified:
            raise APIError(401, "IDENTITY_NOT_VERIFIED")
        if identity.issuer != self.auth_boundary.expected_issuer:
            raise APIError(401, "IDENTITY_ISSUER_MISMATCH")
        if identity.audience != self.auth_boundary.expected_audience:
            raise APIError(401, "IDENTITY_AUDIENCE_MISMATCH")

        try:
            account = self.auth_boundary.accounts.get_user_by_external_auth_subject(
                identity.subject
            )
            created = False
        except NotFoundError:
            account = UserAccount(
                user_id=new_id("usr"),
                external_auth_subject=identity.subject,
                email=identity.email if identity.email_verified else None,
            )
            self.auth_boundary.accounts.create_user(account)
            created = True

        return {"account": asdict(account), "created": created}

    def create_workspace(self, credential: str, payload: dict[str, Any]) -> dict:
        auth = self._auth(credential)
        name = str(payload.get("name") or "")
        workspace = self.service.create_workspace(auth, name)
        return asdict(workspace)

    def list_workspaces(self, credential: str) -> list[dict]:
        auth = self._auth(credential)
        return [asdict(w) for w in self.service.list_workspaces(auth)]

    def create_conversation(
        self,
        credential: str,
        workspace_id: str,
        payload: dict[str, Any],
    ) -> dict:
        auth = self._auth(credential)
        title = str(payload.get("title") or "")
        try:
            conversation = self.service.create_conversation(
                auth, workspace_id, title
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        return asdict(conversation)

    def list_conversations(
        self, credential: str, workspace_id: str
    ) -> list[dict]:
        auth = self._auth(credential)
        try:
            conversations = self.service.list_conversations(auth, workspace_id)
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        return [asdict(c) for c in conversations]

    def get_conversation(
        self, credential: str, conversation_id: str
    ) -> dict:
        auth = self._auth(credential)
        try:
            conversation = self.service.get_conversation(
                auth, conversation_id
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        return asdict(conversation)

    def list_messages(
        self, credential: str, conversation_id: str
    ) -> list[dict]:
        auth = self._auth(credential)
        try:
            messages = self.service.list_messages(auth, conversation_id)
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        return [asdict(m) for m in messages]

    def persist_user_message(
        self,
        credential: str,
        conversation_id: str,
        *,
        content: str,
        mode: str,
    ) -> dict:
        auth = self._auth(credential)
        try:
            message = self.service.save_user_message(
                auth, conversation_id, content, mode
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        return asdict(message)

    def persist_model_reply(
        self,
        credential: str,
        conversation_id: str,
        *,
        content: str,
        mode: str,
    ) -> dict:
        """Internal application operation, not proof of CFC authorization."""
        auth = self._auth(credential)
        try:
            message = self.service.save_model_reply(
                auth, conversation_id, content, mode
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        return asdict(message)
