from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from demonstrator import server as demo_server

demo_server.ensure_runtime()
sys.path.insert(0, str(demo_server.RUNTIME))

import cfc_anchor._engine as frozen_engine

from demonstrator.custom_case_runner import ASOF
from research.review_decision_generic_accounting_reachability import (
    RELATION_MODES,
    build_fixture,
    _mapping_to_draft,
)


def attempt(relation_mode: str) -> dict:
    c, identity_id, records, snapshot = build_fixture(relation_mode)
    text = "DemoSubject is safe."
    claim_map = {"c1": identity_id}
    req = {"c1": {"required_independent_supports": 1}}

    baseline = c.evaluate_snapshot(
        snapshot, text, records, claim_map, as_of=ASOF, requirements=req
    )
    assessments = baseline.raw.get(
        "decision_level_generic_dependency_assessments", []
    )
    required = [
        row
        for row in assessments
        if isinstance(row, dict) and row.get("decision_level_required")
    ]
    if len(required) != 1:
        raise RuntimeError(
            f"{relation_mode}: expected one required obligation, got {len(required)}"
        )

    obligation = required[0]
    node = tuple(obligation["generic_dependency_node"])
    eids = list(obligation["evidence_ids"])

    graph = baseline.raw.get("decision_support_dependency_graph") or {}
    selected_map = {
        cid: list(vals)
        for cid, vals in (graph.get("selected_support_map") or ())
    }

    internal = {
        "registered": False,
        "error": None,
        "binding_state": None,
    }
    try:
        row = frozen_engine.register_decision_generic_dependency_accounting(
            accounting_id=f"acct:schema:{relation_mode.lower()}",
            retrieval_scope_id=snapshot.scope_id,
            claim_ids=["c1"],
            selected_support_map=selected_map,
            generic_dependency_node=node,
            evidence_ids=eids,
            resolution_type=frozen_engine.SUPPORT_UNIVERSE_POLICY[
                "decision_dependency_accounting_resolution_type"
            ],
            reason="Exact obligation schema compatibility probe.",
        )
        internal["registered"] = True
        internal["binding_state"] = row.get("binding_state")
    except Exception as exc:
        internal["error"] = f"{type(exc).__name__}: {exc}"

    public = {
        "draft_created": False,
        "error": None,
    }
    decision_evidence = [_mapping_to_draft(c, row) for row in records]
    try:
        draft = c.draft_decision_generic_dependency_accounting(
            accounting_id=f"acct:public-schema:{relation_mode.lower()}",
            retrieval_scope_id=snapshot.scope_id,
            claim_ids=["c1"],
            selected_support_map=selected_map,
            generic_dependency_node=node,
            evidence_ids=eids,
            reason="Exact obligation schema compatibility probe.",
            text=text,
            evidence=decision_evidence,
            claim_identity_map=claim_map,
            as_of=ASOF,
            requirements=req,
        )
        public["draft_created"] = True
        public["draft_generic_dependency_node"] = list(
            draft.generic_dependency_node
        )
    except Exception as exc:
        public["error"] = f"{type(exc).__name__}: {exc}"

    return {
        "relation_mode": relation_mode,
        "baseline": {
            "claim_state": (
                baseline.claims[0].get("status") if baseline.claims else None
            ),
            "control_closure": bool(baseline.control_closure),
            "false_gates": sorted(k for k, v in baseline.gates.items() if not v),
        },
        "obligation": {
            "generic_dependency_node": list(node),
            "node_arity": len(node),
            "node_nonblank": [
                isinstance(x, str) and bool(x)
                for x in node
            ],
            "evidence_ids": eids,
            "selected_support_map": selected_map,
            "relevance_classification": obligation.get(
                "relevance_classification"
            ),
            "decision_level_required": obligation.get(
                "decision_level_required"
            ),
        },
        "internal_registry_exact_obligation": internal,
        "public_draft_exact_obligation": public,
    }


def run_isolated(mode: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_decision_obligation_schema_compatibility",
            "--single-relation",
            mode,
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
        "test": "DECISION_OBLIGATION_SCHEMA_COMPATIBILITY",
        "rows": rows,
        "interpretation_boundary": (
            "Compares exact generic-dependency obligation node shapes emitted by "
            "the frozen decision engine with the exact node schema accepted by "
            "the frozen internal accounting registry and public Controller draft. "
            "No frozen source or policy is modified."
        ),
    }
    Path("decision_obligation_schema_compatibility.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-relation", choices=RELATION_MODES)
    args = parser.parse_args()
    if args.single_relation:
        print(json.dumps(attempt(args.single_relation), sort_keys=True))
    else:
        main()
