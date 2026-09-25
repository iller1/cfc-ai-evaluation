from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import inspect
import json
import subprocess
import sys
from pathlib import Path

from demonstrator import server as demo_server


def _ensure_frozen():
    demo_server.ensure_runtime()
    if str(demo_server.RUNTIME) not in sys.path:
        sys.path.insert(0, str(demo_server.RUNTIME))


def _sha_source(fn) -> str:
    return hashlib.sha256(
        inspect.getsource(fn).encode("utf-8")
    ).hexdigest()


def _run_acceptance(args: list[str]) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_cfc_next_0_3_0a2_acceptance",
            *args,
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip())
    return json.loads(cp.stdout)


def probe_isolation() -> dict:
    _ensure_frozen()
    import cfc_anchor._engine as engine
    from cfc_anchor import Controller as FrozenController

    frozen_register = engine.register_decision_generic_dependency_accounting
    frozen_hash = _sha_source(frozen_register)
    frozen_install_source = inspect.getsource(
        FrozenController.install_verified_decision_generic_dependency_accounting
    )

    import cfc_next_candidate_0_3_0a2 as candidate

    after_import = engine.register_decision_generic_dependency_accounting
    positive = _run_acceptance(["--single-positive", "root_origin_shared"])
    after_operation = engine.register_decision_generic_dependency_accounting

    return {
        "mode": "isolation",
        "candidate_version": candidate.CANDIDATE_VERSION,
        "register_same_after_import": after_import is frozen_register,
        "register_same_after_candidate_operation": (
            after_operation is frozen_register
        ),
        "frozen_register_source_sha256_before": frozen_hash,
        "frozen_register_source_sha256_after": _sha_source(after_operation),
        "frozen_controller_install_still_uses_engine_global": (
            "_engine.register_decision_generic_dependency_accounting"
            in frozen_install_source
        ),
        "candidate_exposes_import_time_patch_installer": hasattr(
            candidate,
            "install_candidate_engine_patch",
        ),
        "candidate_lineage_validator_accepts_canonical_blank_dimension": (
            candidate.generic_accounting_node_valid(
                ("LINEAGE", "", "root:test")
            )
        ),
        "positive_operation_control_closure": positive["after"][
            "control_closure"
        ],
        "wheel_matches_pinned": (
            demo_server.sha256(demo_server.WHEEL)
            == demo_server.EXPECTED_WHEEL
        ),
    }


def _run_mode(mode: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_cfc_next_0_3_0a2_promotion_readiness",
            "--mode",
            mode,
        ],
        capture_output=True,
        text=True,
        timeout=240,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"{mode}: {cp.stderr.strip() or cp.stdout.strip()}"
        )
    return json.loads(cp.stdout)


def _single_positive(blocker: str) -> dict:
    return _run_acceptance(["--single-positive", blocker])


def main():
    isolation = _run_mode("isolation")

    first = _run_acceptance([])
    second = _run_acceptance([])
    reproducible = first == second

    concurrent_blockers = (
        "root_origin_shared",
        "origin_shared",
        "common_mode_group_shared",
        "dependency:data_source",
    )
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(concurrent_blockers)
    ) as pool:
        futures = {
            blocker: pool.submit(_single_positive, blocker)
            for blocker in concurrent_blockers
        }
        concurrent_rows = {
            blocker: future.result()
            for blocker, future in futures.items()
        }

    concurrent_process_pass = all(
        row["after"]["control_closure"] is True
        and row["after"]["false_gates"] == []
        for row in concurrent_rows.values()
    )

    gates = {
        "no_import_time_engine_mutation": isolation[
            "register_same_after_import"
        ],
        "no_operation_time_engine_mutation": isolation[
            "register_same_after_candidate_operation"
        ],
        "no_patch_installer_surface": not isolation[
            "candidate_exposes_import_time_patch_installer"
        ],
        "repair_a_lineage_domain_preserved": isolation[
            "candidate_lineage_validator_accepts_canonical_blank_dimension"
        ],
        "positive_operation_closes": isolation[
            "positive_operation_control_closure"
        ],
        "frozen_wheel_pinned": isolation["wheel_matches_pinned"],
        "full_acceptance_first_pass": first["status"] == "PASS",
        "full_acceptance_second_pass": second["status"] == "PASS",
        "deterministic_full_acceptance": reproducible,
        "concurrent_fresh_process_positive_pass": concurrent_process_pass,
    }

    result = {
        "test": "CFC_NEXT_0_3_0A2_PROMOTION_READINESS",
        "candidate_version": "0.3.0a2",
        "frozen_reference": "CFC Anchor 0.2.90rc1",
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "isolation": isolation,
        "acceptance_summary": {
            "positive_count": first["positive_count"],
            "positive_pass_count": first["positive_pass_count"],
            "negative_count": first["negative_count"],
            "negative_fail_closed_count": first[
                "negative_fail_closed_count"
            ],
            "unexpected_bound_negative_paths": first[
                "unexpected_bound_negative_paths"
            ],
        },
        "reproducible_full_acceptance": reproducible,
        "concurrent_process_blockers": list(concurrent_blockers),
        "concurrent_process_pass": concurrent_process_pass,
        "same_interpreter_stateful_concurrency_claimed": False,
        "historical_rescore_performed": False,
        "frozen_wheel_modified": False,
        "status": (
            "PASS"
            if all(gates.values())
            else "NOT_PROMOTION_READY"
        ),
    }

    assert result["historical_rescore_performed"] is False
    assert result["frozen_wheel_modified"] is False

    Path("cfc_next_0_3_0a2_promotion_readiness.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("isolation",))
    args = parser.parse_args()

    if args.mode == "isolation":
        print(json.dumps(probe_isolation(), sort_keys=True))
    else:
        main()
