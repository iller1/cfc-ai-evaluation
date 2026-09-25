import unittest

from research.structured_input_state_space import (
    StructuredState,
    admissible_states,
    canonical_states,
    differing_fields,
    one_field_mutation_pairs,
    summary,
)


class StructuredInputStateSpaceTests(unittest.TestCase):
    def test_counts(self):
        s = summary()
        self.assertEqual(s["raw_ui_configurations"], 1024)
        self.assertEqual(s["canonical_logical_states"], 640)
        self.assertEqual(s["admissible_states"], 480)
        self.assertEqual(s["rejected_contradictory_states"], 160)

    def test_omit_e2_collapses_irrelevant_fields(self):
        omitted = [s for s in canonical_states() if s.e2_mode == "OMIT"]
        self.assertTrue(omitted)
        self.assertTrue(all(s.e2_polarity is None for s in omitted))
        self.assertTrue(all(s.e2_validity is None for s in omitted))

    def test_contradictory_independence_not_admissible(self):
        self.assertFalse(
            any(
                s.provenance_shape == "SHARED_LINEAGE"
                and s.independence_authority == "VERIFIED"
                for s in admissible_states()
            )
        )

    def test_mutation_pairs_change_one_field(self):
        for a, b, field in one_field_mutation_pairs():
            self.assertEqual(differing_fields(a, b), [field])

    def test_current_to_stale_is_single_mutation(self):
        a = StructuredState(
            "POSITIVE", 1, "EXPECTED", "DISTINCT", "NONE",
            "POSITIVE", "CURRENT", "OMIT", None, None
        )
        b = StructuredState(
            "POSITIVE", 1, "EXPECTED", "DISTINCT", "NONE",
            "POSITIVE", "STALE", "OMIT", None, None
        )
        self.assertEqual(differing_fields(a, b), ["e1_validity"])


if __name__ == "__main__":
    unittest.main()
