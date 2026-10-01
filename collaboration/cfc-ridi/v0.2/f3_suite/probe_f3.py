from __future__ import annotations

import argparse
import json
from typing import Any

from fixtures import build_resolved_state, execute, make_neutral_arm


def summarize(out: dict[str, Any]) -> dict[str, Any]:
    raw = out.get("raw") if isinstance(out.get("raw"), dict) else {}
    return {
        "control_closure": out.get("control_closure"),
        "stop_type": str(out.get("stop_type")),
        "claim_states": out.get("claim_states"),
        "gates": out.get("gates"),
        "diagnostics": {
            key: raw.get(key)
            for key in (
                "evidence_errors",
                "identity_errors",
                "integration_errors",
                "critical_unresolved",
                "claim_support_policy_violations",
                "constraint_relation_coverage_violations",
                "constraint_coverage_violations",
            )
        },
    }


def scenario(test_id: str, mode: str) -> dict[str, Any]:
    if test_id == "F3-T05":
        arm_a = make_neutral_arm(
            case_id="F3-T05-A", arm="A", passage_namespace="t05-shared"
        )
        arm_b = make_neutral_arm(
            case_id="F3-T05-B", arm="B", passage_namespace="t05-shared"
        )
        state = build_resolved_state(
            arm_b,
            tag="t05-probe",
            required_independent_supports=1,
            install_independence=True,
        )
        return execute(arm_b if mode == "control" else arm_a, state)

    payload = make_neutral_arm(case_id=test_id)

    if test_id == "F3-T06":
        state = build_resolved_state(
            payload,
            tag="t06-probe",
            required_independent_supports=1,
            install_independence=True,
        )
        if mode == "mutation":
            state["claim_identity_map"] = {"c1": "id:foreign-subject:v9"}
        return execute(payload, state)

    if test_id == "F3-T07":
        state = build_resolved_state(
            payload,
            tag="t07-probe",
            required_independent_supports=1,
            install_independence=True,
            controller_scope=None,
            snapshot_scope="scope:f3:narrow",
        )
        if mode == "mutation":
            state["controller_scope"] = "scope:f3:requested-broad"
        return execute(payload, state)

    if test_id == "F3-T08":
        state = build_resolved_state(
            payload,
            tag="t08-probe",
            required_independent_supports=1,
            install_independence=True,
        )
        if mode == "mutation":
            state["decision_as_of"] = "2027-01-15"
        return execute(payload, state)

    if test_id == "F3-T10":
        state = build_resolved_state(
            payload,
            tag="t10-probe",
            shared_lineage=(mode == "mutation"),
            required_independent_supports=2,
            install_independence=(mode == "control"),
        )
        return execute(payload, state)

    if test_id == "F3-T11":
        state = build_resolved_state(
            payload,
            tag="t11-probe",
            shared_lineage=False,
            required_independent_supports=2,
            install_independence=True,
        )
        if mode == "mutation":
            state["requirements"] = {"c1": {"required_independent_supports": 11}}
        return execute(payload, state)

    if test_id == "F3-T12":
        state = build_resolved_state(
            payload,
            tag="t12-probe",
            required_independent_supports=1,
            install_independence=True,
        )
        if mode == "mutation":
            for row in state["host_trust_registrations"]:
                if row["authority_class"] == "IDENTITY":
                    row["authority_id"] = "F3_WRONG_IDENTITY_AUTHORITY"
                    break
        return execute(payload, state)

    raise ValueError(f"unsupported probe test: {test_id}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "test_id",
        choices=["F3-T05", "F3-T06", "F3-T07", "F3-T08", "F3-T10", "F3-T11", "F3-T12"],
    )
    ap.add_argument("mode", choices=["control", "mutation"])
    args = ap.parse_args()

    try:
        out = scenario(args.test_id, args.mode)
        result = {
            "mode": args.mode,
            "execution": "RESULT",
            "summary": summarize(out),
        }
    except Exception as exc:
        result = {
            "mode": args.mode,
            "execution": "EXPLICIT_REJECTION",
            "exception_type": type(exc).__name__,
            "message": str(exc),
        }

    print(json.dumps(result, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
