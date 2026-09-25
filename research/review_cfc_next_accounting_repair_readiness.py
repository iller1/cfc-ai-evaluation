from __future__ import annotations

import json
from pathlib import Path


SPEC = Path("research/cfc_next_decision_accounting_repair_spec.json")
MANIFEST = Path("research/cfc_next_accounting_acceptance_manifest.json")
CASES = Path("research/structured_input_candidate_cases.json")


def main():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cases = json.loads(CASES.read_text(encoding="utf-8"))

    case = next(
        row
        for row in cases["cases"]
        if row["id"] == "SSM_005_STALE_SHARED_LINEAGE_AUTHORIZATION_RESIDUE"
    )
    taxonomy = case["minimal_blocker_accounting_taxonomy"]

    positives = manifest["blockers"]
    negatives = manifest["negative_controls"]

    positive_ids = [row["id"] for row in positives]
    negative_ids = [row["id"] for row in negatives]

    assert len(positive_ids) == 14
    assert len(set(positive_ids)) == 14
    assert len(negative_ids) == 12
    assert len(set(negative_ids)) == 12

    assert set(spec["positive_acceptance"]) == set(positive_ids)
    assert len(spec["negative_controls"]) == len(negative_ids)

    mechanisms = taxonomy["mechanism_counts"]
    assert mechanisms[
        "ENGINE_EMITTED_ACCOUNTING_SCHEMA_INCOMPATIBILITY"
    ] == 3
    assert mechanisms[
        "PUBLIC_SELECTED_EXCLUDED_ENDPOINT_REACHABILITY_INCONSISTENCY_CORE_BINDABLE"
    ] == 11

    empirical = spec["empirical_basis"]
    assert empirical["minimal_blockers"] == 14
    assert empirical["engine_emitted_accounting_schema_incompatibility"] == 3
    assert empirical["public_selected_excluded_reachability_core_bindable"] == 11
    assert empirical["negative_controls"] == 12
    assert empirical["negative_controls_fail_closed"] == 12
    assert empirical[
        "negative_controls_masked_by_legacy_selected_support_guard"
    ] == 3
    assert empirical["unexpected_bound_negative_paths"] == 0

    masked = [
        row["id"]
        for row in negatives
        if row["frozen_reference_expected"]["masked"]
    ]
    assert masked == [
        "NEG_WRONG_NODE_CORRECT_ENDPOINTS",
        "NEG_NONSEL_ENDPOINT_OUTSIDE_EVALUATED_SNAPSHOT",
        "NEG_NONSEL_ENDPOINT_WITHOUT_REQUIRED_OBLIGATION",
    ]

    assert all(
        row["target"] == "REJECT_OR_NONAUTHORIZE"
        for row in negatives
    )
    assert all(
        row["frozen_reference_expected"]["outcome"]
        == "REJECTED_OR_STOPPED_FAIL_CLOSED"
        for row in negatives
    )

    assert spec["repair_A"]["name"] == "SHARED_GENERIC_NODE_VALIDATOR"
    assert spec["repair_B"]["name"] == "EXACT_REQUIRED_OBLIGATION_ENDPOINT_ADMISSION"
    assert "source-semantic exclusion" in spec["repair_A"]["must_preserve"]
    assert (
        spec["repair_B"]["safety_boundary"]
        == "Existing exact bind/universe/hash/attestation checks remain unchanged."
    )

    invariants = manifest["invariants"]
    assert any("Frozen CFC Anchor 0.2.90rc1 remains unchanged" in x for x in invariants)
    assert any("Historical benchmark results are never rescored" in x for x in invariants)
    assert any("must not satisfy" in x and "selected_support_map" in x for x in invariants)
    assert any("fail-closed" in x for x in invariants)

    assert spec["status"] == "DESIGN_SPEC_ONLY"
    assert spec["readiness"]["implementation_status"] == "NOT_IMPLEMENTED"
    assert spec["historical_rule"] == "Do not rescore frozen historical results."

    result = {
        "test": "CFC_NEXT_DECISION_ACCOUNTING_REPAIR_READINESS",
        "frozen_reference": spec["frozen_reference"],
        "positive_fixture_count": len(positive_ids),
        "negative_control_count": len(negative_ids),
        "schema_incompatibility_positive_count": 3,
        "public_reachability_positive_count": 11,
        "masked_negative_count": len(masked),
        "negative_fail_closed_count": 12,
        "unexpected_bound_negative_paths": 0,
        "repair_A": spec["repair_A"]["name"],
        "repair_B": spec["repair_B"]["name"],
        "historical_rescore_prohibited": True,
        "frozen_reference_unchanged_required": True,
        "implementation_status": spec["readiness"]["implementation_status"],
        "status": "PASS",
    }

    Path("cfc_next_accounting_repair_readiness.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
