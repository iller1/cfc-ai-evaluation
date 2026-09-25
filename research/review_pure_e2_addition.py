from __future__ import annotations

import json
from pathlib import Path

from demonstrator import server as demo_server


BASE = {
    "conclusion": "POSITIVE",
    "required_independent_supports": 1,
    "scope": "EXPECTED",
    "provenance_shape": "DISTINCT",
    "independence_authority": "NONE",
}


def run(evidence):
    payload = dict(BASE)
    payload["evidence"] = evidence
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
        "global_consistency_violations": r.get("global_consistency_violations") or [],
        "critical_unresolved": r.get("critical_unresolved") or [],
    }


def pair(label, before_evidence, added):
    before = run(before_evidence)
    after = run(before_evidence + [added])
    return {
        "label": label,
        "before": before,
        "after": after,
        "transition": f'{before["decision"]}/{before["claim_state"]}->{after["decision"]}/{after["claim_state"]}',
        "false_gates_removed": sorted(set(before["false_gates"]) - set(after["false_gates"])),
        "false_gates_added": sorted(set(after["false_gates"]) - set(before["false_gates"])),
    }


def main():
    demo_server.ensure_runtime()
    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "PURE_E2_ADDITION_MINIMAL_PAIRS",
        "support_plus_support": pair(
            "current support + add current support",
            [{"polarity": "POSITIVE", "validity": "CURRENT"}],
            {"polarity": "POSITIVE", "validity": "CURRENT"},
        ),
        "support_plus_conflict": pair(
            "current support + add current opposition",
            [{"polarity": "POSITIVE", "validity": "CURRENT"}],
            {"polarity": "NEGATIVE", "validity": "CURRENT"},
        ),
        "stale_plus_support": pair(
            "stale support + add current support",
            [{"polarity": "POSITIVE", "validity": "STALE"}],
            {"polarity": "POSITIVE", "validity": "CURRENT"},
        ),
        "stale_opposition_plus_support": pair(
            "stale opposition + add current support",
            [{"polarity": "NEGATIVE", "validity": "STALE"}],
            {"polarity": "POSITIVE", "validity": "CURRENT"},
        ),
        "interpretation_boundary": (
            "These are pure E2 additions under DISTINCT provenance and NONE independence authority. "
            "No E1 provenance rewrite and no independence certificate installation occur."
        ),
    }
    Path("pure_e2_addition_review.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
