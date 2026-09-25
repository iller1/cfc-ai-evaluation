from __future__ import annotations

import json
from pathlib import Path

from demonstrator import server as demo_server


def run(e2_validity: str) -> dict:
    payload = {
        "conclusion": "POSITIVE",
        "required_independent_supports": 1,
        "scope": "EXPECTED",
        "provenance_shape": "SHARED_LINEAGE",
        "independence_authority": "NONE",
        "evidence": [
            {"polarity": "POSITIVE", "validity": "CURRENT"},
            {"polarity": "POSITIVE", "validity": e2_validity},
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
        "constraint_relation_coverage_violations": r.get("constraint_relation_coverage_violations") or [],
        "constraint_coverage_violations": r.get("constraint_coverage_violations") or [],
        "global_consistency_violations": r.get("global_consistency_violations") or [],
        "critical_unresolved": r.get("critical_unresolved") or [],
    }


def main():
    demo_server.ensure_runtime()
    current = run("CURRENT")
    stale = run("STALE")
    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "SHARED_LINEAGE_SECOND_RECORD_CURRENT_TO_STALE",
        "current": current,
        "stale": stale,
        "transition": f'{current["decision"]}/{current["claim_state"]}->{stale["decision"]}/{stale["claim_state"]}',
        "false_gates_removed_when_stale": sorted(
            set(current["false_gates"]) - set(stale["false_gates"])
        ),
        "false_gates_added_when_stale": sorted(
            set(stale["false_gates"]) - set(current["false_gates"])
        ),
        "interpretation_boundary": (
            "Both records remain present and SHARED_LINEAGE remains fixed. "
            "Only E2 validity changes CURRENT -> STALE. This avoids the E2 OMIT/INCLUDE "
            "fixture coupling that rewrites E1 provenance."
        ),
    }
    Path("shared_lineage_stale_review.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
