from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from demonstrator import server as demo_server


BASE = {
    "scope": "EXPECTED",
    "provenance_shape": "DISTINCT",
    "independence_authority": "VERIFIED",
    "evidence": [
        {"polarity": "POSITIVE", "validity": "CURRENT"},
        {"polarity": "POSITIVE", "validity": "CURRENT"},
    ],
}


def run_case(conclusion: str, required: int) -> dict:
    payload = dict(BASE)
    payload["conclusion"] = conclusion
    payload["required_independent_supports"] = required
    if conclusion == "NEGATIVE":
        payload["evidence"] = [
            {"polarity": "NEGATIVE", "validity": "CURRENT"},
            {"polarity": "NEGATIVE", "validity": "CURRENT"},
        ]
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
        "constraint_relation_coverage_violations": r.get("constraint_relation_coverage_violations") or [],
        "constraint_coverage_violations": r.get("constraint_coverage_violations") or [],
        "global_consistency_violations": r.get("global_consistency_violations") or [],
        "critical_unresolved": r.get("critical_unresolved") or [],
    }


def compare(conclusion: str) -> dict:
    one = run_case(conclusion, 1)
    two = run_case(conclusion, 2)
    return {
        "conclusion": conclusion,
        "required_1": one,
        "required_2": two,
        "false_gates_removed_at_2": sorted(set(one["false_gates"]) - set(two["false_gates"])),
        "false_gates_added_at_2": sorted(set(two["false_gates"]) - set(one["false_gates"])),
        "closure_transition": f'{one["decision"]}/{one["claim_state"]}->{two["decision"]}/{two["claim_state"]}',
    }


def main() -> dict:
    demo_server.ensure_runtime()
    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "SUPPORT_THRESHOLD_REVERSAL_MINIMAL_PAIR",
        "positive": compare("POSITIVE"),
        "negative": compare("NEGATIVE"),
        "interpretation_boundary": (
            "Observed controller behavior only. This script does not classify the reversal "
            "as intended or erroneous."
        ),
    }
    Path("support_threshold_reversal_review.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
