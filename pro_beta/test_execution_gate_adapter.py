from __future__ import annotations

from dataclasses import replace
import unittest

from pro_beta.contracts import (
    CFCRun,
    ExecutionReceiptRecord,
    HAWMSnapshot,
    HAWMSnapshotIdentity,
)
from pro_beta.execution_gate_adapter import (
    PREFLIGHT_ACTION_ID,
    PRO_BETA_EXECUTION_GATE_ADAPTER_VERSION,
    assess_persisted_execution_preflight,
)
from pro_beta.service import HAWM_STATE_IDENTITY_ADAPTER_VERSION


def snapshot(snapshot_id="hawm-current"):
    return HAWMSnapshot(
        snapshot_id=snapshot_id,
        conversation_id="conv-1",
        state={"goal": "execution preflight"},
        last_verified_state="USER_WORKING_STATE",
    )


def identity(snapshot_id="hawm-current", fingerprint="a" * 64):
    return HAWMSnapshotIdentity(
        snapshot_id=snapshot_id,
        conversation_id="conv-1",
        case_id="HAWM_PRO_BETA_STATE",
        arm_id="HAWM_WORKING_STATE",
        state_id=snapshot_id,
        lineage_id="conv-1",
        previous_state_id=None,
        registered_snapshot_fingerprint=fingerprint,
        adapter_version=HAWM_STATE_IDENTITY_ADAPTER_VERSION,
    )


def state_integrity(
    status="STATE_VALID",
    snapshot_id="hawm-current",
    authorization_effect="DOES_NOT_AUTHORIZE_CLOSURE",
):
    return {
        "status": status,
        "snapshot_id": snapshot_id,
        "state_id": snapshot_id,
        "authorization_effect": authorization_effect,
    }


def cfc_run(
    *,
    snapshot_id="hawm-current",
    closure=False,
    decision=None,
    case_id="HAWM_STRUCTURED_CUSTOM",
    anchor="0.2.90rc1",
):
    if decision is None:
        decision = "ALLOW" if closure else "STOP"
    return CFCRun(
        run_id="cfc-1",
        conversation_id="conv-1",
        case_id=case_id,
        controller_anchor=anchor,
        controller_result={"control_closure": closure},
        presentation={"decision": decision},
        hawm_snapshot_id=snapshot_id,
    )


class ExecutionGateAdapterTests(unittest.TestCase):
    def assess(
        self,
        *,
        current=None,
        current_identity=None,
        si=None,
        run=None,
        controller_identity=None,
        prior=None,
    ):
        current = current or snapshot()
        current_identity = current_identity or identity()
        si = si or state_integrity()
        if run is None:
            run = cfc_run()
        if controller_identity is None and run.hawm_snapshot_id is not None:
            controller_identity = identity(run.hawm_snapshot_id)
        return assess_persisted_execution_preflight(
            current=current,
            current_identity=current_identity,
            state_integrity_result=si,
            cfc_run=run,
            controller_identity=controller_identity,
            prior_execution_receipts=prior or [],
        )

    def test_synthetic_stop_is_blocked_and_never_attempted(self):
        result = self.assess(run=cfc_run(closure=False))

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertEqual(result["controller_decision"], "STOP")
        self.assertIn(
            "FROZEN_CFC_CONTROL_CLOSURE_FALSE",
            result["blockers"],
        )
        self.assertIn(
            "REAL_ACTION_AUTHORITY_NOT_ESTABLISHED",
            result["blockers"],
        )
        self.assertFalse(result["execution"]["attempted"])
        self.assertFalse(result["execution"]["executed"])
        self.assertEqual(
            result["execution"]["execution_status"],
            "BLOCKED",
        )
        self.assertTrue(result["read_only"])
        self.assertFalse(result["executor_called"])
        self.assertEqual(result["persistence_actions"], [])

    def test_synthetic_allow_is_hold_not_continue(self):
        result = self.assess(run=cfc_run(closure=True))

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertEqual(result["controller_decision"], "HOLD")
        self.assertNotEqual(result["controller_decision"], "CONTINUE")
        self.assertIn(
            "SYNTHETIC_CFC_CLOSURE_NOT_REAL_ACTION_AUTHORITY",
            result["blockers"],
        )
        self.assertEqual(result["synthetic_cfc_result"], "SYNTHETIC_CLOSURE_ONLY")
        self.assertTrue(result["raw_control_closure"])
        self.assertEqual(result["presentation_decision"], "ALLOW")
        self.assertEqual(
            result["cfc_authority_state"],
            "NOT_ESTABLISHED",
        )
        self.assertEqual(
            result["current_authority_state"],
            "NOT_ESTABLISHED",
        )

    def test_state_integrity_invalid_blocks_before_cfc_interpretation(self):
        result = self.assess(
            si=state_integrity(status="STATE_INVALID"),
            run=cfc_run(closure=True),
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertEqual(result["reason"], "STATE_INTEGRITY_NOT_VALID")
        self.assertEqual(result["state_integrity_status"], "STATE_INVALID")
        self.assertFalse(result["executor_called"])

    def test_state_integrity_cannot_upgrade_authorization_boundary(self):
        result = self.assess(
            si=state_integrity(
                authorization_effect="AUTHORIZES_CLOSURE"
            )
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertEqual(
            result["reason"],
            "STATE_INTEGRITY_AUTHORIZATION_BOUNDARY_MISMATCH",
        )

    def test_state_integrity_result_must_bind_current_snapshot(self):
        result = self.assess(
            si=state_integrity(snapshot_id="hawm-other")
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertEqual(
            result["reason"],
            "STATE_INTEGRITY_RESULT_BINDING_MISMATCH",
        )

    def test_prepared_fixture_case_is_not_supported_for_preflight(self):
        result = self.assess(
            run=cfc_run(
                case_id="CASE_07_VALID_POSITIVE_CLOSURE",
                closure=True,
            )
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertEqual(
            result["reason"],
            "CFC_RUN_CASE_NOT_SUPPORTED_FOR_EXECUTION_PREFLIGHT",
        )

    def test_unbound_cfc_run_is_blocked(self):
        run = cfc_run()
        run = replace(run, hawm_snapshot_id=None)

        result = assess_persisted_execution_preflight(
            current=snapshot(),
            current_identity=identity(),
            state_integrity_result=state_integrity(),
            cfc_run=run,
            controller_identity=None,
            prior_execution_receipts=[],
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertEqual(result["reason"], "CFC_RUN_NOT_STATE_BOUND")

    def test_missing_cfc_run_is_blocked(self):
        result = assess_persisted_execution_preflight(
            current=snapshot(),
            current_identity=identity(),
            state_integrity_result=state_integrity(),
            cfc_run=None,
            controller_identity=None,
            prior_execution_receipts=[],
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertEqual(result["reason"], "BOUND_CFC_RUN_NOT_FOUND")

    def test_stale_controller_state_is_explicitly_blocked(self):
        current = snapshot("hawm-current")
        current_identity = identity("hawm-current", "b" * 64)
        run = cfc_run(snapshot_id="hawm-old", closure=False)
        old_identity = identity("hawm-old", "a" * 64)

        result = self.assess(
            current=current,
            current_identity=current_identity,
            si=state_integrity(snapshot_id="hawm-current"),
            run=run,
            controller_identity=old_identity,
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertIn(
            "PRE_EXECUTION_STATE_ID_MISMATCH",
            result["blockers"],
        )
        self.assertIn(
            "PRE_EXECUTION_STATE_VERSION_MISMATCH",
            result["blockers"],
        )
        self.assertEqual(result["controller_state_id"], "hawm-old")
        self.assertEqual(result["current_state_id"], "hawm-current")

    def test_raw_and_presentation_mismatch_fails_closed(self):
        result = self.assess(
            run=cfc_run(closure=True, decision="STOP")
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertIn(
            "CFC_RUN_REPRESENTATION_MISMATCH",
            result["blockers"],
        )

    def test_frozen_anchor_mismatch_fails_closed(self):
        result = self.assess(
            run=cfc_run(anchor="0.2.91")
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertIn("FROZEN_CFC_ANCHOR_MISMATCH", result["blockers"])

    def test_prior_receipt_replay_is_seen_by_gate(self):
        first = self.assess(run=cfc_run(closure=False))
        prior = ExecutionReceiptRecord(
            receipt_id="persisted-receipt",
            conversation_id="conv-1",
            action_id=PREFLIGHT_ACTION_ID,
            controller_run_id="cfc-1",
            controller_decision="STOP",
            controller_state_id="hawm-current",
            controller_state_version="a" * 64,
            pre_execution_state_id="hawm-current",
            pre_execution_state_version="a" * 64,
            idempotency_key=first["execution"]["idempotency_key"],
            cfc_authority_state="NOT_ESTABLISHED",
            current_authority_state="NOT_ESTABLISHED",
            human_review_required=False,
            human_review_approved=False,
            transaction_required=False,
            transaction_supported=False,
            attempted=False,
            executed=False,
            execution_status="BLOCKED",
            effect_handle=None,
            blockers=["FROZEN_CFC_CONTROL_CLOSURE_FALSE"],
            reason="FROZEN_CFC_CONTROL_CLOSURE_FALSE",
            adapter_version="EXECUTION_GATE_RECEIPT_ADAPTER_V0_1",
        )

        result = self.assess(
            run=cfc_run(closure=False),
            prior=[prior],
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertIn("IDEMPOTENCY_REPLAY_BLOCKED", result["blockers"])
        self.assertEqual(result["prior_receipt_id"], "persisted-receipt")

    def test_adapter_identity_and_claim_ceiling_are_explicit(self):
        result = self.assess(run=cfc_run(closure=True))

        self.assertEqual(
            result["adapter_version"],
            PRO_BETA_EXECUTION_GATE_ADAPTER_VERSION,
        )
        self.assertIn(
            "NO_REAL_ACTION_EXECUTION",
            result["adapter_boundary"],
        )
        self.assertTrue(result["synthetic_cfc_only"])
        self.assertEqual(
            result["authority_effect"],
            "DOES_NOT_CREATE_AUTHORITY",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
