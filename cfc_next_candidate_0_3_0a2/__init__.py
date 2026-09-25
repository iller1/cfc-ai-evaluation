from __future__ import annotations

"""
CFC-next 0.3.0a2 isolated decision-accounting candidate.

This is a separately versioned successor to 0.3.0a1. It preserves the
accepted Repair A / Repair B semantics while removing the 0.3.0a1
import-time mutation of cfc_anchor._engine.

The frozen CFC Anchor 0.2.90rc1 wheel is never modified.
"""

from demonstrator import server as demo_server

demo_server.ensure_runtime()

import sys

if str(demo_server.RUNTIME) not in sys.path:
    sys.path.insert(0, str(demo_server.RUNTIME))

import cfc_anchor
from cfc_anchor import Controller as FrozenController
import cfc_anchor._engine as _engine


CANDIDATE_VERSION = "0.3.0a2"
FROZEN_REFERENCE = "CFC Anchor 0.2.90rc1"

_controller_module = sys.modules[FrozenController.__module__]
_requires_host_trust = getattr(_controller_module, "_requires_host_trust")
_DECISION_ATTESTATION_SCHEMA = getattr(
    _controller_module,
    "_DECISION_GENERIC_DEPENDENCY_ACCOUNTING_ATTESTATION_SCHEMA",
)
_RESERVED_ENGINE_AUTHORITY = getattr(
    _controller_module,
    "_RESERVED_ENGINE_DECISION_DEPENDENCY_ACCOUNTING_AUTHORITY",
)
_VERIFIED_GENERIC_RUNTIME = getattr(
    _controller_module,
    "_VERIFIED_DECISION_GENERIC_DEPENDENCY_ACCOUNTING_RUNTIME",
)
_VERIFIED_GENERIC_METADATA = getattr(
    _controller_module,
    "_VERIFIED_DECISION_GENERIC_DEPENDENCY_ACCOUNTING_METADATA",
)


def generic_accounting_node_valid(node) -> bool:
    """Repair A validator aligned with the engine-emitted generic node domain."""
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
    """Repair A registration path without replacing the frozen engine function."""
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
        "persistence_history_commitment_version": (
            _engine.PERSISTENCE_HISTORY_COMMITMENT_VERSION
        ),
        "persistence_history_commitment": (
            _engine.decision_persistence_history_commitment()
        ),
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
        "representation_equivalence_policy_hash": (
            _engine.generic_relation_source_identity_policy_hash()
        ),
        "representation_equivalence_registry_hash": (
            _engine.generic_representation_equivalence_registry_hash()
        ),
        "representation_equivalence_certificate_registry_hash": (
            _engine.generic_representation_equivalence_certificate_registry_hash()
        ),
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
        "representation_distinctness_registry_hash": (
            _engine.generic_representation_distinctness_registry_hash()
        ),
        "representation_distinctness_certificate_registry_hash": (
            _engine.generic_representation_distinctness_certificate_registry_hash()
        ),
        "representation_completeness_certificate_hash": None,
        "generic_dependency_record_hash": None,
        "accounting_scope_hash": None,
    }

    _engine.SUPPORT_SELECTION_REGISTRY[accounting_id] = row
    _engine._authorize_fresh_decision_row(accounting_id)
    return _engine.copy.deepcopy(row)


class Controller(FrozenController):
    """CFC-next 0.3.0a2 with isolated Repair A / Repair B admission."""

    candidate_version = CANDIDATE_VERSION
    frozen_reference = FROZEN_REFERENCE

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

    @_requires_host_trust("DECISION_GENERIC_DEPENDENCY_ACCOUNTING")
    def install_verified_decision_generic_dependency_accounting(
        self,
        draft,
        evidence,
        attestation,
        verifier,
        *,
        text,
        claim_identity_map,
        as_of,
        requirements=None,
        waivers=None,
    ):
        if not isinstance(
            draft,
            cfc_anchor.DecisionGenericDependencyAccountingDraft,
        ):
            raise TypeError(
                "draft must be DecisionGenericDependencyAccountingDraft"
            )

        rows = self._canonical_decision_evidence(evidence)
        self._require_retrieval_runtime_verified(draft.retrieval_scope_id)

        current_ctx = self.decision_context_commitment(
            text,
            rows,
            claim_identity_map,
            as_of=as_of,
            retrieval_scope=draft.retrieval_scope_id,
            requirements=requirements,
            waivers=waivers,
        )
        if current_ctx != draft.decision_context_commitment:
            raise ValueError(
                "accounting draft is not bound to this decision context"
            )

        expected = self.decision_generic_dependency_accounting_commitment(
            draft,
            rows,
        )
        self._validate_decision_attestation(
            attestation,
            _DECISION_ATTESTATION_SCHEMA,
            _RESERVED_ENGINE_AUTHORITY,
            expected,
            as_of=as_of,
            commitment_field="accounting_commitment",
        )

        verify = getattr(verifier, "verify", None)
        if not callable(verify):
            raise TypeError(
                "verifier must implement verify(attestation, *, draft, evidence)"
            )

        try:
            verdict = verify(attestation, draft=draft, evidence=rows)
        except Exception as exc:
            raise ValueError(
                "decision generic dependency accounting verifier failed closed"
            ) from exc

        VerdictType = cfc_anchor.DecisionGenericDependencyAccountingVerdict
        if (
            not isinstance(verdict, VerdictType)
            or verdict.approved is not True
            or verdict.attestation_id != attestation.attestation_id
            or verdict.authority_id != attestation.authority_id
            or verdict.accounting_id != draft.accounting_id
            or not isinstance(verdict.verifier_id, str)
            or not verdict.verifier_id.strip()
            or not isinstance(verdict.verification_method, str)
            or not verdict.verification_method.strip()
        ):
            raise ValueError(
                "generic dependency accounting verifier did not approve exact attestation"
            )

        existing = _engine.SUPPORT_SELECTION_REGISTRY.get(
            draft.accounting_id
        )
        idem = existing is not None

        if existing is None:
            _candidate_register_decision_generic_dependency_accounting(
                draft.accounting_id,
                draft.retrieval_scope_id,
                draft.claim_ids,
                dict(draft.selected_support_map),
                draft.generic_dependency_node,
                draft.evidence_ids,
                draft.resolution_type,
                draft.reason,
                authorizer_id=_RESERVED_ENGINE_AUTHORITY,
            )
            row = _engine.SUPPORT_SELECTION_REGISTRY[draft.accounting_id]
        else:
            row = existing
            if (
                row.get("record_type")
                != _engine.DECISION_GENERIC_DEPENDENCY_ACCOUNTING_RECORD_TYPE
                or tuple(row.get("claim_ids", ())) != draft.claim_ids
                or tuple(row.get("selected_support_map", ()))
                != draft.selected_support_map
                or tuple(row.get("generic_dependency_node", ()))
                != draft.generic_dependency_node
                or tuple(row.get("evidence_ids", ())) != draft.evidence_ids
                or row.get("retrieval_scope_id")
                != draft.retrieval_scope_id
                or row.get("resolution_type") != draft.resolution_type
                or row.get("reason") != draft.reason
            ):
                raise ValueError(
                    "generic dependency accounting id already exists with different content"
                )

        runtime = self._decision_accounting_runtime_commitment(
            draft.accounting_id,
            _engine.DECISION_GENERIC_DEPENDENCY_ACCOUNTING_RECORD_TYPE,
        )
        _VERIFIED_GENERIC_RUNTIME[draft.accounting_id] = runtime
        _VERIFIED_GENERIC_METADATA[draft.accounting_id] = {
            "authority_id": attestation.authority_id,
            "attestation_id": attestation.attestation_id,
            "verifier_id": verdict.verifier_id,
            "accounting_commitment": attestation.accounting_commitment,
            "decision_context_commitment": (
                draft.decision_context_commitment
            ),
        }

        InstallationType = (
            cfc_anchor.DecisionGenericDependencyAccountingInstallation
        )
        return InstallationType(
            draft.accounting_id,
            attestation.authority_id,
            attestation.attestation_id,
            verdict.verifier_id,
            verdict.verification_method,
            attestation.accounting_commitment,
            True,
            row.get("binding_state") == "BOUND",
            idem,
        )


__all__ = [
    "Controller",
    "CANDIDATE_VERSION",
    "FROZEN_REFERENCE",
    "generic_accounting_node_valid",
]
