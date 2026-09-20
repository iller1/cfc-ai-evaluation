from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from pro_beta.auth_boundary import AuthContext
from pro_beta.contracts import (
    AuditReportRecord,
    CFCRun,
    Conversation,
    HAWMSnapshot,
    Message,
    Workspace,
    new_id,
)


class PersistencePort(Protocol):
    def create_workspace(self, user_id: str, workspace: Workspace) -> Workspace: ...
    def list_workspaces(self, user_id: str) -> list[Workspace]: ...
    def create_conversation(
        self, user_id: str, conversation: Conversation
    ) -> Conversation: ...
    def list_conversations(
        self, user_id: str, workspace_id: str
    ) -> list[Conversation]: ...
    def get_conversation(
        self, user_id: str, conversation_id: str
    ) -> Conversation: ...
    def append_message(self, user_id: str, message: Message) -> Message: ...
    def list_messages(
        self, user_id: str, conversation_id: str
    ) -> list[Message]: ...
    def add_hawm_snapshot(
        self, user_id: str, snapshot: HAWMSnapshot
    ) -> HAWMSnapshot: ...
    def list_hawm_snapshots(
        self, user_id: str, conversation_id: str
    ) -> list[HAWMSnapshot]: ...
    def add_cfc_run(self, user_id: str, run: CFCRun) -> CFCRun: ...
    def list_cfc_runs(
        self, user_id: str, conversation_id: str
    ) -> list[CFCRun]: ...
    def add_audit_report(
        self, user_id: str, report: AuditReportRecord
    ) -> AuditReportRecord: ...


@dataclass(frozen=True)
class ProBetaService:
    """Application layer for authenticated Pro Beta operations.

    The caller supplies an AuthContext produced by AuthBoundary. Public methods
    intentionally do not accept an arbitrary user_id, so callers cannot select
    another account by passing a different identifier.
    """

    persistence: PersistencePort

    def create_workspace(self, auth: AuthContext, name: str) -> Workspace:
        workspace = Workspace(
            workspace_id=new_id("ws"),
            user_id=auth.user_id,
            name=name.strip() or "Untitled workspace",
        )
        return self.persistence.create_workspace(auth.user_id, workspace)

    def list_workspaces(self, auth: AuthContext) -> list[Workspace]:
        return self.persistence.list_workspaces(auth.user_id)

    def create_conversation(
        self,
        auth: AuthContext,
        workspace_id: str,
        title: str,
    ) -> Conversation:
        conversation = Conversation(
            conversation_id=new_id("conv"),
            workspace_id=workspace_id,
            title=title.strip() or "Untitled conversation",
        )
        return self.persistence.create_conversation(
            auth.user_id, conversation
        )

    def list_conversations(
        self, auth: AuthContext, workspace_id: str
    ) -> list[Conversation]:
        return self.persistence.list_conversations(auth.user_id, workspace_id)

    def get_conversation(
        self, auth: AuthContext, conversation_id: str
    ) -> Conversation:
        return self.persistence.get_conversation(
            auth.user_id, conversation_id
        )

    def save_user_message(
        self,
        auth: AuthContext,
        conversation_id: str,
        content: str,
        mode: str,
    ) -> Message:
        message = Message(
            message_id=new_id("msg"),
            conversation_id=conversation_id,
            role="user",
            content=content,
            authority="USER_INPUT",
            cfc_status="NOT_APPLICABLE",
            mode=mode,
        )
        return self.persistence.append_message(auth.user_id, message)

    def save_model_reply(
        self,
        auth: AuthContext,
        conversation_id: str,
        content: str,
        mode: str,
    ) -> Message:
        message = Message(
            message_id=new_id("msg"),
            conversation_id=conversation_id,
            role="assistant",
            content=content,
            authority="MODEL_REPLY_UNCHECKED",
            cfc_status="NOT_CONNECTED_C2",
            mode=mode,
        )
        return self.persistence.append_message(auth.user_id, message)

    def list_messages(
        self, auth: AuthContext, conversation_id: str
    ) -> list[Message]:
        return self.persistence.list_messages(
            auth.user_id, conversation_id
        )

    def save_hawm_snapshot(
        self,
        auth: AuthContext,
        conversation_id: str,
        state: dict,
        last_verified_state: str,
    ) -> HAWMSnapshot:
        snapshot = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=conversation_id,
            state=state,
            last_verified_state=last_verified_state,
        )
        return self.persistence.add_hawm_snapshot(
            auth.user_id, snapshot
        )

    def latest_hawm_snapshot(
        self, auth: AuthContext, conversation_id: str
    ) -> HAWMSnapshot | None:
        snapshots = self.persistence.list_hawm_snapshots(
            auth.user_id, conversation_id
        )
        return snapshots[-1] if snapshots else None

    def save_cfc_run(
        self,
        auth: AuthContext,
        conversation_id: str,
        *,
        case_id: str,
        controller_anchor: str,
        controller_result: dict,
        presentation: dict,
        replay_matches_reference: bool | None = None,
    ) -> CFCRun:
        run = CFCRun(
            run_id=new_id("cfc"),
            conversation_id=conversation_id,
            case_id=case_id,
            controller_anchor=controller_anchor,
            controller_result=controller_result,
            presentation=presentation,
            replay_matches_reference=replay_matches_reference,
        )
        return self.persistence.add_cfc_run(auth.user_id, run)

    def latest_cfc_run(
        self, auth: AuthContext, conversation_id: str
    ) -> CFCRun | None:
        runs = self.persistence.list_cfc_runs(
            auth.user_id, conversation_id
        )
        return runs[-1] if runs else None


    def save_audit_report(
        self,
        auth: AuthContext,
        conversation_id: str,
        *,
        cfc_run_id: str | None,
        status: str,
        artifact_path: str | None = None,
    ) -> AuditReportRecord:
        report = AuditReportRecord(
            report_id=new_id("report"),
            conversation_id=conversation_id,
            cfc_run_id=cfc_run_id,
            status=status,
            artifact_path=artifact_path,
        )
        return self.persistence.add_audit_report(auth.user_id, report)
