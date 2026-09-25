from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
from pathlib import Path

from demonstrator import server as demo_server

demo_server.ensure_runtime()
sys.path.insert(0, str(demo_server.RUNTIME))

from cfc_anchor import (
    Controller,
    HostTrustPolicy,
    HostTrustRegistration,
    IdentityAuthorityAttestation,
    SourceSemanticsAuthorityAttestation,
    ProvenanceAuthorityAttestation,
    EvidenceAuthorityAttestation,
    EpistemicRoleAuthorityAttestation,
    RetrievalAuthorityAttestation,
    FailureDomainTopologyAttestation,
)
from demonstrator.custom_case_runner import (
    ASOF,
    VALID_FROM,
    VALID_TO,
    STALE_TO,
    AUTHORITIES,
    VERIFIERS,
)

ORIGIN_FACTORS = (
    "root_origin_shared",
    "origin_shared",
    "extractor_shared",
    "lineage_chain_shared",
)

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


def _shared_token(shared: bool, idx: int, label: str) -> str:
    return f"shared:{label}" if shared else f"iso:e{idx}:{label}"


def build_case(
    *,
    tag: str,
    origin_mask: dict[str, bool] | None = None,
    shared_dependencies: set[str] | None = None,
) -> dict:
    origin_mask = origin_mask or {name: False for name in ORIGIN_FACTORS}
    shared_dependencies = shared_dependencies or set()

    trust = HostTrustPolicy(
        tuple(
            HostTrustRegistration(kind, AUTHORITIES[kind], VERIFIERS[kind])
            for kind in AUTHORITIES
            if kind != "SUPPORT_SET_INDEPENDENCE"
        )
    )
    c = Controller(trust_policy=trust)

    identity = c.draft_identity(
        registry_entry_id=f"id:micro:{tag}:subject:v1",
        surface_subject="DemoSubject",
        domain_id="GENERAL_ENTITY",
        entity_id="entity:demo-subject",
        event_id="event:current",
        version_id="v1",
    )
    c.install_verified_identity(
        identity,
        IdentityAuthorityAttestation(
            f"att:micro:{tag}:identity",
            AUTHORITIES["IDENTITY"],
            c.identity_commitment(identity),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["IDENTITY"],
        as_of=ASOF,
    )

    topology = c.draft_failure_domain_topology()
    c.install_verified_failure_domain_topology(
        topology,
        FailureDomainTopologyAttestation(
            f"att:micro:{tag}:topology",
            AUTHORITIES["FAILURE_DOMAIN_TOPOLOGY"],
            c.failure_domain_topology_commitment(topology),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["FAILURE_DOMAIN_TOPOLOGY"],
        as_of=ASOF,
    )

    records = []
    for idx, validity in ((1, "CURRENT"), (2, "STALE")):
        eid = f"E{idx}:{tag}"
        source_token = f"micro:{tag}:e{idx}"

        # Keep source-semantics distinct in this microfactorial.
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

        root_token = _shared_token(
            origin_mask["root_origin_shared"], idx, "root"
        )
        origin_token = _shared_token(
            origin_mask["origin_shared"], idx, "origin"
        )
        extractor_token = _shared_token(
            origin_mask["extractor_shared"], idx, "extractor"
        )

        if origin_mask["lineage_chain_shared"]:
            lineage = [
                "general-record:lineage:shared:root",
                "general-record:lineage:shared:origin",
            ]
        else:
            lineage = [
                f"general-record:lineage:{tag}:e{idx}:root",
                f"general-record:lineage:{tag}:e{idx}:origin",
            ]

        dependencies = {}
        for key in DEPENDENCY_KEYS:
            prefix = DEPENDENCY_PREFIX[key]
            if key in shared_dependencies:
                dep_id = f"{prefix}:shared:{key}"
            else:
                dep_id = f"{prefix}:iso:{tag}:e{idx}:{key}"
            dependencies[key] = {"state": "KNOWN", "id": dep_id}

        provenance = {
            "source_id": f"general-record:{source_token}",
            "root_origin_id": f"general-record:{root_token}",
            "origin_id": f"general-record:{origin_token}",
            "referent_entity_id": "entity:demo-subject",
            "referent_event_id": "event:current",
            "referent_version_id": "v1",
            "extractor_id": f"extractor:{extractor_token}",
            # Keep common-mode group distinct; it was already isolated as atomic.
            "common_mode_group": f"group:iso:{tag}:e{idx}",
            "lineage": lineage,
            "dependencies": dependencies,
        }

        valid_to = STALE_TO if validity == "STALE" else VALID_TO
        observed_at = "2026-08-30" if validity == "STALE" else ASOF

        evidence = c.draft_evidence_record(
            evidence_id=eid,
            subject="DemoSubject",
            predicate="state",
            value="safe",
            source=f"display:{source_token}",
            identity_registry_entry_id=f"id:micro:{tag}:subject:v1",
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
        records.append(c.evidence_record_mapping(evidence))

    scope_id = f"scope:micro:{tag}"
    snapshot = c.draft_snapshot(
        records,
        scope_id=scope_id,
        snapshot_id=f"snapshot:micro:{tag}",
        snapshot_created_at=ASOF,
        snapshot_available_at=ASOF,
        valid_from=VALID_FROM,
        valid_to=VALID_TO,
    )
    c.install_verified_snapshot(
        snapshot,
        records,
        RetrievalAuthorityAttestation(
            f"att:micro:{tag}:retrieval",
            AUTHORITIES["RETRIEVAL"],
            c.snapshot_commitment(snapshot),
            ASOF,
            VALID_FROM,
            VALID_TO,
        ),
        VERIFIERS["RETRIEVAL"],
        as_of=ASOF,
    )

    result = c.evaluate_snapshot(
        snapshot,
        "DemoSubject is safe.",
        records,
        {"c1": f"id:micro:{tag}:subject:v1"},
        as_of=ASOF,
        requirements={"c1": {"required_independent_supports": 1}},
    )

    claim = result.claims[0] if result.claims else {}
    false_gates = sorted(k for k, v in result.gates.items() if not v)
    return {
        "tag": tag,
        "origin_mask": origin_mask,
        "shared_dependencies": sorted(shared_dependencies),
        "claim_state": claim.get("status"),
        "claim_reason": claim.get("reason"),
        "control_closure": bool(result.control_closure),
        "decision_support_closure_valid": bool(
            result.gates.get("decision_support_closure_valid")
        ),
        "false_gates": false_gates,
        "claim_support_policy_violations": result.raw.get(
            "claim_support_policy_violations", []
        ),
        "critical_unresolved": result.raw.get("critical_unresolved", []),
        "global_consistency_violations": result.raw.get(
            "global_consistency_violations", []
        ),
    }


def run_isolated(mode: str, value: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_stale_relation_microfactorial",
            "--single-mode",
            mode,
            "--single-value",
            value,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip())
    return json.loads(cp.stdout)


def grouped_control(mask_bits: str) -> dict:
    cp = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.review_stale_dependency_factorial",
            "--single-mask",
            mask_bits,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip())
    return json.loads(cp.stdout)


def compact(row: dict) -> dict:
    return {
        "claim_state": row["claim_state"],
        "control_closure": row["control_closure"],
        "false_gates": row["false_gates"],
    }


def main() -> dict:
    origin_rows = []
    for bits in itertools.product((False, True), repeat=len(ORIGIN_FACTORS)):
        mask_bits = "".join("1" if bit else "0" for bit in bits)
        origin_rows.append(run_isolated("origin", mask_bits))

    dependency_values = ["NONE", *DEPENDENCY_KEYS, "ALL"]
    dependency_rows = [
        run_isolated("dependency", value)
        for value in dependency_values
    ]

    origin_blockers = [r for r in origin_rows if not r["control_closure"]]
    origin_minimal = []
    for row in origin_blockers:
        shared = {k for k, v in row["origin_mask"].items() if v}
        if not any(
            {k for k, v in other["origin_mask"].items() if v} < shared
            for other in origin_blockers
        ):
            origin_minimal.append(row)

    dependency_singleton_blockers = [
        r for r in dependency_rows
        if len(r["shared_dependencies"]) == 1 and not r["control_closure"]
    ]

    grouped_origin = grouped_control("0100")
    grouped_dependencies = grouped_control("0001")
    origin_all = next(
        r for r in origin_rows
        if all(r["origin_mask"].values())
    )
    dependency_all = next(
        r for r in dependency_rows
        if len(r["shared_dependencies"]) == len(DEPENDENCY_KEYS)
    )

    result = {
        "controller_anchor": "0.2.90rc1",
        "test": "STALE_RELATION_MICROFACTORIAL",
        "origin_factor_order": list(ORIGIN_FACTORS),
        "origin_state_count": len(origin_rows),
        "origin_allow_count": sum(r["control_closure"] for r in origin_rows),
        "origin_stop_count": sum(not r["control_closure"] for r in origin_rows),
        "origin_minimal_blocking_masks": [
            {
                "origin_mask": r["origin_mask"],
                "claim_state": r["claim_state"],
                "false_gates": r["false_gates"],
            }
            for r in origin_minimal
        ],
        "dependency_state_count": len(dependency_rows),
        "dependency_singleton_blockers": [
            r["shared_dependencies"][0]
            for r in dependency_singleton_blockers
        ],
        "dependency_singleton_allows": [
            r["shared_dependencies"][0]
            for r in dependency_rows
            if len(r["shared_dependencies"]) == 1 and r["control_closure"]
        ],
        "equivalence_controls": {
            "origin_all_vs_grouped_0100": {
                "micro": compact(origin_all),
                "grouped": compact(grouped_origin),
                "matches": compact(origin_all) == compact(grouped_origin),
            },
            "dependency_all_vs_grouped_0001": {
                "micro": compact(dependency_all),
                "grouped": compact(grouped_dependencies),
                "matches": compact(dependency_all) == compact(grouped_dependencies),
            },
        },
        "origin_rows": origin_rows,
        "dependency_rows": dependency_rows,
        "interpretation_boundary": (
            "E1 CURRENT + E2 STALE, both supporting, required supports=1. "
            "Source semantics and common-mode group are held distinct in these "
            "microfactorials. Frozen CFC is unchanged."
        ),
    }

    Path("stale_relation_microfactorial.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-mode", choices=("origin", "dependency"))
    parser.add_argument("--single-value")
    args = parser.parse_args()

    if args.single_mode:
        if args.single_mode == "origin":
            bits = args.single_value or ""
            if len(bits) != len(ORIGIN_FACTORS) or any(ch not in "01" for ch in bits):
                raise SystemExit("origin mask must be four binary digits")
            origin_mask = {
                name: bit == "1"
                for name, bit in zip(ORIGIN_FACTORS, bits)
            }
            print(json.dumps(build_case(
                tag=f"origin:{bits}",
                origin_mask=origin_mask,
                shared_dependencies=set(),
            ), sort_keys=True))
        else:
            value = args.single_value or ""
            if value == "NONE":
                shared = set()
            elif value == "ALL":
                shared = set(DEPENDENCY_KEYS)
            elif value in DEPENDENCY_KEYS:
                shared = {value}
            else:
                raise SystemExit("invalid dependency singleton")
            print(json.dumps(build_case(
                tag=f"dependency:{value}",
                origin_mask={name: False for name in ORIGIN_FACTORS},
                shared_dependencies=shared,
            ), sort_keys=True))
    else:
        main()
