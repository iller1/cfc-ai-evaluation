import unittest

from pro_beta.contracts import HAWMSnapshot
from pro_beta.state_monitor import (
    BLOCK_STATE_CARRY_FORWARD,
    NO_ADDITIONAL_BLOCK,
    NO_MONITOR_ALERT,
    STATE_TRANSITION_ALERT,
    UNRESOLVED,
    assess_state_transition,
)


def snapshot(
    snapshot_id: str,
    *,
    conversation_id: str = "conv-1",
    unresolved=None,
    structured=None,
    **extra,
):
    state = dict(extra)
    if unresolved is not None:
        state["unresolved"] = unresolved
    if structured is not None:
        state["cfc_structured"] = structured
    return HAWMSnapshot(
        snapshot_id=snapshot_id,
        conversation_id=conversation_id,
        state=state,
        last_verified_state="USER_WORKING_STATE",
    )


def structured(evidence=None):
    return {
        "conclusion": "POSITIVE",
        "required_independent_supports": 1,
        "provenance_shape": "DISTINCT",
        "independence_authority": "NONE",
        "scope": "EXPECTED",
        "evidence": evidence
        if evidence is not None
        else [{"polarity": "POSITIVE", "validity": "CURRENT"}],
    }


class StateMonitorTests(unittest.TestCase):
    def test_unresolved_persists_without_alert(self):
        result = assess_state_transition(
            snapshot("a", unresolved="Need source", structured=structured()),
            snapshot("b", unresolved="Need source", structured=structured()),
            current_snapshot_evaluated=False,
        )

        self.assertEqual(result["status"], NO_MONITOR_ALERT)
        self.assertEqual(result["reason"], "UNRESOLVED_STILL_PRESENT")
        self.assertFalse(result["requires_review"])
        self.assertEqual(result["propagation_effect"], NO_ADDITIONAL_BLOCK)

    def test_unresolved_added_without_alert(self):
        result = assess_state_transition(
            snapshot("a", unresolved="", structured=structured()),
            snapshot("b", unresolved="Need source", structured=structured()),
            current_snapshot_evaluated=False,
        )

        self.assertEqual(result["status"], NO_MONITOR_ALERT)
        self.assertEqual(result["reason"], "UNRESOLVED_ADDED")

    def test_unresolved_clear_without_current_evaluation_alerts(self):
        result = assess_state_transition(
            snapshot("a", unresolved="Need source", structured=structured()),
            snapshot("b", unresolved="", structured=structured()),
            current_snapshot_evaluated=False,
        )

        self.assertEqual(result["status"], STATE_TRANSITION_ALERT)
        self.assertEqual(
            result["reason"],
            "UNRESOLVED_CLEARED_WITHOUT_CURRENT_SNAPSHOT_EVALUATION",
        )
        self.assertTrue(result["requires_review"])
        self.assertEqual(
            result["propagation_effect"],
            BLOCK_STATE_CARRY_FORWARD,
        )

    def test_unresolved_clear_after_current_evaluation_has_no_monitor_alert(self):
        result = assess_state_transition(
            snapshot("a", unresolved="Need source", structured=structured()),
            snapshot("b", unresolved="", structured=structured()),
            current_snapshot_evaluated=True,
        )

        self.assertEqual(result["status"], NO_MONITOR_ALERT)
        self.assertEqual(
            result["reason"],
            "UNRESOLVED_CLEARED_AFTER_CURRENT_SNAPSHOT_EVALUATION",
        )
        self.assertFalse(result["requires_review"])
        self.assertEqual(
            result["authorization_effect"],
            "DOES_NOT_AUTHORIZE_CLOSURE",
        )

    def test_same_snapshot_id_with_changed_state_is_unresolved(self):
        result = assess_state_transition(
            snapshot("same", unresolved="Need source", structured=structured()),
            snapshot("same", unresolved="", structured=structured()),
            current_snapshot_evaluated=True,
        )

        self.assertEqual(result["status"], UNRESOLVED)
        self.assertEqual(result["reason"], "SNAPSHOT_ID_CONTENT_MISMATCH")
        self.assertTrue(result["requires_review"])

    def test_same_snapshot_evidence_reorder_is_not_identity_mismatch(self):
        evidence = [
            {"id": "E1", "polarity": "POSITIVE", "validity": "CURRENT"},
            {"id": "E2", "polarity": "NEGATIVE", "validity": "STALE"},
        ]
        result = assess_state_transition(
            snapshot(
                "same",
                unresolved="Need source",
                structured=structured(evidence),
            ),
            snapshot(
                "same",
                unresolved="Need source",
                structured=structured(list(reversed(evidence))),
            ),
            current_snapshot_evaluated=False,
        )

        self.assertEqual(result["status"], NO_MONITOR_ALERT)
        self.assertEqual(result["reason"], "UNRESOLVED_STILL_PRESENT")

    def test_cross_conversation_transition_is_unresolved(self):
        result = assess_state_transition(
            snapshot(
                "a",
                conversation_id="conv-a",
                unresolved="Need source",
                structured=structured(),
            ),
            snapshot(
                "b",
                conversation_id="conv-b",
                unresolved="",
                structured=structured(),
            ),
            current_snapshot_evaluated=True,
        )

        self.assertEqual(result["status"], UNRESOLVED)
        self.assertEqual(result["reason"], "CROSS_CONVERSATION_TRANSITION")
        self.assertEqual(
            result["propagation_effect"],
            BLOCK_STATE_CARRY_FORWARD,
        )

    def test_non_string_unresolved_field_is_unresolved(self):
        previous = HAWMSnapshot(
            snapshot_id="a",
            conversation_id="conv-1",
            state={"unresolved": ["not", "a", "string"]},
            last_verified_state="USER_WORKING_STATE",
        )
        current = snapshot("b", unresolved="", structured=structured())

        result = assess_state_transition(
            previous,
            current,
            current_snapshot_evaluated=False,
        )

        self.assertEqual(result["status"], UNRESOLVED)
        self.assertIn("PREVIOUS_UNRESOLVED_FIELD_NOT_STRING", result["reason"])

    def test_invalid_evaluation_flag_is_unresolved(self):
        result = assess_state_transition(
            snapshot("a", unresolved="Need source", structured=structured()),
            snapshot("b", unresolved="", structured=structured()),
            current_snapshot_evaluated="yes",
        )

        self.assertEqual(result["status"], UNRESOLVED)
        self.assertEqual(
            result["reason"],
            "CURRENT_SNAPSHOT_EVALUATION_FLAG_INVALID",
        )
        self.assertIsNone(result["current_snapshot_evaluated"])

    def test_no_unresolved_clearance_is_not_authorization(self):
        result = assess_state_transition(
            snapshot("a", unresolved="", structured=structured()),
            snapshot("b", unresolved="", structured=structured()),
            current_snapshot_evaluated=False,
        )

        self.assertEqual(result["status"], NO_MONITOR_ALERT)
        self.assertEqual(result["reason"], "NO_UNRESOLVED_CLEARANCE")
        self.assertEqual(
            result["authorization_effect"],
            "DOES_NOT_AUTHORIZE_CLOSURE",
        )


if __name__ == "__main__":
    unittest.main()
