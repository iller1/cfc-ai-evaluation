import copy
import unittest

from control_stack.evidence_provenance import (
    BLOCK_EVIDENCE,
    EVIDENCE_APPLICABLE,
    EVIDENCE_INVALID,
    EVIDENCE_PARTIAL,
    EVIDENCE_UNKNOWN,
    NO_ADDITIONAL_BLOCK,
    assess_evidence_provenance,
)


def records():
    return [
        {
            "evidence_id": "E1",
            "source_id": "S1",
            "validity": "CURRENT",
            "scope_status": "MATCH",
            "failure_domain_id": "FD1",
        },
        {
            "evidence_id": "E2",
            "source_id": "S2",
            "validity": "CURRENT",
            "scope_status": "MATCH",
            "failure_domain_id": "FD2",
        },
    ]


def provenance_receipts(state_id="state-1"):
    return [
        {
            "receipt_id": "prov-1",
            "state_id": state_id,
            "evidence_id": "E1",
            "source_id": "S1",
            "status": "ESTABLISHED",
        },
        {
            "receipt_id": "prov-2",
            "state_id": state_id,
            "evidence_id": "E2",
            "source_id": "S2",
            "status": "ESTABLISHED",
        },
    ]


def dependency_receipt(state_id="state-1", status="RESOLVED"):
    return {
        "receipt_id": "dep-1",
        "state_id": state_id,
        "evidence_ids": ["E1", "E2"],
        "failure_domains": {
            "E1": "FD1",
            "E2": "FD2",
        },
        "status": status,
    }


def assess(
    *,
    state_id="state-1",
    evidence_set=None,
    provenance=None,
    dependency=None,
    missing=None,
    drift="NO_DRIFT",
):
    return assess_evidence_provenance(
        state_id=state_id,
        evidence_set=records() if evidence_set is None else evidence_set,
        provenance_receipts=(
            provenance_receipts(state_id)
            if provenance is None
            else provenance
        ),
        dependency_receipt=(
            dependency_receipt(state_id)
            if dependency is None
            else dependency
        ),
        missing_evidence=[] if missing is None else missing,
        drift_state=drift,
    )


class EvidenceProvenanceTests(unittest.TestCase):
    def test_exact_explicit_state_is_applicable_but_not_authority(self):
        result = assess()

        self.assertEqual(result["status"], EVIDENCE_APPLICABLE)
        self.assertEqual(
            result["reason"],
            "EXPLICIT_EVIDENCE_PROVENANCE_STATE_APPLICABLE",
        )
        self.assertEqual(
            result["evidence"]["provenance_state"], "ESTABLISHED"
        )
        self.assertEqual(
            result["evidence"]["applicability_state"], "APPLICABLE"
        )
        self.assertEqual(
            result["evidence"]["dependency_state"], "RESOLVED"
        )
        self.assertFalse(result["requires_review"])
        self.assertEqual(result["propagation_effect"], NO_ADDITIONAL_BLOCK)
        self.assertEqual(
            result["authorization_effect"],
            "DOES_NOT_AUTHORIZE_CLOSURE",
        )
        self.assertIn(
            "NO_FREE_TEXT_SOURCE_TRUTH_OR_INDEPENDENCE_INFERENCE",
            result["boundary"],
        )

    def test_source_ids_alone_do_not_establish_provenance(self):
        result = assess(provenance=[])

        self.assertEqual(result["status"], EVIDENCE_UNKNOWN)
        self.assertEqual(result["evidence"]["provenance_state"], "UNKNOWN")
        self.assertIn("PROVENANCE_NOT_ESTABLISHED", result["diagnostics"])
        self.assertEqual(result["propagation_effect"], BLOCK_EVIDENCE)

    def test_distinct_source_ids_do_not_resolve_dependencies(self):
        result = assess_evidence_provenance(
            state_id="state-1",
            evidence_set=records(),
            provenance_receipts=provenance_receipts(),
            dependency_receipt=None,
            missing_evidence=[],
            drift_state="NO_DRIFT",
        )

        self.assertEqual(result["status"], EVIDENCE_UNKNOWN)
        self.assertEqual(result["evidence"]["dependency_state"], "UNKNOWN")
        self.assertIn("DEPENDENCY_NOT_RESOLVED", result["diagnostics"])

    def test_provenance_receipt_wrong_state_is_invalid(self):
        result = assess(provenance=provenance_receipts("state-other"))

        self.assertEqual(result["status"], EVIDENCE_INVALID)
        self.assertEqual(
            result["reason"], "PROVENANCE_RECEIPT_STATE_MISMATCH"
        )

    def test_provenance_receipt_wrong_source_is_invalid(self):
        provenance = provenance_receipts()
        provenance[0]["source_id"] = "S-OTHER"

        result = assess(provenance=provenance)

        self.assertEqual(result["status"], EVIDENCE_INVALID)
        self.assertEqual(
            result["reason"], "PROVENANCE_RECEIPT_SOURCE_MISMATCH"
        )

    def test_duplicate_provenance_receipt_for_evidence_is_invalid(self):
        provenance = provenance_receipts()
        extra = copy.deepcopy(provenance[0])
        extra["receipt_id"] = "prov-extra"
        provenance.append(extra)

        result = assess(provenance=provenance)

        self.assertEqual(result["status"], EVIDENCE_INVALID)
        self.assertEqual(
            result["reason"],
            "MULTIPLE_PROVENANCE_RECEIPTS_FOR_EVIDENCE",
        )

    def test_stale_record_is_partial_not_applicable(self):
        evidence_set = records()
        evidence_set[0]["validity"] = "STALE"

        result = assess(evidence_set=evidence_set)

        self.assertEqual(result["status"], EVIDENCE_PARTIAL)
        self.assertEqual(
            result["evidence"]["applicability_state"],
            "NOT_APPLICABLE",
        )
        self.assertTrue(result["requires_review"])

    def test_wrong_scope_is_partial_not_applicable(self):
        evidence_set = records()
        evidence_set[0]["scope_status"] = "WRONG"

        result = assess(evidence_set=evidence_set)

        self.assertEqual(result["status"], EVIDENCE_PARTIAL)
        self.assertEqual(
            result["evidence"]["applicability_state"],
            "NOT_APPLICABLE",
        )

    def test_unknown_record_state_is_unknown(self):
        evidence_set = records()
        evidence_set[0]["validity"] = "UNKNOWN"

        result = assess(evidence_set=evidence_set)

        self.assertEqual(result["status"], EVIDENCE_UNKNOWN)
        self.assertEqual(
            result["evidence"]["applicability_state"],
            "UNKNOWN",
        )

    def test_invalid_record_state_is_invalid(self):
        evidence_set = records()
        evidence_set[0]["validity"] = "INVALID"

        result = assess(evidence_set=evidence_set)

        self.assertEqual(result["status"], EVIDENCE_INVALID)
        self.assertEqual(result["reason"], "EVIDENCE_RECORD_INVALID")

    def test_missing_evidence_blocks_applicable_status(self):
        result = assess(missing=["EXPECTED_PRIMARY_SOURCE"])

        self.assertEqual(result["status"], EVIDENCE_PARTIAL)
        self.assertIn("MISSING_EVIDENCE_PRESENT", result["diagnostics"])

    def test_material_drift_requires_reevaluation(self):
        result = assess(drift="MATERIAL_DRIFT")

        self.assertEqual(result["status"], EVIDENCE_PARTIAL)
        self.assertIn("DRIFT_NOT_CLEAR", result["diagnostics"])

    def test_unresolved_drift_is_unknown(self):
        result = assess(drift="UNRESOLVED")

        self.assertEqual(result["status"], EVIDENCE_UNKNOWN)
        self.assertIn("DRIFT_NOT_CLEAR", result["diagnostics"])

    def test_not_assessed_drift_is_unknown(self):
        result = assess(drift="NOT_ASSESSED")

        self.assertEqual(result["status"], EVIDENCE_UNKNOWN)

    def test_dependency_conflict_is_partial(self):
        result = assess(dependency=dependency_receipt(status="CONFLICTING"))

        self.assertEqual(result["status"], EVIDENCE_PARTIAL)
        self.assertEqual(
            result["evidence"]["dependency_state"],
            "CONFLICTING",
        )

    def test_resolved_dependency_must_cover_exact_evidence_set(self):
        dependency = dependency_receipt()
        dependency["evidence_ids"] = ["E1"]

        result = assess(dependency=dependency)

        self.assertEqual(result["status"], EVIDENCE_INVALID)
        self.assertEqual(
            result["reason"], "RESOLVED_DEPENDENCY_COVERAGE_MISMATCH"
        )

    def test_resolved_dependency_must_match_failure_domain_map(self):
        dependency = dependency_receipt()
        dependency["failure_domains"]["E2"] = "FD-WRONG"

        result = assess(dependency=dependency)

        self.assertEqual(result["status"], EVIDENCE_INVALID)
        self.assertEqual(
            result["reason"], "RESOLVED_FAILURE_DOMAIN_VALUE_MISMATCH"
        )

    def test_resolved_dependency_requires_failure_domain_on_each_record(self):
        evidence_set = records()
        evidence_set[1]["failure_domain_id"] = None
        dependency = dependency_receipt()
        dependency["failure_domains"]["E2"] = None

        result = assess(
            evidence_set=evidence_set,
            dependency=dependency,
        )

        self.assertEqual(result["status"], EVIDENCE_INVALID)
        self.assertEqual(
            result["reason"],
            "RESOLVED_DEPENDENCY_REQUIRES_FAILURE_DOMAIN",
        )

    def test_duplicate_evidence_id_is_invalid(self):
        evidence_set = records()
        evidence_set[1]["evidence_id"] = "E1"

        result = assess(evidence_set=evidence_set)

        self.assertEqual(result["status"], EVIDENCE_INVALID)
        self.assertEqual(result["reason"], "DUPLICATE_EVIDENCE_ID")

    def test_empty_evidence_set_is_unknown(self):
        result = assess_evidence_provenance(
            state_id="state-1",
            evidence_set=[],
            provenance_receipts=[],
            dependency_receipt=None,
            missing_evidence=[],
            drift_state="NO_DRIFT",
        )

        self.assertEqual(result["status"], EVIDENCE_UNKNOWN)
        self.assertEqual(result["reason"], "EVIDENCE_SET_EMPTY")

    def test_input_records_are_not_mutated(self):
        evidence_set = records()
        original = copy.deepcopy(evidence_set)

        assess(evidence_set=evidence_set)

        self.assertEqual(evidence_set, original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
