import unittest

from pro_beta.contracts import HAWMSnapshot
from pro_beta.evidence_drift import (
    BLOCK_CARRY_FORWARD,
    MATERIAL_DRIFT,
    NO_ADDITIONAL_BLOCK,
    NO_DRIFT,
    UNRESOLVED,
    assess_evidence_drift,
)


def snapshot(
    snapshot_id: str,
    *,
    conversation_id: str = "conv-1",
    structured=None,
    **free_text,
):
    state = dict(free_text)
    if structured is not None:
        state["cfc_structured"] = structured
    return HAWMSnapshot(
        snapshot_id=snapshot_id,
        conversation_id=conversation_id,
        state=state,
        last_verified_state="USER_WORKING_STATE",
    )


def base_structured():
    return {
        "conclusion": "POSITIVE",
        "required_independent_supports": 1,
        "provenance_shape": "DISTINCT",
        "independence_authority": "NONE",
        "scope": "EXPECTED",
        "evidence": [
            {"polarity": "POSITIVE", "validity": "CURRENT"},
        ],
    }


class EvidenceDriftTests(unittest.TestCase):
    def test_identical_structured_state_across_new_snapshot_is_no_drift(self):
        baseline = snapshot("hawm-a", structured=base_structured(), goal="A")
        current = snapshot("hawm-b", structured=base_structured(), goal="B")

        result = assess_evidence_drift(baseline, current)

        self.assertEqual(result["status"], NO_DRIFT)
        self.assertEqual(result["changed_paths"], [])
        self.assertFalse(result["requires_re_evaluation"])
        self.assertEqual(result["propagation_effect"], NO_ADDITIONAL_BLOCK)
        self.assertEqual(
            result["authorization_effect"],
            "DOES_NOT_AUTHORIZE_CLOSURE",
        )

    def test_free_text_change_is_outside_v0_1_drift_boundary(self):
        baseline = snapshot(
            "hawm-a",
            structured=base_structured(),
            evidence="free text evidence A",
            claims="claim A",
        )
        current = snapshot(
            "hawm-b",
            structured=base_structured(),
            evidence="completely different free text",
            claims="claim B",
        )

        result = assess_evidence_drift(baseline, current)

        self.assertEqual(result["status"], NO_DRIFT)
        self.assertIn("NO_FREE_TEXT_EVIDENCE_INFERENCE", result["boundary"])

    def test_current_to_stale_is_material_drift(self):
        baseline_state = base_structured()
        current_state = base_structured()
        current_state["evidence"][0]["validity"] = "STALE"

        result = assess_evidence_drift(
            snapshot("hawm-a", structured=baseline_state),
            snapshot("hawm-b", structured=current_state),
        )

        self.assertEqual(result["status"], MATERIAL_DRIFT)
        self.assertIn("cfc_structured.evidence", result["changed_paths"])
        self.assertTrue(result["requires_re_evaluation"])
        self.assertEqual(result["propagation_effect"], BLOCK_CARRY_FORWARD)

    def test_evidence_removal_is_material_drift(self):
        current_state = base_structured()
        current_state["evidence"] = []

        result = assess_evidence_drift(
            snapshot("hawm-a", structured=base_structured()),
            snapshot("hawm-b", structured=current_state),
        )

        self.assertEqual(result["status"], MATERIAL_DRIFT)
        self.assertEqual(result["changed_paths"], ["cfc_structured.evidence"])

    def test_scope_change_is_material_drift(self):
        current_state = base_structured()
        current_state["scope"] = "WRONG"

        result = assess_evidence_drift(
            snapshot("hawm-a", structured=base_structured()),
            snapshot("hawm-b", structured=current_state),
        )

        self.assertEqual(result["status"], MATERIAL_DRIFT)
        self.assertEqual(result["changed_paths"], ["cfc_structured.scope"])

    def test_support_requirement_change_is_material_drift(self):
        current_state = base_structured()
        current_state["required_independent_supports"] = 2

        result = assess_evidence_drift(
            snapshot("hawm-a", structured=base_structured()),
            snapshot("hawm-b", structured=current_state),
        )

        self.assertEqual(result["status"], MATERIAL_DRIFT)
        self.assertEqual(
            result["changed_paths"],
            ["cfc_structured.required_independent_supports"],
        )

    def test_evidence_reordering_alone_is_not_drift(self):
        baseline_state = base_structured()
        baseline_state["evidence"] = [
            {"polarity": "POSITIVE", "validity": "CURRENT", "id": "E1"},
            {"polarity": "NEGATIVE", "validity": "STALE", "id": "E2"},
        ]
        current_state = base_structured()
        current_state["evidence"] = list(reversed(baseline_state["evidence"]))

        result = assess_evidence_drift(
            snapshot("hawm-a", structured=baseline_state),
            snapshot("hawm-b", structured=current_state),
        )

        self.assertEqual(result["status"], NO_DRIFT)

    def test_missing_baseline_structured_state_is_unresolved_and_blocks(self):
        result = assess_evidence_drift(
            snapshot("hawm-a", goal="legacy snapshot"),
            snapshot("hawm-b", structured=base_structured()),
        )

        self.assertEqual(result["status"], UNRESOLVED)
        self.assertIn("BASELINE_CFC_STRUCTURED_STATE_MISSING", result["reason"])
        self.assertTrue(result["requires_re_evaluation"])
        self.assertEqual(result["propagation_effect"], BLOCK_CARRY_FORWARD)

    def test_missing_current_structured_state_is_unresolved_and_blocks(self):
        result = assess_evidence_drift(
            snapshot("hawm-a", structured=base_structured()),
            snapshot("hawm-b", goal="structured state removed"),
        )

        self.assertEqual(result["status"], UNRESOLVED)
        self.assertIn("CURRENT_CFC_STRUCTURED_STATE_MISSING", result["reason"])
        self.assertEqual(result["propagation_effect"], BLOCK_CARRY_FORWARD)

    def test_same_snapshot_id_with_different_content_is_unresolved(self):
        changed = base_structured()
        changed["scope"] = "WRONG"

        result = assess_evidence_drift(
            snapshot("hawm-same", structured=base_structured()),
            snapshot("hawm-same", structured=changed),
        )

        self.assertEqual(result["status"], UNRESOLVED)
        self.assertEqual(result["reason"], "SNAPSHOT_ID_CONTENT_MISMATCH")
        self.assertEqual(result["changed_paths"], ["cfc_structured.scope"])
        self.assertEqual(result["propagation_effect"], BLOCK_CARRY_FORWARD)

    def test_cross_conversation_comparison_is_unresolved(self):
        result = assess_evidence_drift(
            snapshot(
                "hawm-a",
                conversation_id="conv-a",
                structured=base_structured(),
            ),
            snapshot(
                "hawm-b",
                conversation_id="conv-b",
                structured=base_structured(),
            ),
        )

        self.assertEqual(result["status"], UNRESOLVED)
        self.assertEqual(result["reason"], "CROSS_CONVERSATION_COMPARISON")
        self.assertEqual(result["propagation_effect"], BLOCK_CARRY_FORWARD)


if __name__ == "__main__":
    unittest.main()
