from __future__ import annotations

"""
CFC-next 0.3.0a1 decision-accounting candidate.

This module is a separately versioned candidate layered over the frozen
CFC Anchor 0.2.90rc1 runtime. It applies only the two admission repairs
specified in research/cfc_next_decision_accounting_repair_spec.json.

The frozen wheel itself is never modified.
"""

from demonstrator import server as demo_server

demo_server.ensure_runtime()

import sys

if str(demo_server.RUNTIME) not in sys.path:
    sys.path.insert(0, str(demo_server.RUNTIME))

import cfc_anchor
from cfc_anchor import Controller as FrozenController
import cfc_anchor._engine as _engine


CANDIDATE_VERSION = "0.3.0a1"
FROZEN_REFERENCE = "CFC Anchor 0.2.90rc1"


def generic_accounting_node_valid(node) -> bool:
    if not isinstance(node, tuple) or len(node) != 3:
        return False
    if any(not isinstance(x, str) for x in node):
        return False
    node_type, dimension, identifier = node
    if not node_type.strip() or not identifier.strip():
        return False
    if node_type in set(_engine.SOURCE_SEMANTIC_NODE_TYPES):
        return False
    if node_type in {"LINEAGE", "COMMON_MODE"}:
        return dimension == ""
    if not dimension.strip():
        return False
    if node_type == "DEPENDENCY":
        return dimension in set(_engine.DEPENDENCY_PREFIX)
    if node_type == "EXTRACTOR":
        return dimension == "extractor"
    return True


def _candidate_register_decision_generic_dependency_accounting(
    accounting_id,
    retrieval_scope_id,
    claim_ids,
    selected_support_map,
    generic_dependency_node,
    evidence_ids,
    resolution_type,
    reason,
    authorizer_id="LOCAL_SUPPORT_UNIVERSE_AUTHORITY",
):
    if not _engine.support_selection_registry_key_identity_coherent():
        raise ValueError("support selection registry key identity mismatch")
    if accounting_id in _engine.SUPPORT_SELECTION_REGISTRY:
        raise ValueError("duplicate generic dependency accounting id")
    if not all(
        _engine.nonblank(x)
        for x in (
            accounting_id,
            retrieval_scope_id,
            resolution_type,
            reason,
            authorizer_id,
        )
    ):
        raise ValueError("invalid generic dependency accounting")
    if authorizer_id not in set(
        _engine.SUPPORT_UNIVERSE_POLICY["allowed_authorizers"]
    ):
        raise ValueError("unauthorized generic accounting authorizer")
    required = _engine.SUPPORT_UNIVERSE_POLICY.get(
        "decision_dependency_accounting_resolution_type"
    )
    if resolution_type != required:
        raise ValueError("invalid generic dependency accounting resolution")

    node = tuple(generic_dependency_node or ())
    if not generic_accounting_node_valid(node):
        raise ValueError("invalid generic dependency node")

    rr = _engine.RETRIEVAL_SCOPE_REGISTRY.get(retrieval_scope_id)
    if rr is None:
        raise ValueError("unknown retrieval scope")

    cids = tuple(sorted(set(claim_ids or ())))
    if not cids or len(cids) != len(tuple(claim_ids or ())):
        raise ValueError("invalid decision claim ids")

    smap = _engine._canonical_selected_support_map(selected_support_map)
    if smap is None or tuple(cid for cid, _ in smap) != cids:
        raise ValueError(
            "selected support map must exactly cover decision claims"
        )

    eids = tuple(sorted(set(evidence_ids or ())))
    if len(eids) < 2 or len(eids) != len(tuple(evidence_ids or ())):
        raise ValueError("generic accounting needs exact endpoint set")

    row = {
        "record_type": _engine.DECISION_GENERIC_DEPENDENCY_ACCOUNTING_RECORD_TYPE,
        "dependency_channel": _engine.GENERIC_DEPENDENCY_ACCOUNTING_CHANNEL,
        "accounting_id": accounting_id,
        "binding_state": "PENDING",
        "retrieval_scope_id": retrieval_scope_id,
        "retrieval_snapshot_id": rr.get("snapshot_id"),
        "claim_ids": cids,
        "claim_ids_hash": _engine.sha(cids),
        "selected_support_map": smap,
        "selected_support_map_hash": _engine.sha(smap),
        "generic_dependency_node": node,
        "generic_dependency_node_hash": _engine.sha(node),
        "evidence_ids": eids,
        "evidence_ids_hash": _engine.sha(eids),
        "resolution_type": resolution_type,
        "reason": reason,
        "authorizer_id": authorizer_id,
        "support_universe_policy_hash": _engine.support_universe_policy_hash(),
        "persistence_history_commitment_version": _engine.PERSISTENCE_HISTORY_COMMITMENT_VERSION,
        "persistence_history_commitment": _engine.decision_persistence_history_commitment(),
        "audit_context_id": None,
        "matching_support_universe_map_hash": None,
        "decision_dependency_graph_hash": None,
        "decision_evidence_ownership_map_hash": None,
        "decision_generic_dependency_universe_hash": None,
        "decision_generic_dependency_records_hash": None,
        "decision_generic_dependency_obligations_hash": None,
        "provenance_policy_hash": None,
        "dependency_ontology_hash": None,
        "dependency_justification_registry_hash": None,
        "representation_equivalence_policy_hash": _engine.generic_relation_source_identity_policy_hash(),
        "representation_equivalence_registry_hash": _engine.generic_representation_equivalence_registry_hash(),
        "representation_equivalence_certificate_registry_hash": _engine.generic_representation_equivalence_certificate_registry_hash(),
        "active_equivalence_ids_hash": None,
        "inactive_equivalence_records_hash": None,
        "equivalence_applicability_records_hash": None,
        "contextual_equivalence_resolution_hash": None,
        "complete_raw_representation_inventory_hash": None,
        "representation_classes_present_hash": None,
        "candidate_semantic_descriptor_records_hash": None,
        "cross_representation_pair_coverage_records_hash": None,
        "proven_non_candidate_records_hash": None,
        "candidate_representation_pair_universe_hash": None,
        "candidate_disposition_records_hash": None,
        "ontology_prefix_map_hash": None,
        "source_discovery_signal_hash": None,
        "typed_discovery_signal_hash": None,
        "representation_distinctness_registry_hash": _engine.generic_representation_distinctness_registry_hash(),
        "representation_distinctness_certificate_registry_hash": _engine.generic_representation_distinctness_certificate_registry_hash(),
        "representation_completeness_certificate_hash": None,
        "generic_dependency_record_hash": None,
        "accounting_scope_hash": None,
    }
    _engine.SUPPORT_SELECTION_REGISTRY[accounting_id] = row
    _engine._authorize_fresh_decision_row(accounting_id)
    return _engine.copy.deepcopy(row)


_PATCH_INSTALLED = False
_FROZEN_REGISTER = _engine.register_decision_generic_dependency_accounting


def install_candidate_engine_patch() -> None:
    global _PATCH_INSTALLED
    if _PATCH_INSTALLED:
        return
    _engine.register_decision_generic_dependency_accounting = (
        _candidate_register_decision_generic_dependency_accounting
    )
    _PATCH_INSTALLED = True


class Controller(FrozenController):
    candidate_version = CANDIDATE_VERSION
    frozen_reference = FROZEN_REFERENCE

    def __init__(self, *args, **kwargs):
        install_candidate_engine_patch()
        super().__init__(*args, **kwargs)

    def draft_decision_generic_dependency_accounting(
        self,
        *,
        accounting_id,
        retrieval_scope_id,
        claim_ids,
        selected_support_map,
        generic_dependency_node,
        evidence_ids,
        reason,
        text,
        evidence,
        claim_identity_map,
        as_of,
        requirements=None,
        waivers=None,
    ):
        if not all(
            isinstance(x, str) and x.strip()
            for x in (accounting_id, retrieval_scope_id, reason)
        ):
            raise ValueError(
                "invalid decision generic dependency accounting draft"
            )

        cids = tuple(sorted(set(claim_ids or ())))
        if (
            not cids
            or len(cids) != len(tuple(claim_ids or ()))
            or any(not isinstance(x, str) or not x.strip() for x in cids)
        ):
            raise ValueError("invalid decision claim ids")

        smap = self._canonical_decision_selected_support_map(
            selected_support_map
        )
        if tuple(cid for cid, _ in smap) != cids:
            raise ValueError("selected support map must exactly cover claim ids")

        node = tuple(generic_dependency_node or ())
        if not generic_accounting_node_valid(node):
            raise ValueError("invalid generic dependency node")

        eids = tuple(sorted(set(evidence_ids or ())))
        if len(eids) < 2 or len(eids) != len(tuple(evidence_ids or ())):
            raise ValueError(
                "generic dependency accounting requires at least two unique evidence ids"
            )

        rows = self._canonical_decision_evidence(evidence)
        known = {x.evidence_id for x in rows}
        if not set(eids).issubset(known):
            raise ValueError(
                "generic dependency endpoints must be present in evidence"
            )

        rr = _engine.RETRIEVAL_SCOPE_REGISTRY.get(retrieval_scope_id)
        if not isinstance(rr, dict):
            raise ValueError("retrieval scope is not installed")
        snapshot_ids = set(rr.get("expected_evidence_ids", ()))
        if not set(eids).issubset(snapshot_ids):
            raise ValueError(
                "generic dependency endpoints must be present in evaluated snapshot"
            )

        snapshot_rows = [
            row for row in rows
            if row.evidence_id in snapshot_ids
        ]
        raw_snapshot = [
            self.evidence_record_mapping(row)
            for row in snapshot_rows
        ]
        fresh = super().evaluate(
            text,
            raw_snapshot,
            claim_identity_map,
            as_of=as_of,
            retrieval_scope=retrieval_scope_id,
            requirements=requirements,
            waivers=waivers,
        )
        graph = fresh.raw.get("decision_support_dependency_graph") or {}
        fresh_smap = tuple(graph.get("selected_support_map") or ())
        if tuple(smap) != fresh_smap:
            raise ValueError(
                "selected support map does not match current decision graph"
            )

        assessments = fresh.raw.get(
            "decision_level_generic_dependency_assessments", ()
        )
        exact_matches = [
            row
            for row in assessments
            if (
                isinstance(row, dict)
                and row.get("decision_level_required") is True
                and tuple(row.get("generic_dependency_node") or ()) == node
                and tuple(sorted(row.get("evidence_ids") or ())) == eids
            )
        ]
        if len(exact_matches) != 1:
            raise ValueError(
                "generic dependency accounting does not match exact required decision obligation"
            )

        ctx = self.decision_context_commitment(
            text,
            rows,
            claim_identity_map,
            as_of=as_of,
            retrieval_scope=retrieval_scope_id,
            requirements=requirements,
            waivers=waivers,
        )
        return cfc_anchor.DecisionGenericDependencyAccountingDraft(
            accounting_id,
            retrieval_scope_id,
            cids,
            smap,
            (node[0], node[1], node[2]),
            eids,
            _engine.SUPPORT_UNIVERSE_POLICY[
                "decision_dependency_accounting_resolution_type"
            ],
            reason,
            ctx,
        )


install_candidate_engine_patch()

__all__ = [
    "Controller",
    "CANDIDATE_VERSION",
    "FROZEN_REFERENCE",
    "generic_accounting_node_valid",
    "install_candidate_engine_patch",
]
