from __future__ import annotations

from dataclasses import replace
from typing import Dict, List

from pro_beta.contracts import (
    AuditReportRecord,
    BenchmarkManualLabel,
    BenchmarkRun,
    CFCRun,
    FoundingBetaMeasurement,
    Conversation,
    HAWMSnapshot,
    Message,
    UsageEvent,
    UserAccount,
    Workspace,
)


class NotFoundError(KeyError):
    """Requested record does not exist."""


class OwnershipError(PermissionError):
    """Requested record exists but is not owned by the current user."""


class InMemoryPersistence:
    """Reference persistence layer for Pro Beta v0.1.

    This is deliberately not the production database implementation. It defines
    ownership and write/read contracts that a later PostgreSQL adapter must
    preserve exactly.
    """

    def __init__(self) -> None:
        self.users: Dict[str, UserAccount] = {}
        self.workspaces: Dict[str, Workspace] = {}
        self.conversations: Dict[str, Conversation] = {}
        self.messages: Dict[str, Message] = {}
        self.hawm_snapshots: Dict[str, HAWMSnapshot] = {}
        self.cfc_runs: Dict[str, CFCRun] = {}
        self.founding_beta_measurements: Dict[str, FoundingBetaMeasurement] = {}
        self.audit_reports: Dict[str, AuditReportRecord] = {}
        self.benchmark_runs: Dict[str, BenchmarkRun] = {}
        self.benchmark_manual_labels: Dict[str, BenchmarkManualLabel] = {}
        self.usage_events: Dict[str, UsageEvent] = {}

    # ---------- user/account ----------

    def create_user(self, account: UserAccount) -> UserAccount:
        if account.user_id in self.users:
            raise ValueError("USER_ALREADY_EXISTS")
        if any(
            u.external_auth_subject == account.external_auth_subject
            for u in self.users.values()
        ):
            raise ValueError("AUTH_SUBJECT_ALREADY_EXISTS")
        self.users[account.user_id] = account
        return account

    def get_user(self, user_id: str) -> UserAccount:
        try:
            return self.users[user_id]
        except KeyError as exc:
            raise NotFoundError("USER_NOT_FOUND") from exc

    def get_user_by_external_auth_subject(
        self, external_auth_subject: str
    ) -> UserAccount:
        for account in self.users.values():
            if account.external_auth_subject == external_auth_subject:
                return account
        raise NotFoundError("AUTH_SUBJECT_NOT_FOUND")

    # ---------- ownership helpers ----------

    def _owned_workspace(self, user_id: str, workspace_id: str) -> Workspace:
        try:
            workspace = self.workspaces[workspace_id]
        except KeyError as exc:
            raise NotFoundError("WORKSPACE_NOT_FOUND") from exc
        if workspace.user_id != user_id:
            raise OwnershipError("WORKSPACE_NOT_OWNED")
        return workspace

    def _owned_conversation(self, user_id: str, conversation_id: str) -> Conversation:
        try:
            conversation = self.conversations[conversation_id]
        except KeyError as exc:
            raise NotFoundError("CONVERSATION_NOT_FOUND") from exc
        self._owned_workspace(user_id, conversation.workspace_id)
        return conversation

    # ---------- workspaces ----------

    def create_workspace(self, user_id: str, workspace: Workspace) -> Workspace:
        self.get_user(user_id)
        if workspace.user_id != user_id:
            raise OwnershipError("WORKSPACE_OWNER_MISMATCH")
        if workspace.workspace_id in self.workspaces:
            raise ValueError("WORKSPACE_ALREADY_EXISTS")
        self.workspaces[workspace.workspace_id] = workspace
        return workspace

    def list_workspaces(self, user_id: str) -> List[Workspace]:
        self.get_user(user_id)
        return [w for w in self.workspaces.values() if w.user_id == user_id]

    def get_workspace(self, user_id: str, workspace_id: str) -> Workspace:
        return self._owned_workspace(user_id, workspace_id)

    def rename_workspace(self, user_id: str, workspace_id: str, name: str) -> Workspace:
        current = self._owned_workspace(user_id, workspace_id)
        updated = replace(current, name=name)
        self.workspaces[workspace_id] = updated
        return updated

    # ---------- conversations ----------

    def create_conversation(
        self, user_id: str, conversation: Conversation
    ) -> Conversation:
        self._owned_workspace(user_id, conversation.workspace_id)
        if conversation.conversation_id in self.conversations:
            raise ValueError("CONVERSATION_ALREADY_EXISTS")
        self.conversations[conversation.conversation_id] = conversation
        return conversation

    def list_conversations(
        self, user_id: str, workspace_id: str
    ) -> List[Conversation]:
        self._owned_workspace(user_id, workspace_id)
        return [
            c
            for c in self.conversations.values()
            if c.workspace_id == workspace_id
        ]

    def get_conversation(
        self, user_id: str, conversation_id: str
    ) -> Conversation:
        return self._owned_conversation(user_id, conversation_id)

    # ---------- conversation children ----------

    def append_message(self, user_id: str, message: Message) -> Message:
        self._owned_conversation(user_id, message.conversation_id)
        if message.message_id in self.messages:
            raise ValueError("MESSAGE_ALREADY_EXISTS")
        self.messages[message.message_id] = message
        return message

    def list_messages(self, user_id: str, conversation_id: str) -> List[Message]:
        self._owned_conversation(user_id, conversation_id)
        return [
            m
            for m in self.messages.values()
            if m.conversation_id == conversation_id
        ]

    def add_hawm_snapshot(
        self, user_id: str, snapshot: HAWMSnapshot
    ) -> HAWMSnapshot:
        self._owned_conversation(user_id, snapshot.conversation_id)
        if snapshot.snapshot_id in self.hawm_snapshots:
            raise ValueError("HAWM_SNAPSHOT_ALREADY_EXISTS")
        self.hawm_snapshots[snapshot.snapshot_id] = snapshot
        return snapshot

    def list_hawm_snapshots(
        self, user_id: str, conversation_id: str
    ) -> List[HAWMSnapshot]:
        self._owned_conversation(user_id, conversation_id)
        return [
            s
            for s in self.hawm_snapshots.values()
            if s.conversation_id == conversation_id
        ]

    def add_cfc_run(self, user_id: str, run: CFCRun) -> CFCRun:
        self._owned_conversation(user_id, run.conversation_id)
        if run.run_id in self.cfc_runs:
            raise ValueError("CFC_RUN_ALREADY_EXISTS")
        self.cfc_runs[run.run_id] = run
        return run

    def list_cfc_runs(self, user_id: str, conversation_id: str) -> List[CFCRun]:
        self._owned_conversation(user_id, conversation_id)
        return [
            r
            for r in self.cfc_runs.values()
            if r.conversation_id == conversation_id
        ]

    def add_audit_report(
        self, user_id: str, report: AuditReportRecord
    ) -> AuditReportRecord:
        self._owned_conversation(user_id, report.conversation_id)
        if report.cfc_run_id is not None:
            try:
                run = self.cfc_runs[report.cfc_run_id]
            except KeyError as exc:
                raise NotFoundError("CFC_RUN_NOT_FOUND") from exc
            if run.conversation_id != report.conversation_id:
                raise OwnershipError("CFC_RUN_CONVERSATION_MISMATCH")
        if report.report_id in self.audit_reports:
            raise ValueError("AUDIT_REPORT_ALREADY_EXISTS")
        self.audit_reports[report.report_id] = report
        return report

    # ---------- benchmark runs ----------

    def add_benchmark_run(
        self, user_id: str, run: BenchmarkRun
    ) -> BenchmarkRun:
        self._owned_conversation(user_id, run.conversation_id)
        if run.benchmark_run_id in self.benchmark_runs:
            raise ValueError("BENCHMARK_RUN_ALREADY_EXISTS")
        self.benchmark_runs[run.benchmark_run_id] = run
        return run

    def list_benchmark_runs(
        self, user_id: str, conversation_id: str
    ) -> List[BenchmarkRun]:
        self._owned_conversation(user_id, conversation_id)
        return [
            r
            for r in self.benchmark_runs.values()
            if r.conversation_id == conversation_id
        ]

    def get_benchmark_run(
        self, user_id: str, benchmark_run_id: str
    ) -> BenchmarkRun:
        try:
            run = self.benchmark_runs[benchmark_run_id]
        except KeyError as exc:
            raise NotFoundError("BENCHMARK_RUN_NOT_FOUND") from exc
        self._owned_conversation(user_id, run.conversation_id)
        return run

    def upsert_benchmark_manual_label(
        self, user_id: str, label: BenchmarkManualLabel
    ) -> BenchmarkManualLabel:
        try:
            run = self.benchmark_runs[label.benchmark_run_id]
        except KeyError as exc:
            raise NotFoundError("BENCHMARK_RUN_NOT_FOUND") from exc
        self._owned_conversation(user_id, run.conversation_id)
        existing_id = None
        for label_id, current in self.benchmark_manual_labels.items():
            if (
                current.benchmark_run_id == label.benchmark_run_id
                and current.provider == label.provider
            ):
                existing_id = label_id
                break
        if existing_id is not None:
            self.benchmark_manual_labels.pop(existing_id)
        self.benchmark_manual_labels[label.label_id] = label
        return label

    def list_benchmark_manual_labels(
        self, user_id: str, benchmark_run_id: str
    ) -> List[BenchmarkManualLabel]:
        try:
            run = self.benchmark_runs[benchmark_run_id]
        except KeyError as exc:
            raise NotFoundError("BENCHMARK_RUN_NOT_FOUND") from exc
        self._owned_conversation(user_id, run.conversation_id)
        return [
            label
            for label in self.benchmark_manual_labels.values()
            if label.benchmark_run_id == benchmark_run_id
        ]

    # ---------- founding beta measurements ----------

    def add_founding_beta_measurement(
        self, user_id: str, item: FoundingBetaMeasurement
    ) -> FoundingBetaMeasurement:
        self._owned_workspace(user_id, item.workspace_id)
        if item.measurement_id in self.founding_beta_measurements:
            raise ValueError("FOUNDING_BETA_MEASUREMENT_ALREADY_EXISTS")
        self.founding_beta_measurements[item.measurement_id] = item
        return item

    def list_founding_beta_measurements(
        self, user_id: str, workspace_id: str
    ) -> List[FoundingBetaMeasurement]:
        self._owned_workspace(user_id, workspace_id)
        return [
            item
            for item in self.founding_beta_measurements.values()
            if item.workspace_id == workspace_id
        ]

    # ---------- usage ----------

    def add_usage_event(self, user_id: str, event: UsageEvent) -> UsageEvent:
        self.get_user(user_id)
        if event.user_id != user_id:
            raise OwnershipError("USAGE_EVENT_OWNER_MISMATCH")
        if event.event_id in self.usage_events:
            raise ValueError("USAGE_EVENT_ALREADY_EXISTS")
        self.usage_events[event.event_id] = event
        return event
