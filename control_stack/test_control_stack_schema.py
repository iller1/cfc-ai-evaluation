import copy
import json
import unittest

from control_stack.schema_contract import (
    ContractError,
    SCHEMA_VERSION,
    fingerprint,
    load_schema,
    round_trip,
    validate_envelope,
)


def valid_envelope():
    return {
        "schema_version": SCHEMA_VERSION,
        "envelope_id": "env-001",
        "identity": {
            "case_id": "case-001",
            "arm_id": "arm-a",
            "conversation_id": "conv-001",
            "state_id": "state-002",
            "snapshot_id": "snapshot-002",
            "lineage_id": "lineage-001",
            "previous_state_id": "state-001",
            "state_fingerprint": "a" * 64,
        },
        "state_integrity": {
            "status": "STATE_VALID",
            "binding_status": "BOUND",
            "lineage_status": "ESTABLISHED",
            "unresolved": [],
        },
        "evidence": {
            "status": "EVIDENCE_APPLICABLE",
            "provenance_state": "ESTABLISHED",
            "applicability_state": "APPLICABLE",
            "dependency_state": "RESOLVED",
            "evidence_set": [
                {
                    "evidence_id": "E1",
                    "source_id": "S1",
                    "validity": "CURRENT",
                    "scope_status": "MATCH",
                    "failure_domain_id": "FD1",
                }
            ],
            "missing_evidence": [],
            "drift_state": "NO_DRIFT",
        },
        "continuity": {
            "status": "CONTINUITY_ESTABLISHED",
            "transition_type": "EXACT_SUCCESSOR",
            "reproducibility_state": "ESTABLISHED",
            "threshold_state": "WITHIN",
            "unresolved": [],
        },
        "authority": {
            "state": "ESTABLISHED",
            "source": "scope-bound-authority",
            "valid_from": None,
            "valid_to": None,
            "revoked": False,
        },
        "cfc": {
            "decision": "CONTINUE",
            "authority_state": "ESTABLISHED",
            "blockers": [],
            "reason": "all explicit gates satisfied",
            "controller_version": "0.2.90rc1",
            "controller_identity": "frozen-anchor-0.2.90rc1",
        },
        "execution": {
            "attempted": False,
            "executed": False,
            "execution_status": "NOT_ATTEMPTED",
            "effect_handle": None,
            "idempotency_key": None,
            "pre_execution_state_id": None,
            "receipt_id": None,
        },
        "audit": {
            "component_versions": {
                "schema": "0.1",
                "state_integrity": "0.1",
                "evidence": "0.1",
                "continuity": "0.1",
                "cfc_adapter": "0.1",
            },
            "receipts": ["receipt-state-001"],
            "supersedes": [],
            "superseded_by": [],
            "claim_ceiling": "synthetic control-stack contract validation only",
        },
    }


class ControlStackSchemaTests(unittest.TestCase):
    def test_schema_file_declares_strict_root_contract(self):
        schema = load_schema()
        self.assertEqual(
            schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertIn("allOf", schema["properties"]["evidence"])
        self.assertEqual(
            set(schema["required"]),
            {
                "schema_version",
                "envelope_id",
                "identity",
                "state_integrity",
                "evidence",
                "continuity",
                "authority",
                "cfc",
                "execution",
                "audit",
            },
        )

    def test_valid_envelope_passes(self):
        value = valid_envelope()
        self.assertEqual(validate_envelope(value), value)

    def test_round_trip_preserves_exact_semantics(self):
        value = valid_envelope()
        value["evidence"]["drift_state"] = "UNRESOLVED"
        value["continuity"]["status"] = "CONTINUITY_UNKNOWN"
        value["cfc"] = {
            "decision": "HOLD",
            "authority_state": "NOT_ESTABLISHED",
            "blockers": ["DRIFT_UNRESOLVED", "CONTINUITY_UNKNOWN"],
            "reason": "explicit unresolved upstream state",
            "controller_version": "0.2.90rc1",
            "controller_identity": "frozen-anchor-0.2.90rc1",
        }
        value["authority"]["state"] = "NOT_ESTABLISHED"

        restored = round_trip(value)

        self.assertEqual(restored, value)
        self.assertEqual(restored["evidence"]["drift_state"], "UNRESOLVED")
        self.assertEqual(
            restored["continuity"]["status"],
            "CONTINUITY_UNKNOWN",
        )
        self.assertEqual(restored["cfc"]["decision"], "HOLD")

    def test_fingerprint_is_deterministic_across_key_order(self):
        value = valid_envelope()
        reordered = json.loads(json.dumps(value))
        reordered = {key: reordered[key] for key in reversed(list(reordered))}
        self.assertEqual(fingerprint(value), fingerprint(reordered))

    def test_undeclared_root_field_is_rejected(self):
        value = valid_envelope()
        value["implicit_upgrade"] = True
        with self.assertRaisesRegex(ContractError, "UNDECLARED"):
            validate_envelope(value)

    def test_schema_version_mismatch_is_rejected(self):
        value = valid_envelope()
        value["schema_version"] = "CONTROL_STACK_SCHEMA_v0.2"
        with self.assertRaisesRegex(ContractError, "SCHEMA_VERSION_MISMATCH"):
            validate_envelope(value)

    def test_state_unknown_cannot_continue(self):
        value = valid_envelope()
        value["state_integrity"]["status"] = "STATE_UNRESOLVED"
        value["state_integrity"]["unresolved"] = ["LINEAGE_UNKNOWN"]
        with self.assertRaisesRegex(
            ContractError,
            "CONTINUE_WITH_UPSTREAM_BLOCKER",
        ):
            validate_envelope(value)

    def test_applicable_evidence_cannot_claim_unknown_provenance(self):
        value = valid_envelope()
        value["evidence"]["provenance_state"] = "UNKNOWN"
        with self.assertRaisesRegex(
            ContractError,
            "APPLICABLE_REQUIRES_ESTABLISHED_PROVENANCE",
        ):
            validate_envelope(value)

    def test_applicable_evidence_requires_applicable_substate(self):
        value = valid_envelope()
        value["evidence"]["applicability_state"] = "UNKNOWN"
        with self.assertRaisesRegex(
            ContractError,
            "APPLICABLE_REQUIRES_APPLICABILITY",
        ):
            validate_envelope(value)

    def test_applicable_evidence_cannot_claim_unknown_dependencies(self):
        value = valid_envelope()
        value["evidence"]["dependency_state"] = "UNKNOWN"
        with self.assertRaisesRegex(
            ContractError,
            "APPLICABLE_REQUIRES_RESOLVED_DEPENDENCIES",
        ):
            validate_envelope(value)

    def test_applicable_evidence_cannot_hide_missing_evidence(self):
        value = valid_envelope()
        value["evidence"]["missing_evidence"] = ["SOURCE_PROVENANCE"]
        with self.assertRaisesRegex(
            ContractError,
            "APPLICABLE_REQUIRES_NO_MISSING_EVIDENCE",
        ):
            validate_envelope(value)

    def test_applicable_evidence_cannot_hide_material_drift(self):
        value = valid_envelope()
        value["evidence"]["drift_state"] = "MATERIAL_DRIFT"
        with self.assertRaisesRegex(
            ContractError,
            "APPLICABLE_REQUIRES_NO_DRIFT",
        ):
            validate_envelope(value)

    def test_applicable_evidence_requires_nonempty_evidence_set(self):
        value = valid_envelope()
        value["evidence"]["evidence_set"] = []
        with self.assertRaisesRegex(
            ContractError,
            "APPLICABLE_REQUIRES_EVIDENCE_RECORD",
        ):
            validate_envelope(value)

    def test_applicable_evidence_requires_current_records(self):
        value = valid_envelope()
        value["evidence"]["evidence_set"][0]["validity"] = "STALE"
        with self.assertRaisesRegex(
            ContractError,
            "APPLICABLE_REQUIRES_CURRENT_RECORDS",
        ):
            validate_envelope(value)

    def test_applicable_evidence_requires_matching_scope(self):
        value = valid_envelope()
        value["evidence"]["evidence_set"][0]["scope_status"] = "UNKNOWN"
        with self.assertRaisesRegex(
            ContractError,
            "APPLICABLE_REQUIRES_SCOPE_MATCH",
        ):
            validate_envelope(value)

    def test_applicable_evidence_requires_failure_domain_resolution(self):
        value = valid_envelope()
        value["evidence"]["evidence_set"][0]["failure_domain_id"] = None
        with self.assertRaisesRegex(
            ContractError,
            "APPLICABLE_REQUIRES_FAILURE_DOMAIN",
        ):
            validate_envelope(value)

    def test_evidence_unknown_cannot_continue(self):
        value = valid_envelope()
        value["evidence"]["status"] = "EVIDENCE_UNKNOWN"
        value["evidence"]["applicability_state"] = "UNKNOWN"
        value["evidence"]["missing_evidence"] = ["CURRENT_SCOPE_SUPPORT"]
        with self.assertRaisesRegex(
            ContractError,
            "CONTINUE_WITH_UPSTREAM_BLOCKER",
        ):
            validate_envelope(value)

    def test_continuity_does_not_imply_permission(self):
        value = valid_envelope()
        value["authority"]["state"] = "NOT_ESTABLISHED"
        value["cfc"]["authority_state"] = "NOT_ESTABLISHED"
        with self.assertRaisesRegex(
            ContractError,
            "CONTINUE_WITH_UPSTREAM_BLOCKER",
        ):
            validate_envelope(value)

    def test_hold_preserves_upstream_unknowns_without_upgrade(self):
        value = valid_envelope()
        value["evidence"]["status"] = "EVIDENCE_UNKNOWN"
        value["evidence"]["provenance_state"] = "UNKNOWN"
        value["evidence"]["applicability_state"] = "UNKNOWN"
        value["evidence"]["dependency_state"] = "UNKNOWN"
        value["evidence"]["missing_evidence"] = ["SOURCE_PROVENANCE"]
        value["continuity"]["status"] = "CONTINUITY_UNKNOWN"
        value["continuity"]["reproducibility_state"] = "UNKNOWN"
        value["continuity"]["threshold_state"] = "UNKNOWN"
        value["continuity"]["unresolved"] = ["TRANSITION_NOT_ESTABLISHED"]
        value["authority"]["state"] = "UNKNOWN"
        value["cfc"] = {
            "decision": "HOLD",
            "authority_state": "UNKNOWN",
            "blockers": [
                "SOURCE_PROVENANCE",
                "TRANSITION_NOT_ESTABLISHED",
            ],
            "reason": "upstream state unresolved",
            "controller_version": "0.2.90rc1",
            "controller_identity": "frozen-anchor-0.2.90rc1",
        }

        result = validate_envelope(value)

        self.assertEqual(result["evidence"]["status"], "EVIDENCE_UNKNOWN")
        self.assertEqual(
            result["continuity"]["status"],
            "CONTINUITY_UNKNOWN",
        )
        self.assertEqual(result["authority"]["state"], "UNKNOWN")
        self.assertEqual(result["cfc"]["decision"], "HOLD")

    def test_not_run_cannot_claim_controller_identity(self):
        value = valid_envelope()
        value["cfc"] = {
            "decision": "NOT_RUN",
            "authority_state": "NOT_ASSESSED",
            "blockers": ["UPSTREAM_INVALID"],
            "reason": "controller not invoked",
            "controller_version": "0.2.90rc1",
            "controller_identity": "frozen-anchor-0.2.90rc1",
        }
        value["state_integrity"]["status"] = "STATE_INVALID"
        with self.assertRaisesRegex(
            ContractError,
            "NOT_RUN_MUST_NOT_CLAIM_CONTROLLER_IDENTITY",
        ):
            validate_envelope(value)

    def test_duplicate_evidence_id_is_rejected(self):
        value = valid_envelope()
        value["evidence"]["evidence_set"].append(
            copy.deepcopy(value["evidence"]["evidence_set"][0])
        )
        with self.assertRaisesRegex(
            ContractError,
            "DUPLICATE_EVIDENCE_ID",
        ):
            validate_envelope(value)

    def test_revocation_flag_and_authority_state_must_agree(self):
        value = valid_envelope()
        value["authority"]["revoked"] = True
        with self.assertRaisesRegex(
            ContractError,
            "REVOKED_FLAG_STATE_MISMATCH",
        ):
            validate_envelope(value)

    def test_execution_requires_attempt(self):
        value = valid_envelope()
        value["execution"] = {
            "attempted": False,
            "executed": True,
            "execution_status": "EXECUTED",
            "effect_handle": "effect-1",
            "idempotency_key": "idem-1",
            "pre_execution_state_id": "state-002",
            "receipt_id": "exec-1",
        }
        with self.assertRaisesRegex(
            ContractError,
            "EXECUTED_REQUIRES_ATTEMPTED",
        ):
            validate_envelope(value)

    def test_execution_requires_continue(self):
        value = valid_envelope()
        value["cfc"]["decision"] = "HOLD"
        value["cfc"]["authority_state"] = "NOT_ESTABLISHED"
        value["execution"] = {
            "attempted": True,
            "executed": True,
            "execution_status": "EXECUTED",
            "effect_handle": "effect-1",
            "idempotency_key": "idem-1",
            "pre_execution_state_id": "state-002",
            "receipt_id": "exec-1",
        }
        with self.assertRaisesRegex(
            ContractError,
            "EXECUTED_WITHOUT_CONTINUE|BLOCKING_DECISION_WAS_EXECUTED",
        ):
            validate_envelope(value)

    def test_execution_must_bind_to_current_state(self):
        value = valid_envelope()
        value["execution"] = {
            "attempted": True,
            "executed": True,
            "execution_status": "EXECUTED",
            "effect_handle": "effect-1",
            "idempotency_key": "idem-1",
            "pre_execution_state_id": "state-OLD",
            "receipt_id": "exec-1",
        }
        with self.assertRaisesRegex(
            ContractError,
            "EXECUTED_ON_WRONG_STATE",
        ):
            validate_envelope(value)

    def test_valid_execution_on_exact_current_state_passes(self):
        value = valid_envelope()
        value["execution"] = {
            "attempted": True,
            "executed": True,
            "execution_status": "EXECUTED",
            "effect_handle": "effect-1",
            "idempotency_key": "idem-1",
            "pre_execution_state_id": value["identity"]["state_id"],
            "receipt_id": "exec-1",
        }
        result = validate_envelope(value)
        self.assertTrue(result["execution"]["executed"])


if __name__ == "__main__":
    unittest.main()
