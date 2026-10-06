import copy
import unittest

from control_stack.state_integrity import (
    BLOCK_STATE,
    NO_ADDITIONAL_BLOCK,
    STATE_INVALID,
    STATE_UNRESOLVED,
    STATE_VALID,
    assess_state_integrity,
    state_fingerprint,
)


def base_record():
    payload = {
        "goal": "test",
        "cfc_structured": {
            "conclusion": "POSITIVE",
            "scope": "EXPECTED",
        },
    }
    return {
        "case_id": "case-A",
        "arm_id": "arm-1",
        "state_id": "state-2",
        "snapshot_id": "snap-2",
        "lineage_id": "lineage-1",
        "previous_state_id": "state-1",
        "state_payload": payload,
    }


def expectation_for(record):
    return {
        "case_id": record["case_id"],
        "arm_id": record["arm_id"],
        "current_snapshot_id": record["snapshot_id"],
        "lineage_id": record["lineage_id"],
        "expected_previous_state_id": record["previous_state_id"],
        "registered_snapshot_fingerprint": state_fingerprint(
            record["state_payload"]
        ),
    }


class StateIntegrityTests(unittest.TestCase):
    def test_exact_state_binding_is_valid(self):
        record = base_record()
        result = assess_state_integrity(
            record,
            expectation_for(record),
        )

        self.assertEqual(result["status"], STATE_VALID)
        self.assertEqual(
            result["reason"],
            "EXACT_STATE_BINDING_ESTABLISHED",
        )
        self.assertEqual(result["binding_status"], "BOUND")
        self.assertEqual(result["lineage_status"], "ESTABLISHED")
        self.assertFalse(result["requires_review"])
        self.assertEqual(
            result["propagation_effect"],
            NO_ADDITIONAL_BLOCK,
        )
        self.assertEqual(
            result["authorization_effect"],
            "DOES_NOT_AUTHORIZE_CLOSURE",
        )

    def test_cross_case_substitution_is_invalid(self):
        record = base_record()
        expected = expectation_for(record)
        record["case_id"] = "case-B"

        result = assess_state_integrity(record, expected)

        self.assertEqual(result["status"], STATE_INVALID)
        self.assertEqual(result["reason"], "CASE_ID_MISMATCH")
        self.assertIn("CASE_ID_MISMATCH", result["violations"])
        self.assertTrue(result["requires_review"])
        self.assertEqual(result["propagation_effect"], BLOCK_STATE)

    def test_cross_arm_substitution_is_invalid(self):
        record = base_record()
        expected = expectation_for(record)
        record["arm_id"] = "arm-2"

        result = assess_state_integrity(record, expected)

        self.assertEqual(result["status"], STATE_INVALID)
        self.assertEqual(result["reason"], "ARM_ID_MISMATCH")

    def test_lineage_id_substitution_is_invalid(self):
        record = base_record()
        expected = expectation_for(record)
        record["lineage_id"] = "lineage-other"

        result = assess_state_integrity(record, expected)

        self.assertEqual(result["status"], STATE_INVALID)
        self.assertEqual(result["reason"], "LINEAGE_ID_MISMATCH")
        self.assertEqual(result["lineage_status"], "INVALID")

    def test_stale_snapshot_is_unresolved_not_valid(self):
        record = base_record()
        expected = expectation_for(record)
        expected["current_snapshot_id"] = "snap-3"

        result = assess_state_integrity(record, expected)

        self.assertEqual(result["status"], STATE_UNRESOLVED)
        self.assertEqual(result["reason"], "CURRENT_SNAPSHOT_MISMATCH")
        self.assertEqual(result["binding_status"], "MISMATCH")
        self.assertTrue(result["requires_review"])

    def test_same_snapshot_id_with_changed_payload_is_invalid(self):
        record = base_record()
        expected = expectation_for(record)
        record["state_payload"]["goal"] = "mutated-after-registration"

        result = assess_state_integrity(record, expected)

        self.assertEqual(result["status"], STATE_INVALID)
        self.assertEqual(
            result["reason"],
            "SNAPSHOT_FINGERPRINT_MISMATCH",
        )

    def test_predecessor_mismatch_is_unresolved(self):
        record = base_record()
        expected = expectation_for(record)
        record["previous_state_id"] = "state-X"

        result = assess_state_integrity(record, expected)

        self.assertEqual(result["status"], STATE_UNRESOLVED)
        self.assertEqual(result["reason"], "PREDECESSOR_MISMATCH")
        self.assertEqual(result["lineage_status"], "DEGRADED")

    def test_missing_registered_fingerprint_is_unresolved(self):
        record = base_record()
        expected = expectation_for(record)
        expected["registered_snapshot_fingerprint"] = None

        result = assess_state_integrity(record, expected)

        self.assertEqual(result["status"], STATE_UNRESOLVED)
        self.assertEqual(
            result["reason"],
            "SNAPSHOT_FINGERPRINT_NOT_REGISTERED",
        )
        self.assertEqual(result["binding_status"], "UNKNOWN")

    def test_payload_key_order_does_not_change_fingerprint(self):
        first = {
            "alpha": 1,
            "nested": {"x": 1, "y": 2},
        }
        second = {
            "nested": {"y": 2, "x": 1},
            "alpha": 1,
        }

        self.assertEqual(
            state_fingerprint(first),
            state_fingerprint(second),
        )

    def test_multiple_violations_preserve_all_detected_problems(self):
        record = base_record()
        expected = expectation_for(record)
        record["case_id"] = "case-B"
        record["arm_id"] = "arm-2"
        expected["current_snapshot_id"] = "snap-3"

        result = assess_state_integrity(record, expected)

        self.assertEqual(result["status"], STATE_INVALID)
        self.assertEqual(
            result["violations"],
            [
                "CASE_ID_MISMATCH",
                "ARM_ID_MISMATCH",
                "CURRENT_SNAPSHOT_MISMATCH",
            ],
        )

    def test_missing_required_expectation_is_unresolved(self):
        record = base_record()
        expected = expectation_for(record)
        del expected["current_snapshot_id"]

        result = assess_state_integrity(record, expected)

        self.assertEqual(result["status"], STATE_UNRESOLVED)
        self.assertEqual(
            result["reason"],
            "STATE_INTEGRITY_INPUT_UNRESOLVED",
        )
        self.assertIn(
            "EXPECTATION_MISSING_CURRENT_SNAPSHOT_ID",
            result["violations"],
        )

    def test_non_object_payload_is_unresolved(self):
        record = base_record()
        expected = expectation_for(record)
        record["state_payload"] = ["not", "an", "object"]

        result = assess_state_integrity(record, expected)

        self.assertEqual(result["status"], STATE_UNRESOLVED)
        self.assertIn(
            "RECORD_STATE_PAYLOAD_NOT_OBJECT",
            result["violations"],
        )

    def test_validity_does_not_authorize_closure(self):
        record = base_record()
        result = assess_state_integrity(
            record,
            expectation_for(record),
        )

        self.assertEqual(result["status"], STATE_VALID)
        self.assertEqual(
            result["authorization_effect"],
            "DOES_NOT_AUTHORIZE_CLOSURE",
        )


if __name__ == "__main__":
    unittest.main()
