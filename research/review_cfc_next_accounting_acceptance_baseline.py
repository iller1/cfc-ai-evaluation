from __future__ import annotations

import json
from pathlib import Path

from research.review_minimal_blocker_accounting_taxonomy import (
    BLOCKERS,
    run_isolated,
)

MANIFEST_PATH = Path(
    "research/cfc_next_accounting_acceptance_manifest.json"
)
REPAIR_SPEC_PATH = Path(
    "research/cfc_next_decision_accounting_repair_spec.json"
)


def main():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    repair_spec = json.loads(REPAIR_SPEC_PATH.read_text(encoding="utf-8"))

    expected = {
        row["id"]: row
        for row in manifest["blockers"]
    }
    assert tuple(expected) == tuple(BLOCKERS)
    assert len(expected) == 14
    assert manifest["frozen_reference"] == "CFC Anchor 0.2.90rc1"
    assert manifest["status"] == "REFERENCE_BASELINE_PLUS_TARGET_CONTRACT"

    repair_positive = set(repair_spec["positive_acceptance"])
    assert repair_positive == set(BLOCKERS)

    rows = []
    mechanism_counts = {}
    for blocker in BLOCKERS:
        observed = run_isolated(blocker)
        target = expected[blocker]
        frozen_expected = target["frozen_reference_expected"]

        assert observed["baseline"]["claim_state"] == frozen_expected["claim_state"]
        assert observed["baseline"]["control_closure"] == frozen_expected["control_closure"]
        assert observed["baseline"]["false_gates"] == frozen_expected["false_gates"]
        assert observed["required_obligation_count"] == 1
        assert observed["mechanisms"] == [frozen_expected["mechanism"]]

        obligation = observed["obligations"][0]
        mechanism = obligation["mechanism"]
        mechanism_counts[mechanism] = mechanism_counts.get(mechanism, 0) + 1

        if mechanism == "ENGINE_EMITTED_ACCOUNTING_SCHEMA_INCOMPATIBILITY":
            assert obligation["internal_registry"]["registered"] is False
            assert "invalid generic dependency node" in (
                obligation["internal_registry"]["error"] or ""
            )
            assert obligation["public_draft"]["draft_created"] is False
            assert "invalid generic dependency node" in (
                obligation["public_draft"]["error"] or ""
            )
            assert obligation["direct_core_after_exact_bind"]["attempted"] is False

        elif mechanism == (
            "PUBLIC_SELECTED_EXCLUDED_ENDPOINT_REACHABILITY_"
            "INCONSISTENCY_CORE_BINDABLE"
        ):
            assert obligation["internal_registry"]["registered"] is True
            assert obligation["internal_registry"]["binding_state"] == "BOUND"
            assert obligation["public_draft"]["draft_created"] is False
            assert "endpoints must be selected supports" in (
                obligation["public_draft"]["error"] or ""
            )
            core = obligation["direct_core_after_exact_bind"]
            assert core["attempted"] is True
            assert core["claim_state"] == "VERIFIED"
            assert core["control_closure"] is True
            assert core["decision_support_closure_valid"] is True
            assert core["decision_support_closure_certificate_present"] is True
            assert core["false_gates"] == []
        else:
            raise AssertionError(f"unexpected mechanism: {mechanism}")

        cfc_next_target = target["cfc_next_target"]
        assert cfc_next_target["exact_obligation_publicly_representable"] is True
        assert cfc_next_target["selected_support_map_must_remain_engine_exact"] is True
        assert cfc_next_target["exact_verified_accounting_must_bind"] is True
        assert cfc_next_target["claim_state"] == "VERIFIED"
        assert cfc_next_target["decision_support_closure_valid"] is True
        assert cfc_next_target["decision_support_closure_certificate_present"] is True
        assert cfc_next_target["control_closure"] is True
        assert cfc_next_target["false_gates"] == []

        rows.append({
            "blocker": blocker,
            "frozen_reference_mechanism": mechanism,
            "frozen_reference_signature": observed["baseline"],
            "cfc_next_target": cfc_next_target,
        })

    assert mechanism_counts == {
        "ENGINE_EMITTED_ACCOUNTING_SCHEMA_INCOMPATIBILITY": 3,
        "PUBLIC_SELECTED_EXCLUDED_ENDPOINT_REACHABILITY_INCONSISTENCY_CORE_BINDABLE": 11,
    }

    negative_ids = [row["id"] for row in manifest["negative_controls"]]
    assert len(negative_ids) == 12
    assert len(set(negative_ids)) == 12
    assert all(
        row["target"] == "REJECT_OR_NONAUTHORIZE"
        for row in manifest["negative_controls"]
    )

    result = {
        "test": "CFC_NEXT_DECISION_ACCOUNTING_ACCEPTANCE_BASELINE",
        "frozen_reference": manifest["frozen_reference"],
        "blocker_count": len(rows),
        "mechanism_counts": mechanism_counts,
        "negative_control_contract_count": len(negative_ids),
        "frozen_reference_matches_manifest": True,
        "cfc_next_target_exactly_covers_positive_taxonomy": True,
        "status": "PASS",
        "rows": rows,
    }

    Path("cfc_next_accounting_acceptance_baseline.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
