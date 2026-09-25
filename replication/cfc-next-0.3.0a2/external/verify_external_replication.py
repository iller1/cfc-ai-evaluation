from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROFILE = HERE / "EXTERNAL_REPLICATION_PROFILE.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd, *, cwd: Path, timeout: int = 360) -> str:
    cp = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\n"
            f"stdout:\n{cp.stdout}\n"
            f"stderr:\n{cp.stderr}"
        )
    return cp.stdout.strip()


def run_json_module(repo: Path, module: str, timeout: int = 360) -> dict:
    output = run(
        [sys.executable, "-m", module],
        cwd=repo,
        timeout=timeout,
    )
    return json.loads(output)


def assert_acceptance(result: dict, expected: dict) -> None:
    assert result["status"] == expected["status"]
    assert result["positive_pass_count"] == expected["positive_pass_count"]
    assert (
        result["negative_fail_closed_count"]
        == expected["negative_fail_closed_count"]
    )
    assert (
        result["unexpected_bound_negative_paths"]
        == expected["unexpected_bound_negative_paths"]
    )


def assert_promotion(result: dict, expected: dict) -> None:
    assert result["status"] == expected["status"]
    assert result["all_gates_pass"] is expected["all_gates_pass"]
    assert (
        result["reproducible_full_acceptance"]
        is expected["reproducible_full_acceptance"]
    )
    assert (
        result["concurrent_process_pass"]
        is expected["concurrent_process_pass"]
    )


def assert_state_isolation(result: dict, expected: dict) -> None:
    assert result["promotion_status"] == expected["promotion_status"]
    assert (
        len(result["relations_tested"])
        == expected["relations_tested_count"]
    )
    assert (
        result["candidate_authorization_visible_to_frozen_relations"]
        == expected[
            "candidate_authorization_visible_to_frozen_relations"
        ]
    )


def assert_freeze_review(result: dict, expected: dict) -> None:
    assert result["status"] == expected["status"]
    assert result["baseline_status"] == expected["baseline_status"]
    assert result["freeze_manifest_verified"] is expected[
        "freeze_manifest_verified"
    ]


def main(repo: Path) -> dict:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    repo = repo.resolve()

    head = run(["git", "rev-parse", "HEAD"], cwd=repo)
    if head != profile["freeze_merge_commit"]:
        raise AssertionError(
            f"wrong frozen checkout: {head} != "
            f"{profile['freeze_merge_commit']}"
        )

    source = repo / profile["candidate_source_path"]
    source_sha = sha256(source)
    if source_sha != profile["candidate_source_sha256"]:
        raise AssertionError(
            f"candidate source hash mismatch: {source_sha}"
        )

    acceptance = run_json_module(
        repo,
        "research.review_cfc_next_0_3_0a2_acceptance",
        timeout=240,
    )
    assert_acceptance(
        acceptance,
        profile["expected"]["acceptance"],
    )

    promotion = run_json_module(
        repo,
        "research.review_cfc_next_0_3_0a2_promotion_readiness",
        timeout=420,
    )
    assert_promotion(
        promotion,
        profile["expected"]["promotion_readiness"],
    )

    state_isolation = run_json_module(
        repo,
        "research.review_cfc_next_0_3_0a2_state_isolation",
        timeout=240,
    )
    assert_state_isolation(
        state_isolation,
        profile["expected"]["state_isolation"],
    )

    freeze_review = run_json_module(
        repo,
        "research.review_cfc_next_0_3_0a2_freeze_review",
        timeout=480,
    )
    assert_freeze_review(
        freeze_review,
        profile["expected"]["freeze_review"],
    )

    result = {
        "test": "CFC_NEXT_0_3_0A2_EXTERNAL_REPLICATION",
        "frozen_ref": profile["frozen_ref"],
        "checked_commit": head,
        "candidate_source_sha256": source_sha,
        "acceptance": {
            "positive_pass_count": acceptance["positive_pass_count"],
            "negative_fail_closed_count": (
                acceptance["negative_fail_closed_count"]
            ),
            "unexpected_bound_negative_paths": (
                acceptance["unexpected_bound_negative_paths"]
            ),
        },
        "promotion_readiness_all_gates_pass": promotion[
            "all_gates_pass"
        ],
        "state_isolation_relations_tested": len(
            state_isolation["relations_tested"]
        ),
        "state_isolation_visible_relations": state_isolation[
            "candidate_authorization_visible_to_frozen_relations"
        ],
        "freeze_manifest_verified": freeze_review[
            "freeze_manifest_verified"
        ],
        "historical_rescore_performed": False,
        "status": "PASS",
    }

    Path("cfc_next_0_3_0a2_external_replication.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        required=True,
        help="Path to a checkout of frozen/cfc-next-0.3.0a2",
    )
    args = parser.parse_args()
    main(Path(args.repo))
