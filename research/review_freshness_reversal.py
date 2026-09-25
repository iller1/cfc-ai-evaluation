from __future__ import annotations

import json
from pathlib import Path

from demonstrator import server as demo_server


def run_case(e1_polarity: str, e1_validity: str, e2_polarity: str) -> dict:
    payload = {
        "conclusion": "POSITIVE",
        "required_independent_supports": 1,
        "scope": "EXPECTED",
        "provenance_shape": "DISTINCT",
        "independence_authority": "NONE",
        "evidence": [
            {"polarity": e1_polarity, "validity": e1_validity},
            {"polarity": e2_polarity, "validity": "CURRENT"},
        ],
    }
    result = demo_server.run_custom(payload)
    p = result["presentation"]
    r = result["result"]
    return {
        "input": payload,
        "decision": p.get("decision"),
        "claim_state": p.get("claim_state"),
        "reason": p.get("reason"),
        "false_gates": p.get("false_gates") or [],
        "control_closure": bool(r.get("control_closure")),
        "claim_support_policy_violations": r.get("claim_support_policy_violations") or [],
        "critical_unresolved": r.get("critical_unresolved") or [],
        "global_consistency_violations": r.get("global_consistency_violations") or [],
    }


def compare(label: str, e1_polarity: str, e2_polarity: str) -> dict:
    current = run_case(e1_polarity, "CURRENT", e2_polarity)
    stale = run_case(e1_polarity, "STALE", e2_polarity)
    return {
        "label": label,
        "current": current,
        "stale": stale,
        "transition": (
            f'{current["decision"]}/{current["claim_state"]}'
            f'->{stale["decision"]}/{stale["claim_state"]}'
        ),
        "false_gates_removed_when_stale": sorted(
            set(current["false_gates"]) - set(stale["false_gates"])
        ),
        "false_gates_added_when_stale": sorted(
            set(stale["false_gates"]) - set(current["false_gates"])
        ),
    }


def main() -> dict:
    demo_server.ensure_runtime()
    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "FRESHNESS_REVERSAL_MINIMAL_PAIRS",
        "matching_support_becomes_stale": compare(
            "matching-current-plus-matching-current -> stale-plus-current",
            "POSITIVE",
            "POSITIVE",
        ),
        "opposing_record_becomes_stale": compare(
            "opposing-current-plus-matching-current -> stale-opposition-plus-current",
            "NEGATIVE",
            "POSITIVE",
        ),
        "interpretation_boundary": (
            "Observed frozen-controller behavior only. Stale evidence is not treated "
            "as positive evidence; review asks whether it is correctly excluded from "
            "the active decision-relevant universe."
        ),
    }
    Path("freshness_reversal_review.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
