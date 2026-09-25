from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, replace
from pathlib import Path

from demonstrator import server as demo_server
from research.structured_input_state_space import (
    StructuredState,
    admissible_states,
    semantic_mutation_edges,
)


def state_key(state: StructuredState) -> str:
    return json.dumps(asdict(state), sort_keys=True, separators=(",", ":"))


def execute_state(state: StructuredState) -> dict:
    payload = demo_server.run_custom(state.as_cfc_structured())
    p = payload["presentation"]
    result = payload["result"]
    return {
        "decision": p.get("decision"),
        "claim_state": p.get("claim_state"),
        "reason": p.get("reason"),
        "false_gates": p.get("false_gates") or [],
        "control_closure": bool(result.get("control_closure")),
        "engine_sha256": result.get("engine_sha256"),
    }

def invert_polarity(value: str | None) -> str | None:
    if value == "POSITIVE":
        return "NEGATIVE"
    if value == "NEGATIVE":
        return "POSITIVE"
    return value


def polarity_inversion(state: StructuredState) -> StructuredState:
    return replace(
        state,
        conclusion=invert_polarity(state.conclusion),
        e1_polarity=invert_polarity(state.e1_polarity),
        e2_polarity=invert_polarity(state.e2_polarity),
    )


def evidence_swap(state: StructuredState) -> StructuredState | None:
    if state.e2_mode != "INCLUDE":
        return None
    return replace(
        state,
        e1_polarity=state.e2_polarity,
        e1_validity=state.e2_validity,
        e2_polarity=state.e1_polarity,
        e2_validity=state.e1_validity,
    )


def directed_pair(a: StructuredState, b: StructuredState, family: str):
    if family == "SUPPORT_THRESHOLD":
        return (a, b) if a.required_independent_supports == 1 else (b, a)
    if family == "SCOPE":
        return (a, b) if a.scope == "EXPECTED" else (b, a)
    if family == "PROVENANCE_DEPENDENCY":
        return (a, b) if a.provenance_shape == "DISTINCT" else (b, a)
    if family == "INDEPENDENCE_AUTHORITY":
        return (a, b) if a.independence_authority == "NONE" else (b, a)
    if family == "FRESHNESS":
        return (a, b) if a.e1_validity == "CURRENT" else (b, a)
    if family == "SECOND_EVIDENCE_FRESHNESS":
        return (a, b) if a.e2_validity == "CURRENT" else (b, a)
    if family == "SUPPORT_COMPLETENESS":
        return (a, b) if a.e2_mode == "OMIT" else (b, a)
    if family == "EVIDENCE_POLARITY":
        a_supports = a.e1_polarity == a.conclusion
        return (b, a) if a_supports else (a, b)
    if family == "SECOND_EVIDENCE_POLARITY":
        a_supports = a.e2_polarity == a.conclusion
        return (b, a) if a_supports else (a, b)
    return a, b


def transition_name(before: dict, after: dict) -> str:
    return f'{before["decision"]}/{before["claim_state"]}->{after["decision"]}/{after["claim_state"]}'


def closure_delta(before: dict, after: dict) -> str:
    x = int(before["control_closure"])
    y = int(after["control_closure"])
    if y > x:
        return "INCREASE"
    if y < x:
        return "DECREASE"
    return "SAME"


def main() -> dict:
    states = admissible_states()
    demo_server.ensure_runtime()
    outcomes = {}
    completed = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(execute_state, state): state for state in states}
        for future in as_completed(futures):
            state = futures[future]
            outcomes[state_key(state)] = future.result()
            completed += 1
            if completed % 50 == 0:
                print(f"EXECUTED_STATES={completed}", flush=True)

    family_summary = {}
    edge_records = []
    for a, b, family in semantic_mutation_edges(states):
        before_state, after_state = directed_pair(a, b, family)
        before = outcomes[state_key(before_state)]
        after = outcomes[state_key(after_state)]
        record = {
            "family": family,
            "before_state": asdict(before_state),
            "after_state": asdict(after_state),
            "before": before,
            "after": after,
            "closure_delta": closure_delta(before, after),
            "transition": transition_name(before, after),
        }
        edge_records.append(record)
        bucket = family_summary.setdefault(
            family,
            {"total": 0, "closure_increase": 0, "closure_decrease": 0, "closure_same": 0, "transitions": {}},
        )
        bucket["total"] += 1
        bucket["closure_" + record["closure_delta"].lower()] += 1
        bucket["transitions"][record["transition"]] = (
            bucket["transitions"].get(record["transition"], 0) + 1
        )

    inversion_checked = set()
    inversion_mismatches = []
    inversion_total = 0
    for state in states:
        other = polarity_inversion(state)
        if not other.admissible:
            continue
        pair_id = tuple(sorted((state_key(state), state_key(other))))
        if pair_id in inversion_checked:
            continue
        inversion_checked.add(pair_id)
        inversion_total += 1
        a = outcomes[state_key(state)]
        b = outcomes[state_key(other)]
        if (a["decision"], a["claim_state"], a["control_closure"]) != (
            b["decision"], b["claim_state"], b["control_closure"]
        ):
            inversion_mismatches.append(
                {
                    "a_state": asdict(state),
                    "b_state": asdict(other),
                    "a": a,
                    "b": b,
                }
            )

    swap_checked = set()
    swap_mismatches = []
    swap_total = 0
    for state in states:
        other = evidence_swap(state)
        if other is None:
            continue
        pair_id = tuple(sorted((state_key(state), state_key(other))))
        if pair_id in swap_checked:
            continue
        swap_checked.add(pair_id)
        swap_total += 1
        a = outcomes[state_key(state)]
        b = outcomes[state_key(other)]
        if (a["decision"], a["claim_state"], a["control_closure"]) != (
            b["decision"], b["claim_state"], b["control_closure"]
        ):
            swap_mismatches.append(
                {
                    "a_state": asdict(state),
                    "b_state": asdict(other),
                    "a": a,
                    "b": b,
                }
            )

    outcome_counts = {}
    for outcome in outcomes.values():
        key = f'{outcome["decision"]}/{outcome["claim_state"]}'
        outcome_counts[key] = outcome_counts.get(key, 0) + 1

    result = {
        "controller_anchor": "0.2.90rc1",
        "states_executed": len(states),
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "semantic_edges_checked": len(edge_records),
        "families": family_summary,
        "polarity_inversion": {
            "pairs_checked": inversion_total,
            "mismatches": len(inversion_mismatches),
            "examples": inversion_mismatches[:10],
        },
        "evidence_order_invariance": {
            "pairs_checked": swap_total,
            "mismatches": len(swap_mismatches),
            "examples": swap_mismatches[:10],
        },
        "edge_records": edge_records,
    }

    output = Path("structured_state_space_results.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    printable = dict(result)
    printable.pop("edge_records")
    print("STRUCTURED_STATE_SPACE_SUMMARY")
    print(json.dumps(printable, indent=2, sort_keys=True))
    print(f"FULL_RESULTS={output}")
    return result


if __name__ == "__main__":
    main()
