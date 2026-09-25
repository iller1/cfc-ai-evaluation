from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from demonstrator import server as demo_server


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "cfc_next_candidate" / "__init__.py"
ACCEPTANCE = ROOT / "research" / "review_cfc_next_candidate_acceptance.py"
MANIFEST = ROOT / "research" / "cfc_next_accounting_acceptance_manifest.json"
REPAIR_SPEC = ROOT / "research" / "cfc_next_decision_accounting_repair_spec.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    demo_server.ensure_runtime()

    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_cfc_next_candidate_acceptance",
        ],
        capture_output=True,
        text=True,
        timeout=240,
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip())
    acceptance = json.loads(cp.stdout)

    assert acceptance["status"] == "PASS"
    assert acceptance["candidate_version"] == "0.3.0a1"
    assert acceptance["frozen_reference"] == "CFC Anchor 0.2.90rc1"
    assert acceptance["positive_count"] == 14
    assert acceptance["positive_pass_count"] == 14
    assert acceptance["negative_count"] == 12
    assert acceptance["negative_fail_closed_count"] == 12
    assert acceptance["unexpected_bound_negative_paths"] == []
    assert acceptance["frozen_reference_modified"] is False
    assert acceptance["historical_rescore_performed"] is False

    wheel_sha = demo_server.sha256(demo_server.WHEEL)
    assert wheel_sha == demo_server.EXPECTED_WHEEL

    result = {
        "test": "CFC_NEXT_0_3_0A1_CANDIDATE_CLOSURE",
        "candidate_version": "0.3.0a1",
        "candidate_status": "ACCEPTED_EXPERIMENTAL_CANDIDATE",
        "promotion_status": "NOT_FROZEN_NOT_RELEASE_BASELINE",
        "frozen_reference": "CFC Anchor 0.2.90rc1",
        "frozen_reference_wheel_sha256": wheel_sha,
        "frozen_reference_unchanged": True,
        "historical_rescore_performed": False,
        "candidate_source_sha256": sha256(CANDIDATE),
        "candidate_acceptance_harness_sha256": sha256(ACCEPTANCE),
        "acceptance_manifest_sha256": sha256(MANIFEST),
        "repair_spec_sha256": sha256(REPAIR_SPEC),
        "positive_count": acceptance["positive_count"],
        "positive_pass_count": acceptance["positive_pass_count"],
        "negative_count": acceptance["negative_count"],
        "negative_fail_closed_count": acceptance["negative_fail_closed_count"],
        "unexpected_bound_negative_paths": acceptance[
            "unexpected_bound_negative_paths"
        ],
        "status": "PASS",
    }

    Path("cfc_next_0_3_0a1_candidate_closure.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
