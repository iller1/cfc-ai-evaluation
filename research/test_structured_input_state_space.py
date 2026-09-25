import unittest

from research.structured_input_state_space import (
    StructuredState,
    admissible_states,
    canonical_states,
    differing_fields,
    e2_add_remove_pairs,
    one_field_mutation_pairs,
    semantic_mutation_edges,
    summary,
)
from research.run_structured_state_space_against_frozen import (
    support_completeness_runtime_coupling,
)


class StructuredInputStateSpaceTests(unittest.TestCase):
    def test_counts(self):
        s = summary()
        self.assertEqual(s["raw_ui_configurations"], 1024)
        self.assertEqual(s["canonical_logical_states"], 640)
        self.assertEqual(s["admissible_states"], 480)
        self.assertEqual(s["rejected_contradictory_states"], 160)
        self.assertEqual(s["one_field_mutation_pairs"], 1904)
        self.assertEqual(s["semantic_mutation_edges"], 2288)
        self.assertEqual(s["mutation_families"]["SUPPORT_COMPLETENESS"], 384)

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

    def test_e2_add_remove_is_one_semantic_operation(self):
        pairs = list(e2_add_remove_pairs())
        self.assertEqual(len(pairs), 384)
        self.assertTrue(all(family == "SUPPORT_COMPLETENESS" for _, _, family in pairs))
        self.assertTrue(all(a.e2_mode == "OMIT" and b.e2_mode == "INCLUDE" for a, b, _ in pairs))

    def test_semantic_edges_include_field_and_e2_operations(self):
        self.assertEqual(len(list(semantic_mutation_edges())), 2288)

    def test_e2_runtime_coupling_classes(self):
        base = StructuredState(
            "POSITIVE", 1, "EXPECTED", "DISTINCT", "NONE",
            "POSITIVE", "CURRENT", "OMIT", None, None
        )
        pure = StructuredState(
            "POSITIVE", 1, "EXPECTED", "DISTINCT", "NONE",
            "POSITIVE", "CURRENT", "INCLUDE", "POSITIVE", "CURRENT"
        )
        cert = StructuredState(
            "POSITIVE", 1, "EXPECTED", "DISTINCT", "VERIFIED",
            "POSITIVE", "CURRENT", "INCLUDE", "POSITIVE", "CURRENT"
        )
        cert_before = StructuredState(
            "POSITIVE", 1, "EXPECTED", "DISTINCT", "VERIFIED",
            "POSITIVE", "CURRENT", "OMIT", None, None
        )
        shared = StructuredState(
            "POSITIVE", 1, "EXPECTED", "SHARED_LINEAGE", "NONE",
            "POSITIVE", "CURRENT", "INCLUDE", "POSITIVE", "CURRENT"
        )
        shared_before = StructuredState(
            "POSITIVE", 1, "EXPECTED", "SHARED_LINEAGE", "NONE",
            "POSITIVE", "CURRENT", "OMIT", None, None
        )
        self.assertEqual(
            support_completeness_runtime_coupling(base, pure),
            "PURE_E2_ADDITION",
        )
        self.assertEqual(
            support_completeness_runtime_coupling(cert_before, cert),
            "E2_PLUS_INDEPENDENCE_CERT_INSTALL",
        )
        self.assertEqual(
            support_completeness_runtime_coupling(shared_before, shared),
            "E2_PLUS_E1_PROVENANCE_REWRITE",
        )

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
