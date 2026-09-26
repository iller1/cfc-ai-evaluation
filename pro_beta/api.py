from __future__ import annotations

import time
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

    def run_founding_beta_structured_cfc(
        self,
        credential: str,
        workspace_id: str,
        payload: dict[str, Any],
    ) -> dict:
        auth = self._auth(credential)
        forbidden = {
            "document",
            "document_text",
            "content",
            "prompt",
            "response",
            "model_response",
            "raw_evidence",
        }
        if forbidden.intersection(payload):
            raise APIError(400, "FOUNDING_BETA_CUSTOMER_CONTENT_FORBIDDEN")
        try:
            self.service.get_workspace(auth, workspace_id)
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc

        state = payload.get("cfc_structured")
        if not isinstance(state, dict):
            raise APIError(400, "FOUNDING_BETA_STRUCTURED_STATE_REQUIRED")
        if forbidden.intersection(state):
            raise APIError(400, "FOUNDING_BETA_CUSTOMER_CONTENT_FORBIDDEN")

        try:
            from pro_beta.cfc_execution import run_structured_hawm_state
            executed = run_structured_hawm_state(
                {"cfc_structured": state}
            )
        except ValueError as exc:
            raise APIError(400, str(exc)) from exc
        except Exception as exc:
            raise APIError(500, "CFC_EXECUTION_FAILED") from exc

        return {
            "case_id": executed["case_id"],
            "controller_anchor": executed["controller_anchor"],
            "controller_result": executed["controller_result"],
            "presentation": executed["presentation"],
            "boundary": executed["boundary"],
            "mapped_input": executed["mapped_input"],
            "persisted_customer_content": False,
        }

    def create_founding_beta_measurement(
        self,
        credential: str,
        workspace_id: str,
        payload: dict[str, Any],
    ) -> dict:
        auth = self._auth(credential)
        forbidden = {
            "document",
            "document_text",
            "content",
            "prompt",
            "response",
            "model_response",
            "raw_evidence",
        }
        if forbidden.intersection(payload):
            raise APIError(400, "FOUNDING_BETA_CUSTOMER_CONTENT_FORBIDDEN")
        try:
            item = self.service.save_founding_beta_measurement(
                auth,
                workspace_id,
                system_version=str(payload.get("system_version") or ""),
                workflow_type=str(payload.get("workflow_type") or ""),
                case_id=str(payload.get("case_id") or ""),
                cfc_result=str(payload.get("cfc_result") or ""),
                reason_code=str(payload.get("reason_code") or ""),
                hawm_state=str(payload.get("hawm_state") or ""),
                human_assessment=str(payload.get("human_assessment") or ""),
                final_action=str(payload.get("final_action") or ""),
                problem_type=str(payload.get("problem_type") or ""),
                comment=payload.get("comment"),
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        except ValueError as exc:
            raise APIError(400, str(exc)) from exc
        return asdict(item)

    def list_founding_beta_measurements(
        self, credential: str, workspace_id: str
    ) -> list[dict]:
        auth = self._auth(credential)
        try:
            rows = self.service.list_founding_beta_measurements(
                auth, workspace_id
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        return [asdict(row) for row in rows]

    def delete_founding_beta_measurements(
        self, credential: str, workspace_id: str
    ) -> dict:
        auth = self._auth(credential)
        try:
            deleted = self.service.delete_founding_beta_measurements(
                auth, workspace_id
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        return {
            "workspace_id": workspace_id,
            "deleted_measurements": deleted,
            "customer_content_deleted": 0,
        }


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

    def extract_document_preview(
        self, credential: str, conversation_id: str, payload: dict[str, Any]
    ) -> dict:
        """Authenticate/authorize the conversation before decoding or parsing bytes."""
        self.get_conversation(credential, conversation_id)
        from pro_beta.document_extract import DocumentError, extract_document_in_worker

        try:
            return extract_document_in_worker(payload)
        except DocumentError as exc:
            raise APIError(422, str(exc)) from exc

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

    def save_hawm_snapshot(
        self,
        credential: str,
        conversation_id: str,
        payload: dict[str, Any],
    ) -> dict:
        auth = self._auth(credential)
        state = payload.get("state")
        if not isinstance(state, dict):
            raise APIError(400, "HAWM_STATE_REQUIRED")
        last_verified_state = str(
            payload.get("last_verified_state") or "UNVERIFIED"
        )
        try:
            snapshot = self.service.save_hawm_snapshot(
                auth,
                conversation_id,
                state,
                last_verified_state,
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        return asdict(snapshot)

    def latest_hawm_snapshot(
        self, credential: str, conversation_id: str
    ) -> dict | None:
        auth = self._auth(credential)
        try:
            snapshot = self.service.latest_hawm_snapshot(
                auth, conversation_id
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        return asdict(snapshot) if snapshot is not None else None

    def run_prepared_cfc_case(
        self,
        credential: str,
        conversation_id: str,
        payload: dict[str, Any],
    ) -> dict:
        auth = self._auth(credential)
        case_id = str(payload.get("case_id") or "")
        try:
            self.service.get_conversation(auth, conversation_id)
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc

        try:
            from pro_beta.cfc_execution import run_prepared_case
            executed = run_prepared_case(case_id)
        except ValueError as exc:
            raise APIError(400, str(exc)) from exc
        except Exception as exc:
            raise APIError(500, "CFC_EXECUTION_FAILED") from exc

        run = self.service.save_cfc_run(
            auth,
            conversation_id,
            case_id=executed["case_id"],
            controller_anchor=executed["controller_anchor"],
            controller_result=executed["controller_result"],
            presentation=executed["presentation"],
            replay_matches_reference=executed["replay_matches_reference"],
        )
        response = asdict(run)
        response["boundary"] = executed["boundary"]
        return response

    def run_structured_hawm_cfc(
        self,
        credential: str,
        conversation_id: str,
    ) -> dict:
        auth = self._auth(credential)
        try:
            snapshot = self.service.latest_hawm_snapshot(
                auth, conversation_id
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        if snapshot is None:
            raise APIError(400, "HAWM_SNAPSHOT_REQUIRED")

        try:
            from pro_beta.cfc_execution import run_structured_hawm_state
            executed = run_structured_hawm_state(snapshot.state)
        except ValueError as exc:
            raise APIError(400, str(exc)) from exc
        except Exception as exc:
            raise APIError(500, "CFC_EXECUTION_FAILED") from exc

        run = self.service.save_cfc_run(
            auth,
            conversation_id,
            case_id=executed["case_id"],
            controller_anchor=executed["controller_anchor"],
            controller_result=executed["controller_result"],
            presentation=executed["presentation"],
            replay_matches_reference=executed["replay_matches_reference"],
        )
        response = asdict(run)
        response["boundary"] = executed["boundary"]
        response["mapped_input"] = executed["mapped_input"]
        response["hawm_snapshot_id"] = snapshot.snapshot_id
        return response

    def latest_cfc_run(
        self, credential: str, conversation_id: str
    ) -> dict | None:
        auth = self._auth(credential)
        try:
            run = self.service.latest_cfc_run(auth, conversation_id)
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc
        return asdict(run) if run is not None else None

    def create_audit_report(
        self,
        credential: str,
        conversation_id: str,
    ) -> dict:
        auth = self._auth(credential)
        try:
            conversation = self.service.get_conversation(
                auth, conversation_id
            )
            hawm_snapshot = self.service.latest_hawm_snapshot(
                auth, conversation_id
            )
            cfc_run = self.service.latest_cfc_run(
                auth, conversation_id
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc

        if hawm_snapshot is None and cfc_run is None:
            raise APIError(400, "HAWM_OR_CFC_REQUIRED")

        from pro_beta.audit_report import build_audit_document, render_markdown

        document = build_audit_document(
            conversation=conversation,
            hawm_snapshot=hawm_snapshot,
            cfc_run=cfc_run,
        )
        report = self.service.save_audit_report(
            auth,
            conversation_id,
            cfc_run_id=cfc_run.run_id if cfc_run is not None else None,
            status="GENERATED_JSON_MARKDOWN",
            artifact_path=None,
        )
        return {
            "report_record": asdict(report),
            "document": document,
            "markdown": render_markdown(document),
        }

    def chat_with_gemini(
        self,
        credential: str,
        conversation_id: str,
        payload: dict[str, Any],
    ) -> dict:
        auth = self._auth(credential)
        text = str(payload.get("text") or "").strip()
        api_key = str(payload.get("api_key") or "").strip()
        model = str(payload.get("model") or "gemini-3.8-flash").strip()
        mode = str(payload.get("mode") or "STANDARD").upper()
        if not text:
            raise APIError(400, "TEXT_REQUIRED")
        if not api_key:
            raise APIError(400, "GEMINI_API_KEY_REQUIRED")

        try:
            self.service.get_conversation(auth, conversation_id)
            history = [
                asdict(message)
                for message in self.service.list_messages(
                    auth, conversation_id
                )
            ]
            hawm_snapshot = self.service.latest_hawm_snapshot(
                auth, conversation_id
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc

        try:
            from pro_beta.model_provider import ProviderError, gemini_call
            result = gemini_call(
                api_key=api_key,
                model=model,
                text=text,
                mode=mode,
                history=history,
                hawm_state=(
                    hawm_snapshot.state if hawm_snapshot is not None else None
                ),
            )
        except ProviderError as exc:
            raise APIError(502, str(exc)) from exc

        user_message = self.service.save_user_message(
            auth,
            conversation_id,
            text,
            result["mode"],
        )
        model_message = self.service.save_model_reply(
            auth,
            conversation_id,
            result["text"],
            result["mode"],
            provider=result["provider"],
            model=result["model"],
        )
        return {
            "user_message": asdict(user_message),
            "model_message": asdict(model_message),
            "provider": result["provider"],
            "model": result["model"],
            "mode": result["mode"],
            "finish_reason": result["finish_reason"],
            "truncated": result["truncated"],
            "authority": result["authority"],
            "cfc_status": result["cfc_status"],
            "api_key_persisted": False,
        }

    def chat_with_claude(
        self,
        credential: str,
        conversation_id: str,
        payload: dict[str, Any],
    ) -> dict:
        auth = self._auth(credential)
        text = str(payload.get("text") or "").strip()
        api_key = str(payload.get("api_key") or "").strip()
        model = str(payload.get("model") or "claude-sonnet-4-5").strip()
        mode = str(payload.get("mode") or "STANDARD").upper()
        if not text:
            raise APIError(400, "TEXT_REQUIRED")
        if not api_key:
            raise APIError(400, "CLAUDE_API_KEY_REQUIRED")

        try:
            self.service.get_conversation(auth, conversation_id)
            history = [
                asdict(message)
                for message in self.service.list_messages(
                    auth, conversation_id
                )
            ]
            hawm_snapshot = self.service.latest_hawm_snapshot(
                auth, conversation_id
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc

        try:
            from pro_beta.model_provider import ProviderError, claude_call
            result = claude_call(
                api_key=api_key,
                model=model,
                text=text,
                mode=mode,
                history=history,
                hawm_state=(
                    hawm_snapshot.state if hawm_snapshot is not None else None
                ),
            )
        except ProviderError as exc:
            raise APIError(502, str(exc)) from exc

        user_message = self.service.save_user_message(
            auth,
            conversation_id,
            text,
            result["mode"],
        )
        model_message = self.service.save_model_reply(
            auth,
            conversation_id,
            result["text"],
            result["mode"],
            provider=result["provider"],
            model=result["model"],
        )
        return {
            "user_message": asdict(user_message),
            "model_message": asdict(model_message),
            "provider": result["provider"],
            "model": result["model"],
            "mode": result["mode"],
            "finish_reason": result["finish_reason"],
            "truncated": result["truncated"],
            "authority": result["authority"],
            "cfc_status": result["cfc_status"],
            "api_key_persisted": False,
        }

    def chat_with_openai(
        self,
        credential: str,
        conversation_id: str,
        payload: dict[str, Any],
    ) -> dict:
        auth = self._auth(credential)
        text = str(payload.get("text") or "").strip()
        api_key = str(payload.get("api_key") or "").strip()
        model = str(payload.get("model") or "gpt-5.6-terra").strip()
        mode = str(payload.get("mode") or "STANDARD").upper()
        if not text:
            raise APIError(400, "TEXT_REQUIRED")
        if not api_key:
            raise APIError(400, "OPENAI_API_KEY_REQUIRED")

        try:
            self.service.get_conversation(auth, conversation_id)
            history = [
                asdict(message)
                for message in self.service.list_messages(
                    auth, conversation_id
                )
            ]
            hawm_snapshot = self.service.latest_hawm_snapshot(
                auth, conversation_id
            )
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc

        try:
            from pro_beta.model_provider import ProviderError, openai_call
            result = openai_call(
                api_key=api_key,
                model=model,
                text=text,
                mode=mode,
                history=history,
                hawm_state=(
                    hawm_snapshot.state if hawm_snapshot is not None else None
                ),
            )
        except ProviderError as exc:
            raise APIError(502, str(exc)) from exc

        user_message = self.service.save_user_message(
            auth,
            conversation_id,
            text,
            result["mode"],
        )
        model_message = self.service.save_model_reply(
            auth,
            conversation_id,
            result["text"],
            result["mode"],
            provider=result["provider"],
            model=result["model"],
        )
        return {
            "user_message": asdict(user_message),
            "model_message": asdict(model_message),
            "provider": result["provider"],
            "model": result["model"],
            "mode": result["mode"],
            "finish_reason": result["finish_reason"],
            "truncated": result["truncated"],
            "authority": result["authority"],
            "cfc_status": result["cfc_status"],
            "api_key_persisted": False,
        }

    def list_benchmark_cases(self, credential: str) -> dict:
        self._auth(credential)
        from pro_beta.benchmark_cases import benchmark_manifest

        return benchmark_manifest()

    def list_benchmark_runs(
        self, credential: str, conversation_id: str
    ) -> list[dict]:
        auth = self._auth(credential)
        try:
            runs = self.service.list_benchmark_runs(auth, conversation_id)
            response = []
            for run in runs:
                row = asdict(run)
                row["manual_labels"] = [
                    asdict(label)
                    for label in self.service.list_benchmark_manual_labels(
                        auth, run.benchmark_run_id
                    )
                ]
                response.append(row)
            return response
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc

    def save_benchmark_manual_label(
        self,
        credential: str,
        benchmark_run_id: str,
        payload: dict[str, Any],
    ) -> dict:
        auth = self._auth(credential)
        provider = str(payload.get("provider") or "").strip().lower()
        label = str(payload.get("label") or "").strip().upper()
        note = str(payload.get("note") or "").strip() or None
        allowed = {"CONSISTENT", "AMBIGUOUS", "PREMATURE_CLOSURE"}
        if label not in allowed:
            raise APIError(400, "BENCHMARK_LABEL_INVALID")
        if not provider:
            raise APIError(400, "BENCHMARK_PROVIDER_REQUIRED")

        try:
            run = self.service.get_benchmark_run(auth, benchmark_run_id)
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc

        result = next(
            (
                item
                for item in run.results
                if str(item.get("provider") or "").lower() == provider
            ),
            None,
        )
        if result is None:
            raise APIError(
                400,
                "BENCHMARK_PROVIDER_NOT_IN_SUCCESSFUL_RESULTS",
            )

        saved = self.service.save_benchmark_manual_label(
            auth,
            benchmark_run_id,
            provider=provider,
            model=str(result.get("model") or ""),
            label=label,
            note=note,
        )
        return asdict(saved)

    def compare_models(
        self,
        credential: str,
        conversation_id: str,
        payload: dict[str, Any],
    ) -> dict:
        auth = self._auth(credential)
        text = str(payload.get("text") or "").strip()
        mode = str(payload.get("mode") or "STANDARD").upper()
        if not text:
            raise APIError(400, "TEXT_REQUIRED")

        benchmark_case_id = str(payload.get("benchmark_case_id") or "").strip()
        benchmark_case = None
        if benchmark_case_id:
            from pro_beta.benchmark_cases import (
                BENCHMARK_VERSION,
                get_benchmark_case,
            )

            benchmark_case = get_benchmark_case(benchmark_case_id)
            if benchmark_case is None:
                raise APIError(400, "BENCHMARK_CASE_UNKNOWN")
            if text != benchmark_case["prompt"]:
                raise APIError(400, "BENCHMARK_PROMPT_MISMATCH")
        else:
            BENCHMARK_VERSION = None

        providers = [
            (
                "gemini",
                str(payload.get("gemini_api_key") or "").strip(),
                str(payload.get("gemini_model") or "gemini-3.8-flash").strip(),
            ),
            (
                "claude",
                str(payload.get("claude_api_key") or "").strip(),
                str(payload.get("claude_model") or "claude-sonnet-4-5").strip(),
            ),
            (
                "openai",
                str(payload.get("openai_api_key") or "").strip(),
                str(payload.get("openai_model") or "gpt-5.6-terra").strip(),
            ),
        ]
        missing = [name for name, key, _ in providers if not key]
        if missing:
            raise APIError(
                400,
                "COMPARE_API_KEYS_REQUIRED_" + "_".join(name.upper() for name in missing),
            )

        try:
            self.service.get_conversation(auth, conversation_id)
            if benchmark_case is None:
                history = [
                    asdict(message)
                    for message in self.service.list_messages(auth, conversation_id)
                ]
                hawm_snapshot = self.service.latest_hawm_snapshot(auth, conversation_id)
            else:
                history = []
                hawm_snapshot = None
        except NotFoundError as exc:
            raise APIError(404, str(exc)) from exc
        except OwnershipError as exc:
            raise APIError(403, str(exc)) from exc

        from pro_beta.model_provider import (
            ProviderError,
            claude_call,
            gemini_call,
            openai_call,
        )

        calls = {
            "gemini": gemini_call,
            "claude": claude_call,
            "openai": openai_call,
        }
        completed: list[dict[str, Any]] = []
        failed: list[dict[str, Any]] = []
        for name, api_key, model in providers:
            started = time.perf_counter()
            try:
                result = calls[name](
                    api_key=api_key,
                    model=model,
                    text=text,
                    mode=mode,
                    history=history,
                    hawm_state=(
                        hawm_snapshot.state if hawm_snapshot is not None else None
                    ),
                )
                elapsed_ms = round((time.perf_counter() - started) * 1000)
                completed.append({**result, "elapsed_ms": elapsed_ms})
            except ProviderError as exc:
                elapsed_ms = round((time.perf_counter() - started) * 1000)
                failed.append(
                    {
                        "provider": name,
                        "model": model,
                        "error": str(exc),
                        "elapsed_ms": elapsed_ms,
                    }
                )

        if not completed:
            joined = "_".join(
                f"{row['provider'].upper()}_{row['error']}" for row in failed
            )
            raise APIError(502, "COMPARE_ALL_PROVIDERS_FAILED_" + joined)

        persisted_mode = completed[0]["mode"]
        user_message = self.service.save_user_message(
            auth, conversation_id, text, persisted_mode
        )
        model_messages = []
        for result in completed:
            saved = self.service.save_model_reply(
                auth,
                conversation_id,
                result["text"],
                result["mode"],
                provider=result["provider"],
                model=result["model"],
            )
            model_messages.append(asdict(saved))

        benchmark_run = None
        if benchmark_case is not None:
            benchmark_run = self.service.save_benchmark_run(
                auth,
                conversation_id,
                benchmark_version=BENCHMARK_VERSION,
                case_id=benchmark_case_id,
                benchmark_type="FIXED_NL_BENCHMARK_ISOLATED",
                context_boundary="ISOLATED_NO_CONVERSATION_HISTORY_NO_HAWM",
                expected_control_state=benchmark_case["expected_control_state"],
                invariant=benchmark_case["invariant"],
                mode=persisted_mode,
                status=(
                    "COMPLETE"
                    if not failed
                    else "PARTIAL_PROVIDER_FAILURE"
                ),
                results=completed,
                failed_providers=failed,
            )

        return {
            "benchmark_type": (
                "FIXED_NL_BENCHMARK_ISOLATED"
                if benchmark_case is not None
                else "SAME_PROMPT_SAME_HISTORY_SAME_HAWM"
            ),
            "benchmark_case_id": benchmark_case_id or None,
            "benchmark_version": BENCHMARK_VERSION,
            "benchmark_expected_control_state": (
                benchmark_case["expected_control_state"]
                if benchmark_case is not None
                else None
            ),
            "benchmark_invariant": (
                benchmark_case["invariant"]
                if benchmark_case is not None
                else None
            ),
            "benchmark_context_boundary": (
                "ISOLATED_NO_CONVERSATION_HISTORY_NO_HAWM"
                if benchmark_case is not None
                else "USES_CURRENT_CONVERSATION_HISTORY_AND_HAWM"
            ),
            "benchmark_status": "COMPLETE" if not failed else "PARTIAL_PROVIDER_FAILURE",
            "benchmark_run": (
                asdict(benchmark_run) if benchmark_run is not None else None
            ),
            "user_message": asdict(user_message),
            "model_messages": model_messages,
            "results": completed,
            "failed_providers": failed,
            "authority": "MODEL_REPLY_UNCHECKED",
            "cfc_status": "NOT_CONNECTED_C2",
            "api_keys_persisted": False,
        }

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
