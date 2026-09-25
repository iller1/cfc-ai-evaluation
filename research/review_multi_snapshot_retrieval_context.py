from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from demonstrator import server as demo_server

demo_server.ensure_runtime()
sys.path.insert(0, str(demo_server.RUNTIME))

from cfc_anchor import Controller, RetrievalAuthorityAttestation
from demonstrator.custom_case_runner import (
    ASOF,
    VALID_FROM,
    VALID_TO,
    AUTHORITIES,
    VERIFIERS,
)
from research.review_stale_relation_snapshot_locality import (
    _trust_policy,
    _install_identity,
    _install_topology,
    _build_record,
)

MODES = (
    "VERIFIED_ONLY",
    "DIFF_SCOPE_AUX_FIRST",
    "DIFF_SCOPE_EVAL_FIRST",
    "SAME_SCOPE_AUX_FIRST",
    "SAME_SCOPE_EVAL_FIRST",
)


def _install_snapshot(
    c: Controller,
    *,
    tag: str,
    label: str,
    scope_id: str,
    records: list[dict],
):
    snapshot = c.draft_snapshot(
        records,
        scope_id=scope_id,
        snapshot_id=f"snapshot:multi-snapshot:{tag}:{label}",
        snapshot_created_at=ASOF,
        snapshot_available_at=ASOF,
        valid_from=VALID_FROM,
        valid_to=VALID_TO,
    )
    c.install_verified_snapshot(
        snapshot,
        records,
        RetrievalAuthorityAttestation(
            f"att:multi-snapshot:{tag}:{label}:retrieval",
            AUTHORITIES["RETRIEVAL"],
            c.snapshot_commitment(snapshot),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["RETRIEVAL"],
        as_of=ASOF,
    )
    return snapshot


def build_case(mode: str) -> dict:
    tag = mode.lower()
    c = Controller(trust_policy=_trust_policy())
    identity_id = _install_identity(c, f"multi:{tag}")
    _install_topology(c, f"multi:{tag}")

    e1 = _build_record(
        c,
        tag=f"multi:{tag}",
        identity_id=identity_id,
        relation_mode="DISTINCT",
        idx=1,
        validity="CURRENT",
    )
    e2 = _build_record(
        c,
        tag=f"multi:{tag}",
        identity_id=identity_id,
        relation_mode="DISTINCT",
        idx=2,
        validity="STALE",
    )

    eval_scope = f"scope:multi-snapshot:{tag}:eval"
    aux_scope = (
        eval_scope
        if mode.startswith("SAME_SCOPE")
        else f"scope:multi-snapshot:{tag}:aux"
    )

    if mode == "VERIFIED_ONLY":
        eval_snapshot = _install_snapshot(
            c, tag=tag, label="eval", scope_id=eval_scope, records=[e1]
        )
    elif mode.endswith("AUX_FIRST"):
        _install_snapshot(
            c, tag=tag, label="aux", scope_id=aux_scope, records=[e2]
        )
        eval_snapshot = _install_snapshot(
            c, tag=tag, label="eval", scope_id=eval_scope, records=[e1]
        )
    elif mode.endswith("EVAL_FIRST"):
        eval_snapshot = _install_snapshot(
            c, tag=tag, label="eval", scope_id=eval_scope, records=[e1]
        )
        _install_snapshot(
            c, tag=tag, label="aux", scope_id=aux_scope, records=[e2]
        )
    else:
        raise ValueError(mode)

    result = c.evaluate_snapshot(
        eval_snapshot,
        "DemoSubject is safe.",
        [e1],
        {"c1": identity_id},
        as_of=ASOF,
        requirements={"c1": {"required_independent_supports": 1}},
    )
    claim = result.claims[0] if result.claims else {}
    return {
        "mode": mode,
        "eval_scope": eval_scope,
        "aux_scope": None if mode == "VERIFIED_ONLY" else aux_scope,
        "claim_record": claim,
        "claim_state": claim.get("status"),
        "claim_reason": claim.get("reason"),
        "stop_type": result.stop_type,
        "control_closure": bool(result.control_closure),
        "gates": result.gates,
        "false_gates": sorted(k for k, v in result.gates.items() if not v),
        "critical_unresolved": result.raw.get("critical_unresolved", []),
        "claim_support_policy_violations": result.raw.get(
            "claim_support_policy_violations", []
        ),
        "global_consistency_violations": result.raw.get(
            "global_consistency_violations", []
        ),
        "evidence_errors": result.raw.get("evidence_errors", []),
        "identity_errors": result.raw.get("identity_errors", []),
        "integration_errors": result.raw.get("integration_errors", []),
    }


def run_isolated(mode: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_multi_snapshot_retrieval_context",
            "--single-mode",
            mode,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip())
    return json.loads(cp.stdout)


def main() -> dict:
    rows = [run_isolated(mode) for mode in MODES]
    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "MULTI_SNAPSHOT_RETRIEVAL_CONTEXT_REDUCER",
        "state_count": len(rows),
        "modes": list(MODES),
        "rows": rows,
        "interpretation_boundary": (
            "Provenance is DISTINCT. E1 is POSITIVE/CURRENT and sufficient for the "
            "one-support claim. E2 is POSITIVE/STALE and fully verified. This reducer "
            "varies only whether E2 is snapshot-installed, installation order, and "
            "whether the auxiliary snapshot uses the same or a different retrieval "
            "scope from the evaluated E1 snapshot."
        ),
    }
    Path("multi_snapshot_retrieval_context.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-mode", choices=MODES)
    args = parser.parse_args()
    if args.single_mode:
        try:
            out = build_case(args.single_mode)
        except Exception as exc:
            out = {
                "mode": args.single_mode,
                "case_error": f"{type(exc).__name__}: {exc}",
            }
        print(json.dumps(out, sort_keys=True))
    else:
        main()
