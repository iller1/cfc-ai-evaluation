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
import cfc_anchor._engine as frozen_engine

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
    "SINGLE_SCOPE",
    "PARALLEL_NO_SUPERSESSION",
    "VALID_SUCCESSOR_EVALUATED",
    "VALID_PREDECESSOR_EVALUATED",
    "SUPERSEDES_WITHOUT_VERSION_INCREASE",
)


def _install_snapshot(
    c: Controller,
    *,
    tag: str,
    label: str,
    scope_id: str,
    records: list[dict],
    snapshot_version: int,
    supersedes: str | None = None,
):
    draft = c.draft_snapshot(
        records,
        scope_id=scope_id,
        snapshot_id=f"snapshot:multi-scope-supersession:{tag}:{label}",
        snapshot_created_at=ASOF,
        snapshot_available_at=ASOF,
        valid_from=VALID_FROM,
        valid_to=VALID_TO,
        snapshot_version=snapshot_version,
        supersedes=supersedes,
    )
    c.install_verified_snapshot(
        draft,
        records,
        RetrievalAuthorityAttestation(
            f"att:multi-scope-supersession:{tag}:{label}:retrieval",
            AUTHORITIES["RETRIEVAL"],
            c.snapshot_commitment(draft),
            ASOF,
            VALID_FROM,
            VALID_TO,
            supersession_authority_id=(
                AUTHORITIES["RETRIEVAL"] if supersedes is not None else None
            ),
        ),
        VERIFIERS["RETRIEVAL"],
        as_of=ASOF,
    )
    return draft


def build_case(mode: str) -> dict:
    tag = mode.lower()
    c = Controller(trust_policy=_trust_policy())
    identity_id = _install_identity(c, f"supersession:{tag}")
    _install_topology(c, f"supersession:{tag}")

    e1 = _build_record(
        c,
        tag=f"supersession:{tag}",
        identity_id=identity_id,
        relation_mode="DISTINCT",
        idx=1,
        validity="CURRENT",
    )
    records = [e1]

    s1 = f"scope:multi-scope-supersession:{tag}:s1"
    s2 = f"scope:multi-scope-supersession:{tag}:s2"

    d1 = _install_snapshot(
        c,
        tag=tag,
        label="s1",
        scope_id=s1,
        records=records,
        snapshot_version=1,
    )

    d2 = None
    eval_draft = d1
    if mode == "PARALLEL_NO_SUPERSESSION":
        d2 = _install_snapshot(
            c,
            tag=tag,
            label="s2",
            scope_id=s2,
            records=records,
            snapshot_version=1,
        )
        eval_draft = d2
    elif mode == "VALID_SUCCESSOR_EVALUATED":
        d2 = _install_snapshot(
            c,
            tag=tag,
            label="s2",
            scope_id=s2,
            records=records,
            snapshot_version=2,
            supersedes=s1,
        )
        eval_draft = d2
    elif mode == "VALID_PREDECESSOR_EVALUATED":
        d2 = _install_snapshot(
            c,
            tag=tag,
            label="s2",
            scope_id=s2,
            records=records,
            snapshot_version=2,
            supersedes=s1,
        )
        eval_draft = d1
    elif mode == "SUPERSEDES_WITHOUT_VERSION_INCREASE":
        d2 = _install_snapshot(
            c,
            tag=tag,
            label="s2",
            scope_id=s2,
            records=records,
            snapshot_version=1,
            supersedes=s1,
        )
        eval_draft = d2
    elif mode != "SINGLE_SCOPE":
        raise ValueError(mode)

    text = "DemoSubject is safe."
    identity_map = {"c1": identity_id}
    requirements = {"c1": {"required_independent_supports": 1}}

    candidates, _ = frozen_engine.decision_relevant_candidate_map(
        text, identity_map, c.scope, ASOF
    )
    claim_descs = frozen_engine.claim_descriptors(text, identity_map)
    winner = None
    supersession_cert_ids = []
    if claim_descs and candidates:
        claim_desc = claim_descs[0]
        winner, certs = frozen_engine.resolve_claim_snapshot_winner(
            claim_desc, candidates[claim_desc["claim_id"]], ASOF
        )
        supersession_cert_ids = [x.certificate_id for x in certs]

    competition = frozen_engine.make_snapshot_competition(
        text, identity_map, c.scope, eval_draft.scope_id, ASOF
    )
    applicability = frozen_engine.make_snapshot_applicability(
        text, identity_map, c.scope, eval_draft.scope_id, ASOF
    )

    result = c.evaluate_snapshot(
        eval_draft,
        text,
        records,
        identity_map,
        as_of=ASOF,
        requirements=requirements,
    )
    claim = result.claims[0] if result.claims else {}

    return {
        "mode": mode,
        "evaluated_scope": eval_draft.scope_id,
        "candidate_map": candidates,
        "resolved_winner": winner,
        "supersession_certificate_count": len(supersession_cert_ids),
        "snapshot_competition_present": competition is not None,
        "snapshot_applicability_present": applicability is not None,
        "claim_state": claim.get("status"),
        "claim_reason": claim.get("reason"),
        "control_closure": bool(result.control_closure),
        "stop_type": result.stop_type,
        "gates": result.gates,
        "false_gates": sorted(k for k, v in result.gates.items() if not v),
        "global_consistency_violations": result.raw.get(
            "global_consistency_violations", []
        ),
        "integration_errors": result.raw.get("integration_errors", []),
    }


def run_isolated(mode: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_multi_scope_supersession_control",
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
        "test": "MULTI_SCOPE_SUPERSESSION_CONTROL",
        "state_count": len(rows),
        "modes": list(MODES),
        "rows": rows,
        "interpretation_boundary": (
            "All states use one identical POSITIVE/CURRENT E1 record and DISTINCT "
            "provenance. Multiple retrieval scopes have the same semantic projection. "
            "The matrix changes only snapshot competition/supersession structure and "
            "which candidate scope is evaluated."
        ),
    }
    Path("multi_scope_supersession_control.json").write_text(
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
            row = build_case(args.single_mode)
        except Exception as exc:
            row = {
                "mode": args.single_mode,
                "case_error": f"{type(exc).__name__}: {exc}",
            }
        print(json.dumps(row, sort_keys=True))
    else:
        main()
