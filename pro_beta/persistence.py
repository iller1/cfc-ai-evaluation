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
    HAWMSnapshotIdentity,
    EvidenceSetRegistration,
    EvidenceProvenanceReceipt,
    EvidenceDependencyReceipt,
    ExecutionIntentRegistration,
    ExecutionReceiptRecord,
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
        self.hawm_snapshot_identities: Dict[str, HAWMSnapshotIdentity] = {}
        self.evidence_set_registrations: Dict[str, EvidenceSetRegistration] = {}
        self.evidence_provenance_receipts: Dict[str, EvidenceProvenanceReceipt] = {}
        self.evidence_dependency_receipts: Dict[str, EvidenceDependencyReceipt] = {}
        self.execution_intents: Dict[str, ExecutionIntentRegistration] = {}
        self.execution_receipts: Dict[str, ExecutionReceiptRecord] = {}
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

    def add_hawm_snapshot_identity(
        self, user_id: str, identity: HAWMSnapshotIdentity
    ) -> HAWMSnapshotIdentity:
        self._owned_conversation(user_id, identity.conversation_id)
        snapshot = self.hawm_snapshots.get(identity.snapshot_id)
        if snapshot is None:
            raise NotFoundError("HAWM_SNAPSHOT_NOT_FOUND")
        if snapshot.conversation_id != identity.conversation_id:
            raise OwnershipError("HAWM_SNAPSHOT_CONVERSATION_MISMATCH")
        if identity.snapshot_id in self.hawm_snapshot_identities:
            raise ValueError("HAWM_SNAPSHOT_IDENTITY_ALREADY_EXISTS")
        self.hawm_snapshot_identities[identity.snapshot_id] = identity
        return identity

    def get_hawm_snapshot_identity(
        self, user_id: str, conversation_id: str, snapshot_id: str
    ) -> HAWMSnapshotIdentity:
        self._owned_conversation(user_id, conversation_id)
        try:
            identity = self.hawm_snapshot_identities[snapshot_id]
        except KeyError as exc:
            raise NotFoundError("HAWM_SNAPSHOT_IDENTITY_NOT_FOUND") from exc
        if identity.conversation_id != conversation_id:
            raise OwnershipError("HAWM_SNAPSHOT_IDENTITY_CONVERSATION_MISMATCH")
        return identity

    def add_evidence_set_registration(
        self, user_id: str, registration: EvidenceSetRegistration
    ) -> EvidenceSetRegistration:
        self._owned_conversation(user_id, registration.conversation_id)
        snapshot = self.hawm_snapshots.get(registration.snapshot_id)
        if snapshot is None:
            raise NotFoundError("HAWM_SNAPSHOT_NOT_FOUND")
        if snapshot.conversation_id != registration.conversation_id:
            raise OwnershipError("HAWM_SNAPSHOT_CONVERSATION_MISMATCH")
        identity = self.hawm_snapshot_identities.get(registration.snapshot_id)
        if identity is None:
            raise NotFoundError("HAWM_SNAPSHOT_IDENTITY_NOT_FOUND")
        if identity.conversation_id != registration.conversation_id:
            raise OwnershipError("HAWM_SNAPSHOT_IDENTITY_CONVERSATION_MISMATCH")
        if registration.state_id != identity.state_id:
            raise ValueError("EVIDENCE_REGISTRATION_STATE_IDENTITY_MISMATCH")
        if registration.state_id != registration.snapshot_id:
            raise ValueError("EVIDENCE_REGISTRATION_STATE_ID_MISMATCH")
        if registration.snapshot_id in self.evidence_set_registrations:
            raise ValueError("EVIDENCE_SET_REGISTRATION_ALREADY_EXISTS")
        self.evidence_set_registrations[registration.snapshot_id] = registration
        return registration

    def get_evidence_set_registration(
        self, user_id: str, conversation_id: str, snapshot_id: str
    ) -> EvidenceSetRegistration:
        self._owned_conversation(user_id, conversation_id)
        try:
            registration = self.evidence_set_registrations[snapshot_id]
        except KeyError as exc:
            raise NotFoundError("EVIDENCE_SET_REGISTRATION_NOT_FOUND") from exc
        if registration.conversation_id != conversation_id:
            raise OwnershipError("EVIDENCE_SET_REGISTRATION_CONVERSATION_MISMATCH")
        return registration

    def add_evidence_provenance_receipt(
        self, user_id: str, receipt: EvidenceProvenanceReceipt
    ) -> EvidenceProvenanceReceipt:
        self._owned_conversation(user_id, receipt.conversation_id)
        registration = self.evidence_set_registrations.get(receipt.snapshot_id)
        if registration is None:
            raise NotFoundError("EVIDENCE_SET_REGISTRATION_NOT_FOUND")
        if registration.conversation_id != receipt.conversation_id:
            raise OwnershipError("EVIDENCE_SET_REGISTRATION_CONVERSATION_MISMATCH")
        if receipt.state_id != registration.state_id:
            raise ValueError("EVIDENCE_PROVENANCE_RECEIPT_STATE_MISMATCH")
        if receipt.receipt_id in self.evidence_provenance_receipts:
            raise ValueError("EVIDENCE_PROVENANCE_RECEIPT_ALREADY_EXISTS")
        if any(
            current.snapshot_id == receipt.snapshot_id
            and current.evidence_id == receipt.evidence_id
            for current in self.evidence_provenance_receipts.values()
        ):
            raise ValueError("EVIDENCE_PROVENANCE_RECEIPT_FOR_EVIDENCE_ALREADY_EXISTS")
        self.evidence_provenance_receipts[receipt.receipt_id] = receipt
        return receipt

    def list_evidence_provenance_receipts(
        self, user_id: str, conversation_id: str, snapshot_id: str
    ) -> List[EvidenceProvenanceReceipt]:
        self._owned_conversation(user_id, conversation_id)
        registration = self.get_evidence_set_registration(
            user_id, conversation_id, snapshot_id
        )
        return [
            receipt
            for receipt in self.evidence_provenance_receipts.values()
            if receipt.snapshot_id == registration.snapshot_id
        ]

    def add_evidence_dependency_receipt(
        self, user_id: str, receipt: EvidenceDependencyReceipt
    ) -> EvidenceDependencyReceipt:
        self._owned_conversation(user_id, receipt.conversation_id)
        registration = self.evidence_set_registrations.get(receipt.snapshot_id)
        if registration is None:
            raise NotFoundError("EVIDENCE_SET_REGISTRATION_NOT_FOUND")
        if registration.conversation_id != receipt.conversation_id:
            raise OwnershipError("EVIDENCE_SET_REGISTRATION_CONVERSATION_MISMATCH")
        if receipt.state_id != registration.state_id:
            raise ValueError("EVIDENCE_DEPENDENCY_RECEIPT_STATE_MISMATCH")
        if receipt.snapshot_id in self.evidence_dependency_receipts:
            raise ValueError("EVIDENCE_DEPENDENCY_RECEIPT_ALREADY_EXISTS")
        self.evidence_dependency_receipts[receipt.snapshot_id] = receipt
        return receipt

    def get_evidence_dependency_receipt(
        self, user_id: str, conversation_id: str, snapshot_id: str
    ) -> EvidenceDependencyReceipt:
        self._owned_conversation(user_id, conversation_id)
        self.get_evidence_set_registration(user_id, conversation_id, snapshot_id)
        try:
            receipt = self.evidence_dependency_receipts[snapshot_id]
        except KeyError as exc:
            raise NotFoundError("EVIDENCE_DEPENDENCY_RECEIPT_NOT_FOUND") from exc
        if receipt.conversation_id != conversation_id:
            raise OwnershipError("EVIDENCE_DEPENDENCY_RECEIPT_CONVERSATION_MISMATCH")
        return receipt

    def add_cfc_run(self, user_id: str, run: CFCRun) -> CFCRun:
        self._owned_conversation(user_id, run.conversation_id)
        if run.hawm_snapshot_id is not None:
            snapshot = self.hawm_snapshots.get(run.hawm_snapshot_id)
            if snapshot is None:
                raise NotFoundError("HAWM_SNAPSHOT_NOT_FOUND")
            if snapshot.conversation_id != run.conversation_id:
                raise OwnershipError("HAWM_SNAPSHOT_CONVERSATION_MISMATCH")
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

    def add_execution_intent(
        self, user_id: str, intent: ExecutionIntentRegistration
    ) -> ExecutionIntentRegistration:
        self._owned_conversation(user_id, intent.conversation_id)
        run = self.cfc_runs.get(intent.controller_run_id)
        if run is None:
            raise NotFoundError("CFC_RUN_NOT_FOUND")
        if run.conversation_id != intent.conversation_id:
            raise OwnershipError("CFC_RUN_CONVERSATION_MISMATCH")
        if run.hawm_snapshot_id is None:
            raise ValueError("EXECUTION_INTENT_REQUIRES_BOUND_CFC_RUN")
        if run.hawm_snapshot_id != intent.state_id:
            raise ValueError("EXECUTION_INTENT_STATE_RUN_MISMATCH")
        identity = self.hawm_snapshot_identities.get(intent.state_id)
        if identity is None:
            raise NotFoundError("HAWM_SNAPSHOT_IDENTITY_NOT_FOUND")
        if identity.conversation_id != intent.conversation_id:
            raise OwnershipError("HAWM_SNAPSHOT_IDENTITY_CONVERSATION_MISMATCH")
        if intent.state_version != identity.registered_snapshot_fingerprint:
            raise ValueError("EXECUTION_INTENT_STATE_VERSION_MISMATCH")
        if intent.intent_id in self.execution_intents:
            raise ValueError("EXECUTION_INTENT_ALREADY_EXISTS")
        if any(
            row.conversation_id == intent.conversation_id
            and row.idempotency_key == intent.idempotency_key
            for row in self.execution_intents.values()
        ):
            raise ValueError("EXECUTION_IDEMPOTENCY_KEY_ALREADY_REGISTERED")
        self.execution_intents[intent.intent_id] = intent
        return intent

    def list_execution_intents(
        self, user_id: str, conversation_id: str
    ) -> List[ExecutionIntentRegistration]:
        self._owned_conversation(user_id, conversation_id)
        return [
            row
            for row in self.execution_intents.values()
            if row.conversation_id == conversation_id
        ]

    def get_execution_intent(
        self, user_id: str, conversation_id: str, intent_id: str
    ) -> ExecutionIntentRegistration:
        self._owned_conversation(user_id, conversation_id)
        try:
            intent = self.execution_intents[intent_id]
        except KeyError as exc:
            raise NotFoundError("EXECUTION_INTENT_NOT_FOUND") from exc
        if intent.conversation_id != conversation_id:
            raise OwnershipError("EXECUTION_INTENT_CONVERSATION_MISMATCH")
        return intent

    def add_execution_receipt(
        self, user_id: str, receipt: ExecutionReceiptRecord
    ) -> ExecutionReceiptRecord:
        self._owned_conversation(user_id, receipt.conversation_id)
        intent = self.get_execution_intent(
            user_id, receipt.conversation_id, receipt.intent_id
        )
        exact = (
            receipt.action_id == intent.action_id
            and receipt.controller_run_id == intent.controller_run_id
            and receipt.state_id == intent.state_id
            and receipt.state_version == intent.state_version
            and receipt.idempotency_key == intent.idempotency_key
        )
        if not exact:
            raise ValueError("EXECUTION_RECEIPT_INTENT_BINDING_MISMATCH")
        if receipt.receipt_id in self.execution_receipts:
            raise ValueError("EXECUTION_RECEIPT_ALREADY_EXISTS")
        if any(
            row.intent_id == receipt.intent_id
            for row in self.execution_receipts.values()
        ):
            raise ValueError("EXECUTION_INTENT_RECEIPT_ALREADY_EXISTS")
        if not receipt.attempted:
            raise ValueError("EXECUTION_RECEIPT_REQUIRES_ATTEMPT")
        self.execution_receipts[receipt.receipt_id] = receipt
        return receipt

    def list_execution_receipts(
        self, user_id: str, conversation_id: str
    ) -> List[ExecutionReceiptRecord]:
        self._owned_conversation(user_id, conversation_id)
        return [
            row
            for row in self.execution_receipts.values()
            if row.conversation_id == conversation_id
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

    def delete_founding_beta_measurements(
        self, user_id: str, workspace_id: str
    ) -> int:
        self._owned_workspace(user_id, workspace_id)
        ids = [
            measurement_id
            for measurement_id, item in self.founding_beta_measurements.items()
            if item.workspace_id == workspace_id
        ]
        for measurement_id in ids:
            self.founding_beta_measurements.pop(measurement_id)
        return len(ids)

    # ---------- usage ----------

    def add_usage_event(self, user_id: str, event: UsageEvent) -> UsageEvent:
        self.get_user(user_id)
        if event.user_id != user_id:
            raise OwnershipError("USAGE_EVENT_OWNER_MISMATCH")
        if event.event_id in self.usage_events:
            raise ValueError("USAGE_EVENT_ALREADY_EXISTS")
        self.usage_events[event.event_id] = event
        return event
