from __future__ import annotations

from dataclasses import asdict, dataclass
import copy
from typing import Protocol

from control_stack.state_integrity import state_fingerprint
from pro_beta.auth_boundary import AuthContext
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
    ExecutionReceiptRecord,
    Message,
    Workspace,
    new_id,
)


HAWM_STATE_IDENTITY_ADAPTER_VERSION = "HAWM_STATE_IDENTITY_ADAPTER_V0_1"
HAWM_STATE_IDENTITY_CASE_ID = "HAWM_PRO_BETA_STATE"
HAWM_STATE_IDENTITY_ARM_ID = "HAWM_WORKING_STATE"
EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION = (
    "EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_V0_1"
)
EXECUTION_GATE_RECEIPT_ADAPTER_VERSION = (
    "EXECUTION_GATE_RECEIPT_ADAPTER_V0_1"
)


class PersistencePort(Protocol):
    def create_workspace(self, user_id: str, workspace: Workspace) -> Workspace: ...
    def list_workspaces(self, user_id: str) -> list[Workspace]: ...
    def get_workspace(self, user_id: str, workspace_id: str) -> Workspace: ...
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
    def add_hawm_snapshot_identity(
        self, user_id: str, identity: HAWMSnapshotIdentity
    ) -> HAWMSnapshotIdentity: ...
    def get_hawm_snapshot_identity(
        self, user_id: str, conversation_id: str, snapshot_id: str
    ) -> HAWMSnapshotIdentity: ...
    def add_evidence_set_registration(
        self, user_id: str, registration: EvidenceSetRegistration
    ) -> EvidenceSetRegistration: ...
    def get_evidence_set_registration(
        self, user_id: str, conversation_id: str, snapshot_id: str
    ) -> EvidenceSetRegistration: ...
    def add_evidence_provenance_receipt(
        self, user_id: str, receipt: EvidenceProvenanceReceipt
    ) -> EvidenceProvenanceReceipt: ...
    def list_evidence_provenance_receipts(
        self, user_id: str, conversation_id: str, snapshot_id: str
    ) -> list[EvidenceProvenanceReceipt]: ...
    def add_evidence_dependency_receipt(
        self, user_id: str, receipt: EvidenceDependencyReceipt
    ) -> EvidenceDependencyReceipt: ...
    def get_evidence_dependency_receipt(
        self, user_id: str, conversation_id: str, snapshot_id: str
    ) -> EvidenceDependencyReceipt: ...
    def add_execution_receipt(
        self, user_id: str, receipt: ExecutionReceiptRecord
    ) -> ExecutionReceiptRecord: ...
    def list_execution_receipts(
        self, user_id: str, conversation_id: str
    ) -> list[ExecutionReceiptRecord]: ...
    def add_cfc_run(self, user_id: str, run: CFCRun) -> CFCRun: ...
    def list_cfc_runs(
        self, user_id: str, conversation_id: str
    ) -> list[CFCRun]: ...
    def add_audit_report(
        self, user_id: str, report: AuditReportRecord
    ) -> AuditReportRecord: ...
    def add_benchmark_run(
        self, user_id: str, run: BenchmarkRun
    ) -> BenchmarkRun: ...
    def list_benchmark_runs(
        self, user_id: str, conversation_id: str
    ) -> list[BenchmarkRun]: ...
    def get_benchmark_run(
        self, user_id: str, benchmark_run_id: str
    ) -> BenchmarkRun: ...
    def upsert_benchmark_manual_label(
        self, user_id: str, label: BenchmarkManualLabel
    ) -> BenchmarkManualLabel: ...
    def list_benchmark_manual_labels(
        self, user_id: str, benchmark_run_id: str
    ) -> list[BenchmarkManualLabel]: ...
    def add_founding_beta_measurement(
        self, user_id: str, item: FoundingBetaMeasurement
    ) -> FoundingBetaMeasurement: ...
    def list_founding_beta_measurements(
        self, user_id: str, workspace_id: str
    ) -> list[FoundingBetaMeasurement]: ...
    def delete_founding_beta_measurements(
        self, user_id: str, workspace_id: str
    ) -> int: ...


@dataclass(frozen=True)
class ProBetaService:
    """Application layer for authenticated Pro Beta operations.

    The caller supplies an AuthContext produced by AuthBoundary. Public methods
    intentionally do not accept an arbitrary user_id, so callers cannot select
    another account by passing a different identifier.
    """

    persistence: PersistencePort

    def save_founding_beta_measurement(
        self,
        auth: AuthContext,
        workspace_id: str,
        *,
        system_version: str,
        workflow_type: str,
        case_id: str,
        cfc_result: str,
        reason_code: str,
        hawm_state: str,
        human_assessment: str,
        final_action: str,
        problem_type: str,
        comment: str | None = None,
    ) -> FoundingBetaMeasurement:
        cfc_result = cfc_result.strip().upper()
        human_assessment = human_assessment.strip().upper()
        problem_type = problem_type.strip().upper()

        if cfc_result not in {"ALLOW", "STOP", "UNRESOLVED"}:
            raise ValueError("FOUNDING_BETA_CFC_RESULT_INVALID")
        if human_assessment not in {"AGREE", "DISAGREE", "UNSURE"}:
            raise ValueError("FOUNDING_BETA_HUMAN_ASSESSMENT_INVALID")
        if problem_type not in {
            "NONE",
            "BUG",
            "USABILITY",
            "FALSE_STOP",
            "FALSE_ALLOW",
            "UPSTREAM_STATE_ISSUE",
        }:
            raise ValueError("FOUNDING_BETA_PROBLEM_TYPE_INVALID")

        required = {
            "system_version": system_version,
            "workflow_type": workflow_type,
            "case_id": case_id,
            "reason_code": reason_code,
            "hawm_state": hawm_state,
            "final_action": final_action,
        }
        if any(not str(value).strip() for value in required.values()):
            raise ValueError("FOUNDING_BETA_REQUIRED_FIELD_MISSING")

        limits = {
            "system_version": (system_version, 128),
            "workflow_type": (workflow_type, 80),
            "case_id": (case_id, 128),
            "reason_code": (reason_code, 1024),
            "hawm_state": (hawm_state, 160),
            "final_action": (final_action, 80),
        }
        if any(len(str(value)) > limit for value, limit in limits.values()):
            raise ValueError("FOUNDING_BETA_FIELD_TOO_LONG")

        clean_comment = None if comment is None else str(comment).strip()
        if clean_comment and len(clean_comment) > 500:
            raise ValueError("FOUNDING_BETA_COMMENT_TOO_LONG")

        item = FoundingBetaMeasurement(
            measurement_id=new_id("fbm"),
            workspace_id=workspace_id,
            system_version=system_version.strip(),
            workflow_type=workflow_type.strip(),
            case_id=case_id.strip(),
            cfc_result=cfc_result,
            reason_code=reason_code.strip(),
            hawm_state=hawm_state.strip(),
            human_assessment=human_assessment,
            final_action=final_action.strip(),
            problem_type=problem_type,
            comment=clean_comment or None,
        )
        return self.persistence.add_founding_beta_measurement(
            auth.user_id, item
        )

    def list_founding_beta_measurements(
        self, auth: AuthContext, workspace_id: str
    ) -> list[FoundingBetaMeasurement]:
        return self.persistence.list_founding_beta_measurements(
            auth.user_id, workspace_id
        )

    def delete_founding_beta_measurements(
        self, auth: AuthContext, workspace_id: str
    ) -> int:
        return self.persistence.delete_founding_beta_measurements(
            auth.user_id, workspace_id
        )

    def create_workspace(self, auth: AuthContext, name: str) -> Workspace:
        workspace = Workspace(
            workspace_id=new_id("ws"),
            user_id=auth.user_id,
            name=name.strip() or "Untitled workspace",
        )
        return self.persistence.create_workspace(auth.user_id, workspace)

    def list_workspaces(self, auth: AuthContext) -> list[Workspace]:
        return self.persistence.list_workspaces(auth.user_id)

    def get_workspace(
        self, auth: AuthContext, workspace_id: str
    ) -> Workspace:
        return self.persistence.get_workspace(auth.user_id, workspace_id)

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
        provider: str | None = None,
        model: str | None = None,
    ) -> Message:
        message = Message(
            message_id=new_id("msg"),
            conversation_id=conversation_id,
            role="assistant",
            content=content,
            authority="MODEL_REPLY_UNCHECKED",
            cfc_status="NOT_CONNECTED_C2",
            mode=mode,
            provider=provider,
            model=model,
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
        previous = self.persistence.list_hawm_snapshots(
            auth.user_id, conversation_id
        )
        snapshot = HAWMSnapshot(
            snapshot_id=new_id("hawm"),
            conversation_id=conversation_id,
            state=state,
            last_verified_state=last_verified_state,
        )
        saved = self.persistence.add_hawm_snapshot(auth.user_id, snapshot)
        identity = HAWMSnapshotIdentity(
            snapshot_id=saved.snapshot_id,
            conversation_id=conversation_id,
            case_id=HAWM_STATE_IDENTITY_CASE_ID,
            arm_id=HAWM_STATE_IDENTITY_ARM_ID,
            state_id=saved.snapshot_id,
            lineage_id=conversation_id,
            previous_state_id=(
                previous[-1].snapshot_id if previous else None
            ),
            registered_snapshot_fingerprint=state_fingerprint(saved.state),
            adapter_version=HAWM_STATE_IDENTITY_ADAPTER_VERSION,
        )
        # If identity persistence fails, this operation fails closed. The
        # snapshot may exist without an anchor, but must never be treated as
        # STATE_VALID until a separately governed identity receipt exists.
        self.persistence.add_hawm_snapshot_identity(auth.user_id, identity)
        return saved

    def latest_hawm_snapshot(
        self, auth: AuthContext, conversation_id: str
    ) -> HAWMSnapshot | None:
        snapshots = self.persistence.list_hawm_snapshots(
            auth.user_id, conversation_id
        )
        return snapshots[-1] if snapshots else None

    def list_hawm_snapshots(
        self, auth: AuthContext, conversation_id: str
    ) -> list[HAWMSnapshot]:
        return self.persistence.list_hawm_snapshots(
            auth.user_id, conversation_id
        )

    def get_hawm_snapshot(
        self, auth: AuthContext, conversation_id: str, snapshot_id: str
    ) -> HAWMSnapshot:
        """Resolve by owned conversation, not by a user-provided unscoped ID."""
        for snapshot in self.persistence.list_hawm_snapshots(
            auth.user_id, conversation_id
        ):
            if snapshot.snapshot_id == snapshot_id:
                return snapshot
        from pro_beta.persistence import NotFoundError
        raise NotFoundError("HAWM_SNAPSHOT_NOT_FOUND")

    def get_hawm_snapshot_identity(
        self, auth: AuthContext, conversation_id: str, snapshot_id: str
    ) -> HAWMSnapshotIdentity:
        return self.persistence.get_hawm_snapshot_identity(
            auth.user_id, conversation_id, snapshot_id
        )

    def register_evidence_set(
        self,
        auth: AuthContext,
        conversation_id: str,
        snapshot_id: str,
        *,
        evidence_set: list[dict],
        missing_evidence: list[str],
    ) -> EvidenceSetRegistration:
        snapshot = self.get_hawm_snapshot(
            auth, conversation_id, snapshot_id
        )
        identity = self.get_hawm_snapshot_identity(
            auth, conversation_id, snapshot_id
        )
        if identity.state_id != snapshot.snapshot_id:
            raise ValueError("EVIDENCE_REGISTRATION_STATE_IDENTITY_MISMATCH")

        from control_stack.evidence_provenance import (
            EVIDENCE_INVALID,
            assess_evidence_provenance,
        )

        probe = assess_evidence_provenance(
            state_id=snapshot.snapshot_id,
            evidence_set=evidence_set,
            provenance_receipts=[],
            dependency_receipt=None,
            missing_evidence=missing_evidence,
            drift_state="NOT_ASSESSED",
        )
        if probe["status"] == EVIDENCE_INVALID:
            raise ValueError(probe["reason"])

        registration = EvidenceSetRegistration(
            registration_id=new_id("evidence_set"),
            snapshot_id=snapshot.snapshot_id,
            conversation_id=conversation_id,
            state_id=snapshot.snapshot_id,
            evidence_set=copy.deepcopy(evidence_set),
            missing_evidence=list(missing_evidence),
            adapter_version=EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION,
        )
        return self.persistence.add_evidence_set_registration(
            auth.user_id, registration
        )

    def get_evidence_set_registration(
        self,
        auth: AuthContext,
        conversation_id: str,
        snapshot_id: str,
    ) -> EvidenceSetRegistration:
        return self.persistence.get_evidence_set_registration(
            auth.user_id, conversation_id, snapshot_id
        )

    def register_evidence_provenance_receipt(
        self,
        auth: AuthContext,
        conversation_id: str,
        snapshot_id: str,
        *,
        evidence_id: str,
        source_id: str,
        status: str,
    ) -> EvidenceProvenanceReceipt:
        registration = self.get_evidence_set_registration(
            auth, conversation_id, snapshot_id
        )
        record = next(
            (
                item
                for item in registration.evidence_set
                if item.get("evidence_id") == evidence_id
            ),
            None,
        )
        if record is None:
            raise ValueError("EVIDENCE_PROVENANCE_EVIDENCE_NOT_REGISTERED")
        if record.get("source_id") != source_id:
            raise ValueError("EVIDENCE_PROVENANCE_SOURCE_MISMATCH")
        if status not in {"ESTABLISHED", "PARTIAL", "UNKNOWN", "INVALID"}:
            raise ValueError("EVIDENCE_PROVENANCE_STATUS_INVALID")

        receipt = EvidenceProvenanceReceipt(
            receipt_id=new_id("evidence_prov"),
            snapshot_id=registration.snapshot_id,
            conversation_id=registration.conversation_id,
            state_id=registration.state_id,
            evidence_id=evidence_id,
            source_id=source_id,
            status=status,
            adapter_version=EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION,
        )
        return self.persistence.add_evidence_provenance_receipt(
            auth.user_id, receipt
        )

    def list_evidence_provenance_receipts(
        self,
        auth: AuthContext,
        conversation_id: str,
        snapshot_id: str,
    ) -> list[EvidenceProvenanceReceipt]:
        return self.persistence.list_evidence_provenance_receipts(
            auth.user_id, conversation_id, snapshot_id
        )

    def register_evidence_dependency_receipt(
        self,
        auth: AuthContext,
        conversation_id: str,
        snapshot_id: str,
        *,
        evidence_ids: list[str],
        failure_domains: dict[str, str | None],
        status: str,
    ) -> EvidenceDependencyReceipt:
        registration = self.get_evidence_set_registration(
            auth, conversation_id, snapshot_id
        )
        if status not in {"RESOLVED", "PARTIAL", "UNKNOWN", "CONFLICTING"}:
            raise ValueError("EVIDENCE_DEPENDENCY_STATUS_INVALID")

        candidate = {
            "receipt_id": "candidate",
            "state_id": registration.state_id,
            "evidence_ids": list(evidence_ids),
            "failure_domains": copy.deepcopy(failure_domains),
            "status": status,
        }
        provenance = [
            {
                "receipt_id": receipt.receipt_id,
                "state_id": receipt.state_id,
                "evidence_id": receipt.evidence_id,
                "source_id": receipt.source_id,
                "status": receipt.status,
            }
            for receipt in self.list_evidence_provenance_receipts(
                auth, conversation_id, snapshot_id
            )
        ]

        from control_stack.evidence_provenance import (
            EVIDENCE_INVALID,
            assess_evidence_provenance,
        )

        probe = assess_evidence_provenance(
            state_id=registration.state_id,
            evidence_set=registration.evidence_set,
            provenance_receipts=provenance,
            dependency_receipt=candidate,
            missing_evidence=registration.missing_evidence,
            drift_state="NOT_ASSESSED",
        )
        if probe["status"] == EVIDENCE_INVALID:
            raise ValueError(probe["reason"])

        receipt = EvidenceDependencyReceipt(
            receipt_id=new_id("evidence_dep"),
            snapshot_id=registration.snapshot_id,
            conversation_id=registration.conversation_id,
            state_id=registration.state_id,
            evidence_ids=list(evidence_ids),
            failure_domains=copy.deepcopy(failure_domains),
            status=status,
            adapter_version=EVIDENCE_PROVENANCE_REGISTRY_ADAPTER_VERSION,
        )
        return self.persistence.add_evidence_dependency_receipt(
            auth.user_id, receipt
        )

    def get_evidence_dependency_receipt(
        self,
        auth: AuthContext,
        conversation_id: str,
        snapshot_id: str,
    ) -> EvidenceDependencyReceipt:
        return self.persistence.get_evidence_dependency_receipt(
            auth.user_id, conversation_id, snapshot_id
        )

    def save_execution_gate_receipt(
        self,
        auth: AuthContext,
        conversation_id: str,
        gate_result: dict,
    ) -> ExecutionReceiptRecord:
        self.get_conversation(auth, conversation_id)

        if not isinstance(gate_result, dict):
            raise ValueError("EXECUTION_GATE_RESULT_REQUIRED")
        if gate_result.get("version") != "EXECUTION_GATE_V0_1":
            raise ValueError("EXECUTION_GATE_VERSION_UNSUPPORTED")
        if gate_result.get("authority_effect") != "DOES_NOT_CREATE_AUTHORITY":
            raise ValueError("EXECUTION_GATE_AUTHORITY_BOUNDARY_MISMATCH")

        execution = gate_result.get("execution")
        if not isinstance(execution, dict):
            raise ValueError("EXECUTION_GATE_EXECUTION_RECEIPT_REQUIRED")

        required_outer = (
            "action_id",
            "controller_run_id",
            "controller_decision",
            "controller_state_id",
            "current_state_id",
            "controller_state_version",
            "current_state_version",
            "cfc_authority_state",
            "current_authority_state",
            "human_review_required",
            "human_review_approved",
            "transaction_required",
            "transaction_supported",
            "blockers",
            "reason",
        )
        if any(key not in gate_result for key in required_outer):
            raise ValueError("EXECUTION_GATE_RESULT_INCOMPLETE")

        required_execution = (
            "receipt_id",
            "idempotency_key",
            "attempted",
            "executed",
            "execution_status",
            "effect_handle",
            "pre_execution_state_id",
        )
        if any(key not in execution for key in required_execution):
            raise ValueError("EXECUTION_GATE_RECEIPT_INCOMPLETE")

        if execution["pre_execution_state_id"] != gate_result["current_state_id"]:
            raise ValueError("EXECUTION_GATE_PRE_STATE_BINDING_MISMATCH")

        receipt = ExecutionReceiptRecord(
            receipt_id=execution["receipt_id"],
            conversation_id=conversation_id,
            action_id=gate_result["action_id"],
            controller_run_id=gate_result["controller_run_id"],
            controller_decision=gate_result["controller_decision"],
            controller_state_id=gate_result["controller_state_id"],
            controller_state_version=gate_result["controller_state_version"],
            pre_execution_state_id=execution["pre_execution_state_id"],
            pre_execution_state_version=gate_result["current_state_version"],
            idempotency_key=execution["idempotency_key"],
            cfc_authority_state=gate_result["cfc_authority_state"],
            current_authority_state=gate_result["current_authority_state"],
            human_review_required=gate_result["human_review_required"],
            human_review_approved=gate_result["human_review_approved"],
            transaction_required=gate_result["transaction_required"],
            transaction_supported=gate_result["transaction_supported"],
            attempted=execution["attempted"],
            executed=execution["executed"],
            execution_status=execution["execution_status"],
            effect_handle=execution["effect_handle"],
            blockers=list(gate_result["blockers"]),
            reason=gate_result["reason"],
            adapter_version=EXECUTION_GATE_RECEIPT_ADAPTER_VERSION,
        )
        return self.persistence.add_execution_receipt(
            auth.user_id, receipt
        )

    def list_execution_receipts(
        self,
        auth: AuthContext,
        conversation_id: str,
    ) -> list[ExecutionReceiptRecord]:
        return self.persistence.list_execution_receipts(
            auth.user_id, conversation_id
        )

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
        hawm_snapshot_id: str | None = None,
    ) -> CFCRun:
        run = CFCRun(
            run_id=new_id("cfc"),
            conversation_id=conversation_id,
            case_id=case_id,
            controller_anchor=controller_anchor,
            controller_result=controller_result,
            presentation=presentation,
            replay_matches_reference=replay_matches_reference,
            hawm_snapshot_id=hawm_snapshot_id,
        )
        return self.persistence.add_cfc_run(auth.user_id, run)

    def latest_cfc_run(
        self, auth: AuthContext, conversation_id: str
    ) -> CFCRun | None:
        runs = self.persistence.list_cfc_runs(
            auth.user_id, conversation_id
        )
        return runs[-1] if runs else None

    def list_cfc_runs(
        self, auth: AuthContext, conversation_id: str
    ) -> list[CFCRun]:
        return self.persistence.list_cfc_runs(
            auth.user_id, conversation_id
        )


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


    def save_benchmark_run(
        self,
        auth: AuthContext,
        conversation_id: str,
        *,
        benchmark_version: str,
        case_id: str,
        benchmark_type: str,
        context_boundary: str,
        expected_control_state: str,
        invariant: str,
        mode: str,
        status: str,
        results: list[dict],
        failed_providers: list[dict],
    ) -> BenchmarkRun:
        run = BenchmarkRun(
            benchmark_run_id=new_id("bench"),
            conversation_id=conversation_id,
            benchmark_version=benchmark_version,
            case_id=case_id,
            benchmark_type=benchmark_type,
            context_boundary=context_boundary,
            expected_control_state=expected_control_state,
            invariant=invariant,
            mode=mode,
            status=status,
            results=results,
            failed_providers=failed_providers,
        )
        return self.persistence.add_benchmark_run(auth.user_id, run)

    def list_benchmark_runs(
        self, auth: AuthContext, conversation_id: str
    ) -> list[BenchmarkRun]:
        return self.persistence.list_benchmark_runs(
            auth.user_id, conversation_id
        )


    def save_benchmark_manual_label(
        self,
        auth: AuthContext,
        benchmark_run_id: str,
        *,
        provider: str,
        model: str,
        label: str,
        note: str | None = None,
    ) -> BenchmarkManualLabel:
        item = BenchmarkManualLabel(
            label_id=new_id("benchlabel"),
            benchmark_run_id=benchmark_run_id,
            provider=provider,
            model=model,
            label=label,
            note=note,
        )
        return self.persistence.upsert_benchmark_manual_label(
            auth.user_id, item
        )

    def list_benchmark_manual_labels(
        self, auth: AuthContext, benchmark_run_id: str
    ) -> list[BenchmarkManualLabel]:
        return self.persistence.list_benchmark_manual_labels(
            auth.user_id, benchmark_run_id
        )


    def get_benchmark_run(
        self, auth: AuthContext, benchmark_run_id: str
    ) -> BenchmarkRun:
        return self.persistence.get_benchmark_run(
            auth.user_id, benchmark_run_id
        )
