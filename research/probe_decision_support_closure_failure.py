from __future__ import annotations

import argparse
import contextlib
import json
import subprocess
import sys
from pathlib import Path

from demonstrator import server as demo_server

demo_server.ensure_runtime()
sys.path.insert(0, str(demo_server.RUNTIME))

from cfc_anchor import Controller
import cfc_anchor._engine as frozen_engine

from demonstrator.custom_case_runner import ASOF
from research.review_stale_relation_snapshot_locality import (
    RELATION_MODES,
    _trust_policy,
    _install_identity,
    _install_topology,
    _build_record,
    _install_snapshot,
)


WATCH = (
    "_decision_support_dependency_graph",
    "_decision_level_relation_coverage",
    "make_decision_level_generic_dependency_universe",
    "_decision_level_generic_dependency_assessments",
    "_find_bound_decision_generic_dependency_accounting",
    "make_decision_level_source_relation_universe",
    "_decision_level_source_relation_assessments",
    "_find_bound_decision_dependency_accounting",
    "make_decision_support_closure_certificate",
)


def _safe(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, tuple):
        return [_safe(x) for x in value]
    if isinstance(value, list):
        return [_safe(x) for x in value]
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k in {
                "selected_support_map",
                "matching_support_universe_map",
                "path_relevant_source_edges",
                "node_ownership",
                "justificatory_bridges",
                "source_relation_rows",
                "decision_obligation_nodes",
                "decision_obligation_pair_ids",
                "generic_dependency_records",
                "source_relation_records",
                "candidate_disposition_records",
                "equivalence_resolution_records",
                "generic_dependency_node",
                "evidence_ids",
                "decision_level_required",
                "relevance_classification",
                "selected_support_path_relevant",
                "selected_support_path_anchor_ids",
                "endpoint_classifications",
                "endpoint_claim_ownership",
            }:
                out[str(k)] = _safe(v)
        if out:
            return out
        return {"keys": sorted(str(k) for k in value.keys())}
    if hasattr(value, "__dict__"):
        d = vars(value)
        keep = {}
        for key in (
            "certificate_id",
            "universe_id",
            "universe_hash",
            "decision_obligation_nodes",
            "decision_obligation_pair_ids",
            "generic_dependency_records",
            "source_relation_records",
            "candidate_disposition_records",
        ):
            if key in d:
                keep[key] = _safe(d[key])
        return {
            "type": type(value).__name__,
            "fields": keep,
        }
    return {"type": type(value).__name__, "repr": repr(value)[:1200]}


@contextlib.contextmanager
def trace_calls(trace):
    originals = {}
    for name in WATCH:
        if not hasattr(frozen_engine, name):
            continue
        original = getattr(frozen_engine, name)
        originals[name] = original

        def make_wrapper(func_name, func):
            def wrapper(*args, **kwargs):
                try:
                    out = func(*args, **kwargs)
                except Exception as exc:
                    trace.append({
                        "function": func_name,
                        "exception": f"{type(exc).__name__}: {exc}",
                    })
                    raise
                trace.append({
                    "function": func_name,
                    "result_is_none": out is None,
                    "result": _safe(out),
                })
                return out
            return wrapper

        setattr(frozen_engine, name, make_wrapper(name, original))
    try:
        yield
    finally:
        for name, original in originals.items():
            setattr(frozen_engine, name, original)


def build_case(relation_mode: str) -> dict:
    tag = f"closure-failure:{relation_mode.lower()}"
    c = Controller(trust_policy=_trust_policy())
    identity_id = _install_identity(c, tag)
    _install_topology(c, tag)

    e1 = _build_record(
        c,
        tag=tag,
        identity_id=identity_id,
        relation_mode=relation_mode,
        idx=1,
        validity="CURRENT",
    )
    e2 = _build_record(
        c,
        tag=tag,
        identity_id=identity_id,
        relation_mode=relation_mode,
        idx=2,
        validity="STALE",
    )
    records = [e1, e2]
    snapshot = _install_snapshot(
        c,
        tag=tag,
        label="evaluated",
        records=records,
    )

    trace = []
    with trace_calls(trace):
        result = c.evaluate_snapshot(
            snapshot,
            "DemoSubject is safe.",
            records,
            {"c1": identity_id},
            as_of=ASOF,
            requirements={"c1": {"required_independent_supports": 1}},
        )

    claim = result.claims[0] if result.claims else {}
    return {
        "relation_mode": relation_mode,
        "claim_state": claim.get("status"),
        "control_closure": bool(result.control_closure),
        "false_gates": sorted(k for k, v in result.gates.items() if not v),
        "decision_support_closure_valid": bool(
            result.gates.get("decision_support_closure_valid")
        ),
        "decision_support_closure_certificate_present": (
            result.raw.get("decision_support_closure_certificate") is not None
        ),
        "decision_support_dependency_graph": result.raw.get(
            "decision_support_dependency_graph"
        ),
        "trace": trace,
    }


def run_isolated(relation_mode: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.probe_decision_support_closure_failure",
            "--single-relation",
            relation_mode,
        ],
        capture_output=True,
        text=True,
        timeout=40,
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip())
    return json.loads(cp.stdout)


def main():
    rows = [run_isolated(mode) for mode in RELATION_MODES]
    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "DECISION_SUPPORT_CLOSURE_FAILURE_PROBE",
        "state_count": len(rows),
        "relations": list(RELATION_MODES),
        "rows": rows,
        "non_mutation": (
            "Runtime wrappers only observe return values and restore all frozen-engine "
            "callables after each evaluation. No controller source or policy is changed."
        ),
    }
    Path("decision_support_closure_failure_probe.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-relation", choices=RELATION_MODES)
    args = parser.parse_args()
    if args.single_relation:
        print(json.dumps(build_case(args.single_relation), sort_keys=True))
    else:
        main()
