from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from demonstrator import server as demo_server

demo_server.ensure_runtime()
sys.path.insert(0, str(demo_server.RUNTIME))

from cfc_anchor import (
    Controller,
    SourceSemanticsAuthorityAttestation,
    ProvenanceAuthorityAttestation,
    EvidenceAuthorityAttestation,
    EpistemicRoleAuthorityAttestation,
)
import cfc_anchor._engine as frozen_engine

from demonstrator.custom_case_runner import (
    ASOF,
    VALID_FROM,
    VALID_TO,
    STALE_TO,
    AUTHORITIES,
    VERIFIERS,
)
from research.review_stale_relation_snapshot_locality import (
    _trust_policy,
    _install_identity,
    _install_topology,
    _install_snapshot,
)
from research.review_decision_generic_accounting_reachability import (
    _mapping_to_draft,
)

ORIGIN_BLOCKERS = (
    "root_origin_shared",
    "origin_shared",
    "extractor_shared",
)
COMMON_MODE_BLOCKER = "common_mode_group_shared"
DEPENDENCY_KEYS = (
    "data_source",
    "sensor_input",
    "transform",
    "model",
    "extractor",
    "cache",
    "upstream_db",
    "operator",
    "preprocessing",
    "runtime",
)
BLOCKERS = (
    *ORIGIN_BLOCKERS,
    COMMON_MODE_BLOCKER,
    *(f"dependency:{key}" for key in DEPENDENCY_KEYS),
)

DEPENDENCY_PREFIX = {
    "data_source": "data",
    "sensor_input": "sensor",
    "transform": "transform",
    "model": "model",
    "extractor": "extractor",
    "cache": "cache",
    "upstream_db": "db",
    "operator": "operator",
    "preprocessing": "prep",
    "runtime": "runtime",
}


def _shared(blocker: str, key: str) -> bool:
    if blocker == key:
        return True
    if blocker.startswith("dependency:") and key.startswith("dependency:"):
        return blocker == key
    return False


def _build_record(
    c: Controller,
    *,
    tag: str,
    identity_id: str,
    blocker: str,
    idx: int,
    validity: str,
) -> dict:
    eid = f"E{idx}:{tag}"
    source_token = f"taxonomy:{tag}:e{idx}"

    sem_id = f"sem:{source_token}"
    semantics = c.draft_source_semantics(
        semantics_registry_entry_id=sem_id,
        source_id=f"general-record:{source_token}",
        repository_id=f"repo:iso:{tag}:e{idx}",
        producer_id=f"producer:iso:{tag}:e{idx}",
        process_id=f"process:iso:{tag}:e{idx}",
        failure_domain_id=f"fd:iso:{tag}:e{idx}",
        resolution_state="KNOWN",
    )
    c.install_verified_source_semantics(
        semantics,
        SourceSemanticsAuthorityAttestation(
            f"att:{source_token}:semantics",
            AUTHORITIES["SOURCE_SEMANTICS"],
            c.source_semantics_commitment(semantics),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["SOURCE_SEMANTICS"],
        as_of=ASOF,
    )

    root_origin_id = (
        "general-record:root:shared"
        if blocker == "root_origin_shared"
        else f"general-record:root:iso:{tag}:e{idx}"
    )
    origin_id = (
        "general-record:origin:shared"
        if blocker == "origin_shared"
        else f"general-record:origin:iso:{tag}:e{idx}"
    )
    extractor_id = (
        "extractor:shared"
        if blocker == "extractor_shared"
        else f"extractor:iso:{tag}:e{idx}"
    )
    common_mode_group = (
        "group:shared"
        if blocker == COMMON_MODE_BLOCKER
        else f"group:iso:{tag}:e{idx}"
    )

    dependencies = {}
    for key in DEPENDENCY_KEYS:
        prefix = DEPENDENCY_PREFIX[key]
        if blocker == f"dependency:{key}":
            dep_id = f"{prefix}:shared:{key}"
        else:
            dep_id = f"{prefix}:iso:{tag}:e{idx}:{key}"
        dependencies[key] = {"state": "KNOWN", "id": dep_id}

    provenance = {
        "source_id": f"general-record:{source_token}",
        "root_origin_id": root_origin_id,
        "origin_id": origin_id,
        "referent_entity_id": "entity:demo-subject",
        "referent_event_id": "event:current",
        "referent_version_id": "v1",
        "extractor_id": extractor_id,
        "common_mode_group": common_mode_group,
        "lineage": [root_origin_id, origin_id],
        "dependencies": dependencies,
    }

    observed_at = "2026-08-30" if validity == "STALE" else ASOF
    valid_to = STALE_TO if validity == "STALE" else VALID_TO

    evidence = c.draft_evidence_record(
        evidence_id=eid,
        subject="DemoSubject",
        predicate="state",
        value="safe",
        source=f"display:{source_token}",
        identity_registry_entry_id=identity_id,
        authority_id="GENERAL_RECORD_V5",
        authority_record_entity_id="entity:demo-subject",
        authority_record_event_id="event:current",
        authority_record_version_id="v1",
        valid_from=VALID_FROM,
        valid_to=valid_to,
        observed_at=observed_at,
        available_at=observed_at,
        provenance=provenance,
        polarity="POSITIVE",
        source_semantics_id=sem_id,
    )
    c.verify_evidence_provenance(
        evidence,
        ProvenanceAuthorityAttestation(
            f"att:{source_token}:prov",
            AUTHORITIES["PROVENANCE"],
            eid,
            c.provenance_commitment(evidence),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["PROVENANCE"],
        as_of=ASOF,
    )
    c.verify_evidence_authority(
        evidence,
        EvidenceAuthorityAttestation(
            f"att:{source_token}:evidence",
            AUTHORITIES["EVIDENCE_AUTHORITY"],
            eid,
            "GENERAL_RECORD_V5",
            c.evidence_authority_commitment(evidence),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["EVIDENCE_AUTHORITY"],
        as_of=ASOF,
    )
    role = c.draft_epistemic_role(
        evidence,
        epistemic_role="DIRECT_WORLD_RECORD",
    )
    role_installation = c.install_verified_epistemic_role(
        evidence,
        role,
        EpistemicRoleAuthorityAttestation(
            f"att:{source_token}:role",
            AUTHORITIES["EPISTEMIC_ROLE"],
            eid,
            "DIRECT_WORLD_RECORD",
            role.role_commitment,
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["EPISTEMIC_ROLE"],
        as_of=ASOF,
    )
    evidence = c.evidence_with_epistemic_role(evidence, role_installation)
    return c.evidence_record_mapping(evidence)


def build_fixture(blocker: str):
    tag = blocker.replace(":", "-")
    c = Controller(trust_policy=_trust_policy())
    identity_id = _install_identity(c, tag)
    _install_topology(c, tag)
    records = [
        _build_record(
            c,
            tag=tag,
            identity_id=identity_id,
            blocker=blocker,
            idx=1,
            validity="CURRENT",
        ),
        _build_record(
            c,
            tag=tag,
            identity_id=identity_id,
            blocker=blocker,
            idx=2,
            validity="STALE",
        ),
    ]
    snapshot = _install_snapshot(
        c,
        tag=tag,
        label="evaluated",
        records=records,
    )
    return c, identity_id, records, snapshot


def _classify_obligation(internal: dict, public: dict, core: dict) -> str:
    ierr = internal.get("error") or ""
    perr = public.get("error") or ""
    if "invalid generic dependency node" in ierr:
        return "ENGINE_EMITTED_ACCOUNTING_SCHEMA_INCOMPATIBILITY"
    if internal.get("registered") and "endpoints must be selected supports" in perr:
        if core.get("decision_support_closure_valid") is True:
            return "PUBLIC_SELECTED_EXCLUDED_ENDPOINT_REACHABILITY_INCONSISTENCY_CORE_BINDABLE"
        return "PUBLIC_SELECTED_EXCLUDED_ENDPOINT_REACHABILITY_INCONSISTENCY"
    if internal.get("registered") and public.get("draft_created"):
        return "ACCOUNTING_REPRESENTABLE"
    return "UNCLASSIFIED_CONTRACT_BEHAVIOR"


def attempt(blocker: str) -> dict:
    c, identity_id, records, snapshot = build_fixture(blocker)
    text = "DemoSubject is safe."
    claim_map = {"c1": identity_id}
    req = {"c1": {"required_independent_supports": 1}}

    baseline = c.evaluate_snapshot(
        snapshot,
        text,
        records,
        claim_map,
        as_of=ASOF,
        requirements=req,
    )
    baseline_claim = baseline.claims[0] if baseline.claims else {}
    assessments = baseline.raw.get(
        "decision_level_generic_dependency_assessments", []
    )
    required = [
        row
        for row in assessments
        if isinstance(row, dict) and row.get("decision_level_required")
    ]

    graph = baseline.raw.get("decision_support_dependency_graph") or {}
    selected_map = {
        cid: list(vals)
        for cid, vals in (graph.get("selected_support_map") or ())
    }
    decision_evidence = [_mapping_to_draft(c, row) for row in records]

    obligation_rows = []
    for index, obligation in enumerate(required, 1):
        node = tuple(obligation["generic_dependency_node"])
        eids = list(obligation["evidence_ids"])
        accounting_id = f"acct:taxonomy:{blocker.replace(':','-')}:{index}"

        internal = {
            "registered": False,
            "bind_error": None,
            "binding_state": None,
            "error": None,
        }
        core = {
            "attempted": False,
            "error": None,
            "claim_state": None,
            "control_closure": None,
            "decision_support_closure_valid": None,
            "false_gates": None,
            "decision_support_closure_certificate_present": None,
        }
        try:
            row = frozen_engine.register_decision_generic_dependency_accounting(
                accounting_id=accounting_id,
                retrieval_scope_id=snapshot.scope_id,
                claim_ids=["c1"],
                selected_support_map=selected_map,
                generic_dependency_node=node,
                evidence_ids=eids,
                resolution_type=frozen_engine.SUPPORT_UNIVERSE_POLICY[
                    "decision_dependency_accounting_resolution_type"
                ],
                reason="Minimal blocker accounting taxonomy control.",
            )
            internal["registered"] = True
            internal["binding_state"] = row.get("binding_state")
            try:
                frozen_engine.bind_decision_generic_dependency_accountings_for_prepare(
                    text,
                    records,
                    claim_map,
                    ASOF,
                    c.scope,
                    c.extraction,
                    snapshot.scope_id,
                    req,
                    (accounting_id,),
                )
                bound = frozen_engine.SUPPORT_SELECTION_REGISTRY.get(accounting_id)
                internal["binding_state"] = (
                    bound.get("binding_state")
                    if isinstance(bound, dict)
                    else None
                )
            except Exception as exc:
                internal["bind_error"] = f"{type(exc).__name__}: {exc}"

            if internal["binding_state"] == "BOUND":
                core["attempted"] = True
                try:
                    bundle = frozen_engine.prepare(
                        text,
                        records,
                        claim_map,
                        ASOF,
                        c.scope,
                        c.extraction,
                        snapshot.scope_id,
                        req,
                        None,
                    )
                    result = frozen_engine.audit_text(
                        text,
                        records,
                        claim_map,
                        ASOF,
                        c.scope,
                        c.extraction,
                        snapshot.scope_id,
                        req,
                        None,
                        *bundle,
                        resource_exhausted=False,
                    )
                    claims = result.get("claims") or []
                    core.update({
                        "claim_state": (
                            claims[0].get("status") if claims else None
                        ),
                        "control_closure": bool(result.get("control_closure")),
                        "decision_support_closure_valid": bool(
                            result.get("gates", {}).get(
                                "decision_support_closure_valid"
                            )
                        ),
                        "false_gates": sorted(
                            k
                            for k, v in result.get("gates", {}).items()
                            if not v
                        ),
                        "decision_support_closure_certificate_present": (
                            result.get("decision_support_closure_certificate")
                            is not None
                        ),
                    })
                except Exception as exc:
                    core["error"] = f"{type(exc).__name__}: {exc}"
        except Exception as exc:
            internal["error"] = f"{type(exc).__name__}: {exc}"

        public = {
            "draft_created": False,
            "error": None,
        }
        try:
            draft = c.draft_decision_generic_dependency_accounting(
                accounting_id=f"public:{accounting_id}",
                retrieval_scope_id=snapshot.scope_id,
                claim_ids=["c1"],
                selected_support_map=selected_map,
                generic_dependency_node=node,
                evidence_ids=eids,
                reason="Minimal blocker accounting taxonomy control.",
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

        obligation_rows.append({
            "generic_dependency_node": list(node),
            "evidence_ids": eids,
            "endpoint_claim_ownership": obligation.get(
                "endpoint_claim_ownership"
            ),
            "endpoint_classifications": obligation.get(
                "endpoint_classifications"
            ),
            "relevance_classification": obligation.get(
                "relevance_classification"
            ),
            "decision_level_required": obligation.get(
                "decision_level_required"
            ),
            "selected_support_path_relevant": obligation.get(
                "selected_support_path_relevant"
            ),
            "internal_registry": internal,
            "public_draft": public,
            "direct_core_after_exact_bind": core,
            "mechanism": _classify_obligation(internal, public, core),
        })

    mechanisms = sorted({row["mechanism"] for row in obligation_rows})
    return {
        "blocker": blocker,
        "baseline": {
            "claim_state": baseline_claim.get("status"),
            "control_closure": bool(baseline.control_closure),
            "false_gates": sorted(
                k for k, v in baseline.gates.items() if not v
            ),
            "decision_support_closure_valid": bool(
                baseline.gates.get("decision_support_closure_valid")
            ),
        },
        "selected_support_map": selected_map,
        "required_obligation_count": len(required),
        "obligations": obligation_rows,
        "mechanisms": mechanisms,
    }


def run_isolated(blocker: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_minimal_blocker_accounting_taxonomy",
            "--single-blocker",
            blocker,
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if cp.returncode != 0:
        raise RuntimeError(
            f"{blocker}: {cp.stderr.strip() or cp.stdout.strip()}"
        )
    return json.loads(cp.stdout)


def main():
    rows = [run_isolated(blocker) for blocker in BLOCKERS]
    mechanism_counts = {}
    for row in rows:
        for mechanism in row["mechanisms"]:
            mechanism_counts[mechanism] = (
                mechanism_counts.get(mechanism, 0) + 1
            )

    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "MINIMAL_BLOCKER_ACCOUNTING_TAXONOMY",
        "blocker_count": len(BLOCKERS),
        "blockers": list(BLOCKERS),
        "mechanism_counts_by_blocker": mechanism_counts,
        "rows": rows,
        "interpretation_boundary": (
            "Fresh subprocess per minimal blocker. E1 is CURRENT, E2 is STALE, "
            "both are positive matching evidence, required supports=1, and exactly "
            "one minimal relation factor is shared. The review compares frozen "
            "engine-emitted decision obligations with the frozen internal generic "
            "accounting registry, the supported public draft constructor, and—when "
            "the exact accounting can bind—the direct frozen core closure result. "
            "Frozen source and policy are unchanged."
        ),
    }
    Path("minimal_blocker_accounting_taxonomy.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-blocker", choices=BLOCKERS)
    args = parser.parse_args()
    if args.single_blocker:
        print(json.dumps(attempt(args.single_blocker), sort_keys=True))
    else:
        main()
