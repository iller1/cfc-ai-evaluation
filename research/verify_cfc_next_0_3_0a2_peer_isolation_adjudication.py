from __future__ import annotations

import json
from pathlib import Path

from research import review_minimal_blocker_accounting_taxonomy as taxonomy


CONTEXT_PATH = Path(
    "cfc_next_0_3_0a2_peer_controller_isolation.json"
)
IDENTITY_PATH = Path(
    "cfc_next_0_3_0a2_peer_identity_isolation.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> dict:
    context = _load(CONTEXT_PATH)
    identity = _load(IDENTITY_PATH)
    expected = sorted(taxonomy.BLOCKERS)

    assert context["scenario_count"] == 112
    assert context["scenario_errors"] == []
    assert context["accounting_authorization_installed"] is False
    assert context["classification"] == (
        "PEER_CONTROLLER_CONTEXT_ISOLATION_FINDING"
    )
    assert sorted(
        context["global_shared_relation_id_interference"]
    ) == expected
    assert sorted(
        context["tenant_namespaced_relation_id_interference"]
    ) == expected

    for row in context["comparisons"]:
        assert row["a_changed_after_b"] is True
        assert row["b_changed_after_a"] is True
        for standalone in ("a_only", "b_only"):
            assert row[standalone]["claim_state"] == "VERIFIED"
            assert (
                row[standalone]["required_obligation_count"] == 1
            )
            assert row[standalone]["control_closure"] is False
        for after_peer in ("a_after_b", "b_after_a"):
            assert row[after_peer]["claim_state"] == "UNRESOLVED"
            assert (
                row[after_peer]["required_obligation_count"] == 0
            )
            assert row[after_peer]["control_closure"] is False

    assert identity["scenario_count"] == 112
    assert identity["scenario_errors"] == []
    assert identity["accounting_authorization_installed"] is False
    assert identity["classification"] == (
        "SHARED_CANONICAL_IDENTITY_CROSS_CONTEXT_INTERFERENCE"
    )
    assert sorted(
        identity["shared_canonical_identity_interference"]
    ) == expected
    assert (
        identity[
            "tenant_namespaced_canonical_identity_interference"
        ]
        == []
    )

    shared_rows = [
        row for row in identity["comparisons"]
        if row["identity_mode"] == "SHARED_CANONICAL_IDENTITY"
    ]
    namespaced_rows = [
        row for row in identity["comparisons"]
        if (
            row["identity_mode"]
            == "TENANT_NAMESPACED_CANONICAL_IDENTITY"
        )
    ]
    assert len(shared_rows) == 14
    assert len(namespaced_rows) == 14

    for row in shared_rows:
        assert row["a_changed_after_b"] is True
        assert row["b_changed_after_a"] is True
        assert row["a_only"]["claim_state"] == "VERIFIED"
        assert row["b_only"]["claim_state"] == "VERIFIED"
        assert row["a_after_b"]["claim_state"] == "UNRESOLVED"
        assert row["b_after_a"]["claim_state"] == "UNRESOLVED"
        assert row["a_after_b"]["control_closure"] is False
        assert row["b_after_a"]["control_closure"] is False

    for row in namespaced_rows:
        assert row["a_changed_after_b"] is False
        assert row["b_changed_after_a"] is False
        assert row["a_only"] == row["a_after_b"]
        assert row["b_only"] == row["b_after_a"]
        assert row["a_only"]["claim_state"] == "VERIFIED"
        assert row["b_only"]["claim_state"] == "VERIFIED"
        assert row["a_only"]["required_obligation_count"] == 1
        assert row["b_only"]["required_obligation_count"] == 1
        assert row["a_only"]["control_closure"] is False
        assert row["b_only"]["control_closure"] is False

    result = {
        "test": "CFC_NEXT_0_3_0A2_PEER_ISOLATION_ADJUDICATION",
        "blocker_family_count": len(expected),
        "peer_context_scenarios": context["scenario_count"],
        "peer_identity_scenarios": identity["scenario_count"],
        "total_fresh_process_scenarios": (
            context["scenario_count"] + identity["scenario_count"]
        ),
        "shared_canonical_identity_interference_count": len(
            identity["shared_canonical_identity_interference"]
        ),
        "tenant_namespaced_identity_interference_count": len(
            identity[
                "tenant_namespaced_canonical_identity_interference"
            ]
        ),
        "unauthorized_closure_observed": False,
        "accounting_authorization_installed": False,
        "deployment_boundary": (
            "same-process independent identity registrations for the "
            "same canonical entity/event/version can interfere; "
            "process isolation or registry-level canonical identity "
            "coordination is required for independent sessions"
        ),
        "classification": (
            "FAIL_CLOSED_SHARED_CANONICAL_IDENTITY_"
            "CROSS_CONTEXT_INTERFERENCE"
        ),
        "status": "PASS",
    }

    Path(
        "cfc_next_0_3_0a2_peer_isolation_adjudication.json"
    ).write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
