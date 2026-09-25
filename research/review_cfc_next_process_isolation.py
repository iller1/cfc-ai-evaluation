from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import subprocess
import sys
from pathlib import Path

from demonstrator import server as demo_server


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ensure_frozen():
    demo_server.ensure_runtime()
    if str(demo_server.RUNTIME) not in sys.path:
        sys.path.insert(0, str(demo_server.RUNTIME))


def _fn_signature(fn) -> dict:
    try:
        source = inspect.getsource(fn)
    except Exception:
        source = repr(fn)
    return {
        "module": getattr(fn, "__module__", None),
        "qualname": getattr(fn, "__qualname__", None),
        "source_sha256": _sha_text(source),
    }


def probe_baseline() -> dict:
    _ensure_frozen()
    import cfc_anchor._engine as engine

    fn = engine.register_decision_generic_dependency_accounting
    return {
        "mode": "baseline",
        "register": _fn_signature(fn),
        "candidate_module_loaded": "cfc_next_candidate" in sys.modules,
        "wheel_sha256": demo_server.sha256(demo_server.WHEEL),
        "wheel_matches_pinned": (
            demo_server.sha256(demo_server.WHEEL)
            == demo_server.EXPECTED_WHEEL
        ),
    }


def probe_import_mutation() -> dict:
    _ensure_frozen()
    import cfc_anchor._engine as engine

    before = engine.register_decision_generic_dependency_accounting
    before_sig = _fn_signature(before)

    import cfc_next_candidate as candidate

    after = engine.register_decision_generic_dependency_accounting
    return {
        "mode": "import_mutation",
        "before": before_sig,
        "after": _fn_signature(after),
        "same_function_object": before is after,
        "after_is_candidate_register": (
            after
            is candidate._candidate_register_decision_generic_dependency_accounting
        ),
        "candidate_patch_flag": candidate._PATCH_INSTALLED,
        "frozen_register_saved_is_before": candidate._FROZEN_REGISTER is before,
        "wheel_sha256": demo_server.sha256(demo_server.WHEEL),
        "wheel_matches_pinned": (
            demo_server.sha256(demo_server.WHEEL)
            == demo_server.EXPECTED_WHEEL
        ),
    }


def probe_frozen_controller_contamination() -> dict:
    _ensure_frozen()
    import cfc_anchor._engine as engine
    from cfc_anchor import Controller as FrozenController

    method_source = inspect.getsource(
        FrozenController.install_verified_decision_generic_dependency_accounting
    )
    before = engine.register_decision_generic_dependency_accounting

    import cfc_next_candidate as candidate

    after = engine.register_decision_generic_dependency_accounting
    return {
        "mode": "frozen_controller_contamination",
        "frozen_controller_loaded_before_candidate": True,
        "controller_install_uses_engine_global_register": (
            "_engine.register_decision_generic_dependency_accounting"
            in method_source
        ),
        "engine_register_changed_after_candidate_import": before is not after,
        "engine_register_is_candidate_after_import": (
            after
            is candidate._candidate_register_decision_generic_dependency_accounting
        ),
        "candidate_frozen_controller_alias_is_same_class": (
            candidate.FrozenController is FrozenController
        ),
        "same_process_frozen_controller_can_observe_candidate_register": (
            "_engine.register_decision_generic_dependency_accounting"
            in method_source
            and after
            is candidate._candidate_register_decision_generic_dependency_accounting
        ),
    }


def probe_restore_reentry() -> dict:
    _ensure_frozen()
    import cfc_anchor._engine as engine
    import cfc_next_candidate as candidate

    assert (
        engine.register_decision_generic_dependency_accounting
        is candidate._candidate_register_decision_generic_dependency_accounting
    )

    engine.register_decision_generic_dependency_accounting = (
        candidate._FROZEN_REGISTER
    )
    candidate.install_candidate_engine_patch()

    return {
        "mode": "restore_reentry",
        "candidate_patch_flag_after_manual_restore": candidate._PATCH_INSTALLED,
        "register_is_frozen_after_reinstall_call": (
            engine.register_decision_generic_dependency_accounting
            is candidate._FROZEN_REGISTER
        ),
        "register_is_candidate_after_reinstall_call": (
            engine.register_decision_generic_dependency_accounting
            is candidate._candidate_register_decision_generic_dependency_accounting
        ),
        "patch_flag_matches_actual_patch": (
            candidate._PATCH_INSTALLED
            and engine.register_decision_generic_dependency_accounting
            is candidate._candidate_register_decision_generic_dependency_accounting
        ),
    }


def _run_mode(mode: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_cfc_next_process_isolation",
            "--mode",
            mode,
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"{mode}: {cp.stderr.strip() or cp.stdout.strip()}"
        )
    return json.loads(cp.stdout)


def main():
    baseline_before = _run_mode("baseline")
    mutation = _run_mode("import_mutation")
    contamination = _run_mode("frozen_controller_contamination")
    restore_reentry = _run_mode("restore_reentry")
    baseline_after = _run_mode("baseline")

    subprocess_isolation_control = (
        baseline_before["register"]["source_sha256"]
        == baseline_after["register"]["source_sha256"]
        and baseline_before["candidate_module_loaded"] is False
        and baseline_after["candidate_module_loaded"] is False
        and baseline_before["wheel_matches_pinned"] is True
        and baseline_after["wheel_matches_pinned"] is True
    )

    blockers = []
    if mutation["same_function_object"] is False:
        blockers.append("IMPORT_TIME_GLOBAL_ENGINE_MUTATION")
    if contamination[
        "same_process_frozen_controller_can_observe_candidate_register"
    ]:
        blockers.append("FROZEN_CONTROLLER_SAME_PROCESS_CONTAMINATION")
    if restore_reentry["patch_flag_matches_actual_patch"] is False:
        blockers.append("PATCH_LIFECYCLE_STATE_DIVERGENCE")

    result = {
        "test": "CFC_NEXT_0_3_0A1_PROCESS_ISOLATION_READINESS",
        "candidate_version": "0.3.0a1",
        "frozen_reference": "CFC Anchor 0.2.90rc1",
        "candidate_status_before_review": "ACCEPTED_EXPERIMENTAL_CANDIDATE",
        "promotion_status": (
            "NOT_PROMOTION_READY_PROCESS_ISOLATION_BLOCKER"
            if blockers
            else "PROCESS_ISOLATION_GATE_PASS"
        ),
        "blockers": blockers,
        "subprocess_isolation_control_passed": subprocess_isolation_control,
        "baseline_before": baseline_before,
        "import_mutation": mutation,
        "frozen_controller_contamination": contamination,
        "restore_reentry": restore_reentry,
        "baseline_after": baseline_after,
        "frozen_wheel_modified": False,
        "historical_rescore_performed": False,
    }

    assert subprocess_isolation_control
    assert result["frozen_wheel_modified"] is False
    assert result["historical_rescore_performed"] is False

    Path("cfc_next_0_3_0a1_process_isolation_readiness.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=(
            "baseline",
            "import_mutation",
            "frozen_controller_contamination",
            "restore_reentry",
        ),
    )
    args = parser.parse_args()

    if args.mode == "baseline":
        print(json.dumps(probe_baseline(), sort_keys=True))
    elif args.mode == "import_mutation":
        print(json.dumps(probe_import_mutation(), sort_keys=True))
    elif args.mode == "frozen_controller_contamination":
        print(json.dumps(probe_frozen_controller_contamination(), sort_keys=True))
    elif args.mode == "restore_reentry":
        print(json.dumps(probe_restore_reentry(), sort_keys=True))
    else:
        main()
