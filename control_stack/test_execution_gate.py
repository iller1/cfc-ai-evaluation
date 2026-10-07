import copy
import unittest

from control_stack.execution_gate import (
    EXECUTION_ALLOWED,
    EXECUTION_BLOCKED,
    EXECUTION_INVALID,
    assess_execution_gate,
    execute_with_gate,
)
from control_stack.schema_contract import validate_envelope
from control_stack.test_control_stack_schema import valid_envelope


def gate_inputs(**overrides):
    value = {
        "action_id": "action-1",
        "controller_run_id": "cfc-run-1",
        "controller_decision": "CONTINUE",
        "controller_blockers": [],
        "controller_state_id": "state-002",
        "current_state_id": "state-002",
        "controller_state_version": "version-2",
        "current_state_version": "version-2",
        "cfc_authority_state": "ESTABLISHED",
        "current_authority_state": "ESTABLISHED",
        "idempotency_key": "idem-1",
        "receipt_id": "exec-receipt-1",
        "prior_execution_receipts": [],
        "human_review_required": False,
        "human_review_approved": False,
        "transaction_required": False,
        "transaction_supported": False,
    }
    value.update(overrides)
    return value


class ExecutionGateTests(unittest.TestCase):
    def test_exact_pre_execution_state_is_allowed_but_not_yet_attempted(self):
        result = assess_execution_gate(**gate_inputs())

        self.assertEqual(result["gate_status"], EXECUTION_ALLOWED)
        self.assertEqual(
            result["reason"],
            "EXACT_PRE_EXECUTION_GATES_ESTABLISHED",
        )
        self.assertEqual(result["blockers"], [])
        self.assertFalse(result["execution"]["attempted"])
        self.assertFalse(result["execution"]["executed"])
        self.assertEqual(
            result["execution"]["execution_status"],
            "NOT_ATTEMPTED",
        )
        self.assertEqual(
            result["authority_effect"],
            "DOES_NOT_CREATE_AUTHORITY",
        )

    def test_hold_never_calls_executor(self):
        calls = []

        def executor(payload):
            calls.append(payload)
            return {"outcome": "EXECUTED", "effect_handle": "effect-1"}

        result = execute_with_gate(
            executor=executor,
            **gate_inputs(controller_decision="HOLD"),
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertEqual(result["reason"], "CONTROLLER_DECISION_NOT_CONTINUE")
        self.assertEqual(calls, [])
        self.assertFalse(result["execution"]["attempted"])
        self.assertFalse(result["execution"]["executed"])
        self.assertEqual(result["execution"]["execution_status"], "BLOCKED")

    def test_stop_never_calls_executor(self):
        calls = []

        result = execute_with_gate(
            executor=lambda payload: calls.append(payload),
            **gate_inputs(controller_decision="STOP"),
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertEqual(calls, [])

    def test_controller_blockers_cannot_be_laundered_by_continue_label(self):
        result = assess_execution_gate(
            **gate_inputs(controller_blockers=["UPSTREAM_UNRESOLVED"])
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertIn("CONTROLLER_BLOCKERS_PRESENT", result["blockers"])

    def test_cfc_authority_must_be_established(self):
        result = assess_execution_gate(
            **gate_inputs(cfc_authority_state="UNKNOWN")
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertIn("CFC_AUTHORITY_NOT_ESTABLISHED", result["blockers"])

    def test_current_authority_must_still_be_established(self):
        result = assess_execution_gate(
            **gate_inputs(current_authority_state="REVOKED")
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertIn("CURRENT_AUTHORITY_NOT_ESTABLISHED", result["blockers"])

    def test_state_id_change_blocks_before_attempt(self):
        result = assess_execution_gate(
            **gate_inputs(current_state_id="state-003")
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertIn("PRE_EXECUTION_STATE_ID_MISMATCH", result["blockers"])

    def test_state_version_change_blocks_before_attempt(self):
        result = assess_execution_gate(
            **gate_inputs(current_state_version="version-3")
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertIn(
            "PRE_EXECUTION_STATE_VERSION_MISMATCH",
            result["blockers"],
        )

    def test_human_review_required_without_approval_blocks(self):
        result = assess_execution_gate(
            **gate_inputs(human_review_required=True)
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertIn("HUMAN_REVIEW_REQUIRED", result["blockers"])

    def test_human_review_required_with_approval_can_continue(self):
        result = assess_execution_gate(
            **gate_inputs(
                human_review_required=True,
                human_review_approved=True,
            )
        )

        self.assertEqual(result["gate_status"], EXECUTION_ALLOWED)

    def test_transaction_required_without_supported_boundary_blocks(self):
        result = assess_execution_gate(
            **gate_inputs(transaction_required=True)
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertIn(
            "TRANSACTION_BOUNDARY_UNAVAILABLE",
            result["blockers"],
        )

    def test_transaction_required_with_supported_boundary_can_continue(self):
        result = assess_execution_gate(
            **gate_inputs(
                transaction_required=True,
                transaction_supported=True,
            )
        )

        self.assertEqual(result["gate_status"], EXECUTION_ALLOWED)

    def test_same_idempotency_key_same_action_blocks_replay(self):
        prior = [{
            "receipt_id": "old-receipt",
            "action_id": "action-1",
            "idempotency_key": "idem-1",
        }]

        result = assess_execution_gate(
            **gate_inputs(prior_execution_receipts=prior)
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertIn("IDEMPOTENCY_REPLAY_BLOCKED", result["blockers"])
        self.assertEqual(result["prior_receipt_id"], "old-receipt")

    def test_idempotency_key_reused_for_other_action_is_blocked(self):
        prior = [{
            "receipt_id": "old-receipt",
            "action_id": "other-action",
            "idempotency_key": "idem-1",
        }]

        result = assess_execution_gate(
            **gate_inputs(prior_execution_receipts=prior)
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertIn(
            "IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_ACTION",
            result["blockers"],
        )

    def test_invalid_prior_receipt_collection_fails_closed(self):
        result = assess_execution_gate(
            **gate_inputs(prior_execution_receipts={"not": "a-list"})
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertIn(
            "PRIOR_EXECUTION_RECEIPTS_NOT_ARRAY",
            result["blockers"],
        )

    def test_successful_executor_is_called_exactly_once(self):
        calls = []

        def executor(payload):
            calls.append(copy.deepcopy(payload))
            return {"outcome": "EXECUTED", "effect_handle": "effect-1"}

        result = execute_with_gate(
            executor=executor,
            action_payload={"operation": "demo"},
            **gate_inputs(),
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["state_id"], "state-002")
        self.assertEqual(calls[0]["state_version"], "version-2")
        self.assertEqual(calls[0]["idempotency_key"], "idem-1")
        self.assertEqual(
            calls[0]["action_payload"],
            {"operation": "demo"},
        )
        self.assertTrue(result["execution"]["attempted"])
        self.assertTrue(result["execution"]["executed"])
        self.assertEqual(result["execution"]["execution_status"], "EXECUTED")
        self.assertEqual(result["execution"]["effect_handle"], "effect-1")

    def test_executor_confirms_no_effect(self):
        result = execute_with_gate(
            executor=lambda payload: {
                "outcome": "NOT_EXECUTED",
                "effect_handle": None,
            },
            **gate_inputs(),
        )

        self.assertTrue(result["execution"]["attempted"])
        self.assertFalse(result["execution"]["executed"])
        self.assertEqual(
            result["execution"]["execution_status"],
            "ATTEMPTED_NOT_EXECUTED",
        )

    def test_executor_exception_is_outcome_unknown_not_false_no_effect(self):
        calls = []

        def executor(payload):
            calls.append(payload)
            raise RuntimeError("connection lost after submit")

        result = execute_with_gate(
            executor=executor,
            **gate_inputs(),
        )

        self.assertEqual(len(calls), 1)
        self.assertTrue(result["execution"]["attempted"])
        self.assertIsNone(result["execution"]["executed"])
        self.assertEqual(
            result["execution"]["execution_status"],
            "OUTCOME_UNKNOWN",
        )
        self.assertEqual(
            result["reason"],
            "EXECUTOR_EXCEPTION_OUTCOME_UNKNOWN",
        )

    def test_executor_explicit_unknown_is_preserved(self):
        result = execute_with_gate(
            executor=lambda payload: {
                "outcome": "UNKNOWN",
                "effect_handle": "provider-request-17",
            },
            **gate_inputs(),
        )

        self.assertTrue(result["execution"]["attempted"])
        self.assertIsNone(result["execution"]["executed"])
        self.assertEqual(
            result["execution"]["execution_status"],
            "OUTCOME_UNKNOWN",
        )
        self.assertEqual(
            result["execution"]["effect_handle"],
            "provider-request-17",
        )

    def test_malformed_executor_result_is_outcome_unknown(self):
        result = execute_with_gate(
            executor=lambda payload: "not-a-receipt",
            **gate_inputs(),
        )

        self.assertIsNone(result["execution"]["executed"])
        self.assertEqual(
            result["execution"]["execution_status"],
            "OUTCOME_UNKNOWN",
        )

    def test_executed_claim_requires_nonempty_effect_handle(self):
        result = execute_with_gate(
            executor=lambda payload: {
                "outcome": "EXECUTED",
                "effect_handle": None,
            },
            **gate_inputs(),
        )

        self.assertIsNone(result["execution"]["executed"])
        self.assertEqual(
            result["execution"]["execution_status"],
            "OUTCOME_UNKNOWN",
        )

    def test_missing_executor_blocks_without_attempt(self):
        result = execute_with_gate(
            executor=None,
            **gate_inputs(),
        )

        self.assertEqual(result["gate_status"], EXECUTION_BLOCKED)
        self.assertEqual(result["reason"], "EXECUTOR_UNAVAILABLE")
        self.assertFalse(result["execution"]["attempted"])
        self.assertFalse(result["execution"]["executed"])

    def test_required_identity_missing_is_invalid_and_not_attempted(self):
        result = assess_execution_gate(
            **gate_inputs(receipt_id="")
        )

        self.assertEqual(result["gate_status"], EXECUTION_INVALID)
        self.assertFalse(result["execution"]["attempted"])
        self.assertFalse(result["execution"]["executed"])

    def test_successful_gate_output_plugs_into_shared_envelope(self):
        result = execute_with_gate(
            executor=lambda payload: {
                "outcome": "EXECUTED",
                "effect_handle": "effect-1",
            },
            **gate_inputs(),
        )
        envelope = valid_envelope()
        envelope["execution"] = copy.deepcopy(result["execution"])

        validated = validate_envelope(envelope)

        self.assertTrue(validated["execution"]["executed"])
        self.assertEqual(
            validated["execution"]["execution_status"],
            "EXECUTED",
        )

    def test_unknown_outcome_plugs_into_shared_envelope_without_false_claim(self):
        result = execute_with_gate(
            executor=lambda payload: {
                "outcome": "UNKNOWN",
                "effect_handle": "provider-request-17",
            },
            **gate_inputs(),
        )
        envelope = valid_envelope()
        envelope["execution"] = copy.deepcopy(result["execution"])

        validated = validate_envelope(envelope)

        self.assertTrue(validated["execution"]["attempted"])
        self.assertIsNone(validated["execution"]["executed"])
        self.assertEqual(
            validated["execution"]["execution_status"],
            "OUTCOME_UNKNOWN",
        )

    def test_blocked_output_plugs_into_shared_envelope(self):
        result = execute_with_gate(
            executor=lambda payload: {
                "outcome": "EXECUTED",
                "effect_handle": "should-not-run",
            },
            **gate_inputs(controller_decision="HOLD"),
        )
        envelope = valid_envelope()
        envelope["cfc"]["decision"] = "HOLD"
        envelope["cfc"]["blockers"] = ["POLICY_HOLD"]
        envelope["execution"] = copy.deepcopy(result["execution"])

        validated = validate_envelope(envelope)

        self.assertFalse(validated["execution"]["attempted"])
        self.assertFalse(validated["execution"]["executed"])
        self.assertEqual(
            validated["execution"]["execution_status"],
            "BLOCKED",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
