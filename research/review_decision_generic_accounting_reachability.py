from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from demonstrator import server as demo_server

demo_server.ensure_runtime()
sys.path.insert(0, str(demo_server.RUNTIME))

from cfc_anchor import Controller
from demonstrator.custom_case_runner import ASOF
from research.review_stale_relation_snapshot_locality import (
    _trust_policy,
    _install_identity,
    _install_topology,
    _build_record,
    _install_snapshot,
)

RELATION_MODES = ("COMMON_MODE", "ROOT_ORIGIN", "GENERIC_DEPENDENCY")

NODES = {
    "COMMON_MODE": ("COMMON_MODE", "", "group:shared"),
    "ROOT_ORIGIN": ("LINEAGE", "", "general-record:root:shared"),
    "GENERIC_DEPENDENCY": ("DEPENDENCY", "data_source", "shared"),
}


def build_fixture(relation_mode: str):
    tag=f"accounting-reachability:{relation_mode.lower()}"
    c=Controller(trust_policy=_trust_policy())
    identity_id=_install_identity(c,tag)
    _install_topology(c,tag)
    e1=_build_record(c,tag=tag,identity_id=identity_id,relation_mode=relation_mode,idx=1,validity="CURRENT")
    e2=_build_record(c,tag=tag,identity_id=identity_id,relation_mode=relation_mode,idx=2,validity="STALE")
    records=[e1,e2]
    snapshot=_install_snapshot(c,tag=tag,label="evaluated",records=records)
    return c, identity_id, records, snapshot


def _mapping_to_draft(c: Controller, row: dict):
    return c.draft_evidence_record(
        evidence_id=row["evidence_id"],
        subject=row["subject"],
        predicate=row["predicate"],
        value=row["value"],
        source=row["source"],
        identity_registry_entry_id=row["identity_registry_entry_id"],
        authority_id=row["authority_id"],
        authority_record_entity_id=row["authority_record_entity_id"],
        authority_record_event_id=row["authority_record_event_id"],
        authority_record_version_id=row["authority_record_version_id"],
        valid_from=row["valid_from"],
        valid_to=row["valid_to"],
        observed_at=row["observed_at"],
        available_at=row["available_at"],
        provenance=row["provenance"],
        polarity=row["polarity"],
        source_semantics_id=row["source_semantics_id"],
        epistemic_role_record_id=row.get("epistemic_role_record_id"),
    )


def attempt(relation_mode: str) -> dict:
    c, identity_id, records, snapshot = build_fixture(relation_mode)
    eids=[r["evidence_id"] for r in records]
    decision_evidence=[_mapping_to_draft(c,r) for r in records]
    e1,e2=eids
    text="DemoSubject is safe."
    claim_map={"c1": identity_id}
    req={"c1":{"required_independent_supports":1}}
    node=NODES[relation_mode]

    baseline=c.evaluate_snapshot(
        snapshot,text,records,claim_map,as_of=ASOF,requirements=req
    )
    baseline_claim=baseline.claims[0] if baseline.claims else {}

    attempts={}
    for label,selected_map in (
        ("EXACT_ENGINE_SELECTED_MAP",{"c1":[e1]}),
        ("EXPANDED_ENDPOINT_SELECTED_MAP",{"c1":[e1,e2]}),
    ):
        try:
            draft=c.draft_decision_generic_dependency_accounting(
                accounting_id=f"acct:{relation_mode.lower()}:{label.lower()}",
                retrieval_scope_id=snapshot.scope_id,
                claim_ids=["c1"],
                selected_support_map=selected_map,
                generic_dependency_node=node,
                evidence_ids=[e1,e2],
                reason="Reachability control for stale mixed endpoint obligation.",
                text=text,
                evidence=decision_evidence,
                claim_identity_map=claim_map,
                as_of=ASOF,
                requirements=req,
            )
            attempts[label]={
                "draft_created":True,
                "error":None,
                "draft_selected_support_map":[[cid,list(vals)] for cid,vals in draft.selected_support_map],
                "draft_evidence_ids":list(draft.evidence_ids),
                "draft_generic_dependency_node":list(draft.generic_dependency_node),
                "decision_context_commitment":draft.decision_context_commitment,
            }
        except Exception as exc:
            attempts[label]={
                "draft_created":False,
                "error":f"{type(exc).__name__}: {exc}",
            }

    return {
        "relation_mode":relation_mode,
        "baseline":{
            "claim_state":baseline_claim.get("status"),
            "control_closure":bool(baseline.control_closure),
            "false_gates":sorted(k for k,v in baseline.gates.items() if not v),
        },
        "obligation":{
            "generic_dependency_node":list(node),
            "evidence_ids":[e1,e2],
            "actual_selected_support_map":{"c1":[e1]},
            "stale_endpoint":e2,
        },
        "attempts":attempts,
    }


def run_isolated(mode:str)->dict:
    cp=subprocess.run(
        [sys.executable,"-m","research.review_decision_generic_accounting_reachability","--single-relation",mode],
        capture_output=True,text=True,timeout=40,
    )
    if cp.returncode!=0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip())
    return json.loads(cp.stdout)


def main():
    rows=[run_isolated(m) for m in RELATION_MODES]
    result={
        "controller_anchor":"0.2.90rc1",
        "test":"DECISION_GENERIC_ACCOUNTING_PUBLIC_DRAFT_REACHABILITY",
        "state_count":len(rows),
        "rows":rows,
        "interpretation_boundary":(
            "Tests only whether the public Controller draft API can represent the exact "
            "decision-level generic dependency obligation already observed in the stale-E2 "
            "boundary. No frozen source, policy, registry semantics, or evaluation rule is modified."
        ),
    }
    Path("decision_generic_accounting_reachability.json").write_text(
        json.dumps(result,indent=2,sort_keys=True),encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--single-relation",choices=RELATION_MODES)
    a=p.parse_args()
    if a.single_relation:
        print(json.dumps(attempt(a.single_relation),sort_keys=True))
    else:
        main()
