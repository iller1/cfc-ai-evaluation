from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pro_beta.cfc_execution import run_structured_hawm_state


@dataclass(frozen=True)
class BridgeScenario:
    scenario_id: str
    state: dict[str, Any]
    expected_claim_state: str
    expected_decision: str
    required_false_gates: tuple[str, ...] = ()


BASE = {
    "conclusion": "POSITIVE",
    "scope": "EXPECTED",
}


SCENARIOS = (
    BridgeScenario(
        "BRIDGE_01_SUFFICIENT_SUPPORT",
        {
            **BASE,
            "required_independent_supports": 1,
            "provenance_shape": "DISTINCT",
            "independence_authority": "NONE",
            "evidence": [{"polarity": "POSITIVE", "validity": "CURRENT"}],
        },
        "VERIFIED",
        "ALLOW",
    ),
    BridgeScenario(
        "BRIDGE_02_INSUFFICIENT_SUPPORT",
        {
            **BASE,
            "required_independent_supports": 2,
            "provenance_shape": "DISTINCT",
            "independence_authority": "NONE",
            "evidence": [{"polarity": "POSITIVE", "validity": "CURRENT"}],
        },
        "SUPPORTED",
        "STOP",
        ("claim_specific_support_policy_valid",),
    ),
    BridgeScenario(
        "BRIDGE_03_ACTIVE_CONTRADICTION",
        {
            **BASE,
            "required_independent_supports": 1,
            "provenance_shape": "DISTINCT",
            "independence_authority": "NONE",
            "evidence": [
                {"polarity": "POSITIVE", "validity": "CURRENT"},
                {"polarity": "NEGATIVE", "validity": "CURRENT"},
            ],
        },
        "QUARANTINED",
        "STOP",
        ("global_consistency_valid",),
    ),
    BridgeScenario(
        "BRIDGE_04_STALE_EVIDENCE",
        {
            **BASE,
            "required_independent_supports": 1,
            "provenance_shape": "DISTINCT",
            "independence_authority": "NONE",
            "evidence": [{"polarity": "POSITIVE", "validity": "STALE"}],
        },
        "UNRESOLVED",
        "STOP",
        ("decision_support_closure_valid",),
    ),
    BridgeScenario(
        "BRIDGE_05_WRONG_SCOPE",
        {
            **BASE,
            "scope": "WRONG",
            "required_independent_supports": 1,
            "provenance_shape": "DISTINCT",
            "independence_authority": "NONE",
            "evidence": [{"polarity": "POSITIVE", "validity": "CURRENT"}],
        },
        "VERIFIED",
        "STOP",
        ("scope_adequacy_valid",),
    ),
    BridgeScenario(
        "BRIDGE_06_INDEPENDENCE_AUTHORITY_AB_ALLOW",
        {
            **BASE,
            "required_independent_supports": 2,
            "provenance_shape": "DISTINCT",
            "independence_authority": "VERIFIED",
            "evidence": [
                {"polarity": "POSITIVE", "validity": "CURRENT"},
                {"polarity": "POSITIVE", "validity": "CURRENT"},
            ],
        },
        "VERIFIED",
        "ALLOW",
    ),
    BridgeScenario(
        "BRIDGE_07_SHARED_LINEAGE",
        {
            **BASE,
            "required_independent_supports": 2,
            "provenance_shape": "SHARED_LINEAGE",
            "independence_authority": "NONE",
            "evidence": [
                {"polarity": "POSITIVE", "validity": "CURRENT"},
                {"polarity": "POSITIVE", "validity": "CURRENT"},
            ],
        },
        "SUPPORTED",
        "STOP",
        (
            "claim_specific_support_policy_valid",
            "source_independence_semantics_valid",
        ),
    ),
)


def run_bridge_acceptance_pack() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    passed = True

    for scenario in SCENARIOS:
        executed = run_structured_hawm_state(
            {"cfc_structured": scenario.state}
        )
        presentation = executed["presentation"]
        false_gates = set(presentation.get("false_gates") or [])
        checks = {
            "anchor": executed["controller_anchor"] == "0.2.90rc1",
            "boundary": executed["boundary"]
            == "STRUCTURED_HAWM_FIELDS_ONLY_NO_NATURAL_LANGUAGE_INFERENCE",
            "claim_state": presentation.get("claim_state")
            == scenario.expected_claim_state,
            "decision": presentation.get("decision")
            == scenario.expected_decision,
            "false_gates": all(
                gate in false_gates for gate in scenario.required_false_gates
            ),
        }
        row_passed = all(checks.values())
        passed = passed and row_passed
        rows.append(
            {
                "scenario_id": scenario.scenario_id,
                "passed": row_passed,
                "expected": {
                    "claim_state": scenario.expected_claim_state,
                    "decision": scenario.expected_decision,
                    "required_false_gates": list(
                        scenario.required_false_gates
                    ),
                },
                "actual": {
                    "claim_state": presentation.get("claim_state"),
                    "decision": presentation.get("decision"),
                    "false_gates": presentation.get("false_gates") or [],
                },
                "checks": checks,
            }
        )

    return {
        "pack": "HAWM_CFC_BRIDGE_ACCEPTANCE_V1",
        "controller_anchor": "0.2.90rc1",
        "scenario_count": len(SCENARIOS),
        "passed": passed,
        "boundary": "BOUNDED_STRUCTURED_SYNTHETIC_INPUT_NOT_FREE_TEXT_ANALYSIS",
        "results": rows,
    }
