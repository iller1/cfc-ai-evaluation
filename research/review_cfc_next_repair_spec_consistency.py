from __future__ import annotations

import json
from pathlib import Path


def main():
    cases = json.loads(
        Path("research/structured_input_candidate_cases.json").read_text(
            encoding="utf-8"
        )
    )
    spec = json.loads(
        Path("research/cfc_next_decision_accounting_repair_spec.json").read_text(
            encoding="utf-8"
        )
    )

    case = next(
        row
        for row in cases["cases"]
        if row["id"] == "SSM_005_STALE_SHARED_LINEAGE_AUTHORIZATION_RESIDUE"
    )
    taxonomy = case["minimal_blocker_accounting_taxonomy"]

    schema_blockers = set(taxonomy["schema_incompatible_blockers"])
    reachability_blockers = set(
        taxonomy["core_bindable_public_unreachable_blockers"]
    )
    all_blockers = schema_blockers | reachability_blockers

    assert taxonomy["blocker_count"] == 14
    assert len(schema_blockers) == 3
    assert len(reachability_blockers) == 11
    assert len(all_blockers) == 14

    empirical = spec["empirical_basis"]
    assert empirical["minimal_blockers"] == taxonomy["blocker_count"]
    assert (
        empirical["engine_emitted_accounting_schema_incompatibility"]
        == taxonomy["mechanism_counts"][
            "ENGINE_EMITTED_ACCOUNTING_SCHEMA_INCOMPATIBILITY"
        ]
    )
    assert (
        empirical["public_selected_excluded_reachability_core_bindable"]
        == taxonomy["mechanism_counts"][
            "PUBLIC_SELECTED_EXCLUDED_ENDPOINT_REACHABILITY_INCONSISTENCY_CORE_BINDABLE"
        ]
    )

    assert set(spec["positive_acceptance"]) == all_blockers
    assert spec["frozen_reference"] == "CFC Anchor 0.2.90rc1"
    assert spec["status"] == "DESIGN_SPEC_ONLY"
    assert spec["repair_A"]["name"] == "SHARED_GENERIC_NODE_VALIDATOR"
    assert (
        spec["repair_B"]["name"]
        == "EXACT_REQUIRED_OBLIGATION_ENDPOINT_ADMISSION"
    )
    assert "Do not rescore" in spec["historical_rule"]

    result = {
        "test": "CFC_NEXT_REPAIR_SPEC_CONSISTENCY",
        "frozen_reference": spec["frozen_reference"],
        "blocker_count": len(all_blockers),
        "schema_incompatible": len(schema_blockers),
        "core_bindable_public_unreachable": len(reachability_blockers),
        "positive_acceptance_exactly_covers_taxonomy": True,
        "status": "PASS",
    }
    Path("cfc_next_repair_spec_consistency.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
