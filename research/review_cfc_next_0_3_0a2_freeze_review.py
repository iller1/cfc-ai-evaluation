from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from demonstrator import server as demo_server


ROOT = Path(__file__).resolve().parents[1]
FREEZE_MANIFEST = (
    ROOT / "research" / "cfc_next_0_3_0a2_freeze_manifest.json"
)

FILES = {
    "candidate_source_sha256": (
        ROOT / "cfc_next_candidate_0_3_0a2" / "__init__.py"
    ),
    "acceptance_harness_sha256": (
        ROOT / "research" / "review_cfc_next_0_3_0a2_acceptance.py"
    ),
    "promotion_readiness_harness_sha256": (
        ROOT
        / "research"
        / "review_cfc_next_0_3_0a2_promotion_readiness.py"
    ),
    "state_isolation_harness_sha256": (
        ROOT
        / "research"
        / "review_cfc_next_0_3_0a2_state_isolation.py"
    ),
    "acceptance_manifest_sha256": (
        ROOT / "research" / "cfc_next_accounting_acceptance_manifest.json"
    ),
    "repair_spec_sha256": (
        ROOT
        / "research"
        / "cfc_next_decision_accounting_repair_spec.json"
    ),
    "a1_closure_manifest_sha256": (
        ROOT
        / "research"
        / "cfc_next_0_3_0a1_candidate_closure_manifest.json"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_json_module(module: str, timeout: int) -> dict:
    cp = subprocess.run(
        [sys.executable, "-m", module],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"{module}: {cp.stderr.strip() or cp.stdout.strip()}"
        )
    return json.loads(cp.stdout)


def main():
    demo_server.ensure_runtime()

    promotion = run_json_module(
        "research.review_cfc_next_0_3_0a2_promotion_readiness",
        300,
    )
    state_isolation = run_json_module(
        "research.review_cfc_next_0_3_0a2_state_isolation",
        180,
    )

    expected_acceptance = {
        "positive_count": 14,
        "positive_pass_count": 14,
        "negative_count": 12,
        "negative_fail_closed_count": 12,
        "unexpected_bound_negative_paths": [],
    }

    assert promotion["status"] == "PASS"
    assert promotion["candidate_version"] == "0.3.0a2"
    assert promotion["all_gates_pass"] is True
    assert promotion["acceptance_summary"] == expected_acceptance
    assert promotion["reproducible_full_acceptance"] is True
    assert promotion["concurrent_process_pass"] is True
    assert promotion["historical_rescore_performed"] is False
    assert promotion["frozen_wheel_modified"] is False

    assert state_isolation["candidate_version"] == "0.3.0a2"
    assert len(state_isolation["relations_tested"]) == 14
    assert (
        state_isolation[
            "candidate_authorization_visible_to_frozen_relations"
        ]
        == []
    )
    assert (
        state_isolation["promotion_status"]
        == "STATE_ISOLATION_GATE_PASS"
    )
    assert state_isolation["historical_rescore_performed"] is False
    assert state_isolation["frozen_wheel_modified"] is False

    wheel_sha = demo_server.sha256(demo_server.WHEEL)
    assert wheel_sha == demo_server.EXPECTED_WHEEL

    commitments = {
        name: sha256(path)
        for name, path in FILES.items()
    }
    commitments["frozen_reference_wheel_sha256"] = wheel_sha

    pinned = json.loads(FREEZE_MANIFEST.read_text(encoding="utf-8"))
    assert pinned["schema_version"] == "1"
    assert pinned["baseline"] == "CFC-next 0.3.0a2"
    assert pinned["freeze_intent"] == "FROZEN_ON_MERGE"
    assert pinned["candidate_merge_commit"] == (
        "09d4d16f2159a7d600527fff8ab0e01e21aa2efb"
    )
    assert pinned["state_isolation_merge_commit"] == (
        "77642de212a98ba5be2b9fda5111fcdc5d8fd516"
    )
    assert pinned["frozen_reference"] == "CFC Anchor 0.2.90rc1"
    assert pinned["previous_candidate"] == "CFC-next 0.3.0a1"
    assert pinned["commitments"] == commitments
    assert pinned["acceptance"] == expected_acceptance
    assert pinned["promotion_readiness_all_gates_pass"] is True
    assert pinned["state_isolation"] == {
        "relations_tested": 14,
        "candidate_authorization_visible_to_frozen_relations": [],
        "gate": "STATE_ISOLATION_GATE_PASS",
    }
    assert pinned["historical_rescore_performed"] is False
    assert pinned["frozen_reference_modified"] is False

    result = {
        "test": "CFC_NEXT_0_3_0A2_FREEZE_REVIEW",
        "baseline": "CFC-next 0.3.0a2",
        "baseline_status": "PINNED_FREEZE_MANIFEST_VERIFIED",
        "freeze_intent": "FROZEN_ON_MERGE",
        "candidate_merge_commit": pinned["candidate_merge_commit"],
        "state_isolation_merge_commit": (
            pinned["state_isolation_merge_commit"]
        ),
        "frozen_reference": pinned["frozen_reference"],
        "previous_candidate": pinned["previous_candidate"],
        "commitments": commitments,
        "freeze_manifest_verified": True,
        "acceptance": expected_acceptance,
        "promotion_readiness_all_gates_pass": True,
        "state_isolation_relations_tested": 14,
        "state_isolation_visible_relations": [],
        "state_isolation_gate_pass": True,
        "historical_rescore_performed": False,
        "frozen_reference_modified": False,
        "status": "PASS",
    }

    Path("cfc_next_0_3_0a2_freeze_review.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
