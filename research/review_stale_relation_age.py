from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from research import review_stale_relation_polarity as base

RELATION_MODES = base.RELATION_MODES
ASOF_WINDOWS = {
    "D3": "2026-09-03",
    "D31": "2026-10-01",
    "D92": "2026-12-01",
}


def build_case(relation_mode: str, window: str) -> dict:
    as_of = ASOF_WINDOWS[window]
    base.ASOF = as_of
    row = base.build_case(relation_mode, "POSITIVE")
    row["window"] = window
    row["as_of"] = as_of
    row["stale_valid_to"] = base.STALE_TO
    row["stale_age_days"] = (
        date.fromisoformat(as_of) - date.fromisoformat(base.STALE_TO)
    ).days
    return row


def run_isolated(relation_mode: str, window: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_stale_relation_age",
            "--single-relation",
            relation_mode,
            "--single-window",
            window,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip())
    return json.loads(cp.stdout)


def main() -> dict:
    rows = [
        run_isolated(relation, window)
        for relation in RELATION_MODES
        for window in ASOF_WINDOWS
    ]

    comparisons = {}
    for relation in RELATION_MODES:
        rel_rows = [r for r in rows if r["relation_mode"] == relation]
        signatures = [
            {
                "claim_state": r["claim_state"],
                "control_closure": r["control_closure"],
                "false_gates": r["false_gates"],
                "global_consistency_violations": r[
                    "global_consistency_violations"
                ],
            }
            for r in rel_rows
        ]
        comparisons[relation] = {
            "rows": [
                {
                    "window": r["window"],
                    "as_of": r["as_of"],
                    "stale_age_days": r["stale_age_days"],
                    "claim_state": r["claim_state"],
                    "control_closure": r["control_closure"],
                    "false_gates": r["false_gates"],
                    "global_consistency_violations": r[
                        "global_consistency_violations"
                    ],
                }
                for r in rel_rows
            ],
            "same_authorization_signature": all(
                sig == signatures[0] for sig in signatures[1:]
            ),
        }

    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "STALE_RELATION_AGE",
        "state_count": len(rows),
        "relations": list(RELATION_MODES),
        "windows": ASOF_WINDOWS,
        "comparisons": comparisons,
        "rows": rows,
        "interpretation_boundary": (
            "E1 is POSITIVE/CURRENT and alone satisfies required supports = 1. "
            "E2 is POSITIVE/STALE with fixed valid_to=2026-08-31 and fixed "
            "historical record content. One shared relation is present per case. "
            "The evaluation/snapshot time is shifted while the current context is "
            "co-shifted consistently, testing whether stale-relation authorization "
            "persistence changes as the same stale record ages."
        ),
    }
    Path("stale_relation_age.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-relation", choices=RELATION_MODES)
    parser.add_argument("--single-window", choices=tuple(ASOF_WINDOWS))
    args = parser.parse_args()
    if args.single_relation:
        print(json.dumps(
            build_case(args.single_relation, args.single_window),
            sort_keys=True,
        ))
    else:
        main()
