from __future__ import annotations

import copy
import unittest

from pro_beta.api import APIError, ProBetaAPI
from pro_beta.auth_boundary import AuthBoundary, VerifiedExternalIdentity
from pro_beta.contracts import UserAccount
from pro_beta.persistence import InMemoryPersistence
from pro_beta.service import ProBetaService


ISSUER = "https://identity.example/"
AUDIENCE = "cfc-hawm-pro-beta"


class FakeVerifier:
    def verify(self, credential: str) -> VerifiedExternalIdentity:
        subjects = {
            "token-a": "provider|exec-a",
            "token-b": "provider|exec-b",
        }
        if credential not in subjects:
            raise RuntimeError("unexpected credential")
        return VerifiedExternalIdentity(
            subject=subjects[credential],
            issuer=ISSUER,
            audience=AUDIENCE,
            provider_verified=True,
        )


class ExecutionGateAPITests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryPersistence()
        self.account_a = UserAccount(
            "usr-exec-a", "provider|exec-a", "a@example.com"
        )
        self.account_b = UserAccount(
            "usr-exec-b", "provider|exec-b", "b@example.com"
        )
        self.store.create_user(self.account_a)
        self.store.create_user(self.account_b)
        self.service = ProBetaService(self.store)

        boundary = AuthBoundary(
            self.store,
            expected_issuer=ISSUER,
            expected_audience=AUDIENCE,
        )
        self.api = ProBetaAPI(
            verifier=FakeVerifier(),
            auth_boundary=boundary,
            service=self.service,
        )

        self.workspace_a = self.api.create_workspace(
            "token-a", {"name": "Execution A"}
        )
        self.conversation_a = self.api.create_conversation(
            "token-a",
            self.workspace_a["workspace_id"],
            {"title": "Execution A"},
        )
        self.workspace_b = self.api.create_workspace(
            "token-b", {"name": "Execution B"}
        )
        self.api.create_conversation(
            "token-b",
            self.workspace_b["workspace_id"],
            {"title": "Execution B"},
        )

    def _auth_a(self):
        return self.api._auth("token-a")

    def _save_snapshot(self, value=1):
        return self.api.save_hawm_snapshot(
            "token-a",
            self.conversation_a["conversation_id"],
            {
                "state": {"goal": "execution", "value": value},
                "last_verified_state": "USER_WORKING_STATE",
            },
        )

    def _bound_run(self, snapshot_id):
        return self.service.save_cfc_run(
            self._auth_a(),
            self.conversation_a["conversation_id"],
            case_id="EXECUTION_PREFLIGHT_BINDING_ONLY",
            controller_anchor="0.2.90rc1",
            controller_result={"control_closure": False},
            presentation={"decision": "STOP"},
            hawm_snapshot_id=snapshot_id,
        )

    def _intent(self, snapshot_id):
        run = self._bound_run(snapshot_id)
        return self.service.register_execution_intent(
            self._auth_a(),
            self.conversation_a["conversation_id"],
            action_id="action-1",
            controller_run_id=run.run_id,
            action_payload={"operation": "synthetic"},
            idempotency_key="idem-1",
            receipt_id="receipt-1",
        )

    def test_no_intent_after_valid_state_integrity_is_unresolved(self):
        snap = self._save_snapshot()

        result = self.api.assess_execution_preflight(
            "token-a",
            self.conversation_a["conversation_id"],
        )

        self.assertEqual(
            result["preflight_status"],
            "PREFLIGHT_UNRESOLVED",
        )
        self.assertEqual(
            result["reason"],
            "EXECUTION_INTENT_NOT_REGISTERED",
        )
        self.assertEqual(result["current_state_id"], snap["snapshot_id"])
        self.assertEqual(
            result["state_integrity_status"],
            "STATE_VALID",
        )
        self.assertFalse(result["execution"]["attempted"])
        self.assertFalse(result["execution"]["executed"])
        self.assertTrue(result["read_only"])
        self.assertEqual(result["persistence_actions"], [])
        self.assertFalse(result["cfc_executed"])
        self.assertEqual(
            result["authority_effect"],
            "DOES_NOT_CREATE_AUTHORITY",
        )
        self.assertEqual(result["prior_execution_receipt_count"], 0)

    def test_no_intent_reports_existing_receipt_count(self):
        from pro_beta.contracts import ExecutionReceiptRecord

        self._save_snapshot()
        orphan = ExecutionReceiptRecord(
            receipt_id="orphan-receipt",
            intent_id="missing-intent",
            conversation_id=self.conversation_a["conversation_id"],
            action_id="orphan-action",
            controller_run_id="orphan-run",
            state_id="orphan-state",
            state_version="f" * 64,
            idempotency_key="orphan-idem",
            execution_status="OUTCOME_UNKNOWN",
            attempted=True,
            executed=None,
            effect_handle=None,
            adapter_version="EXECUTION_GATE_REGISTRY_ADAPTER_V0_1",
        )
        # Synthetic invalid state; not a permitted production database state.
        self.store.execution_receipts[orphan.receipt_id] = orphan
        before = copy.deepcopy(self.store.execution_receipts)
        result = self.api.assess_execution_preflight(
            "token-a", self.conversation_a["conversation_id"]
        )
        self.assertEqual(result["reason"], "EXECUTION_INTENT_NOT_REGISTERED")
        self.assertEqual(result["prior_execution_receipt_count"], 1)
        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertFalse(result["execution"]["attempted"])
        self.assertFalse(result["execution"]["executed"])
        self.assertEqual(self.store.execution_receipts, before)

    def test_exact_intent_is_blocked_by_real_authority_hold(self):
        snap = self._save_snapshot()
        intent = self._intent(snap["snapshot_id"])

        before = {
            "snapshots": copy.deepcopy(self.store.hawm_snapshots),
            "identities": copy.deepcopy(self.store.hawm_snapshot_identities),
            "runs": copy.deepcopy(self.store.cfc_runs),
            "intents": copy.deepcopy(self.store.execution_intents),
            "receipts": copy.deepcopy(self.store.execution_receipts),
        }

        result = self.api.assess_execution_preflight(
            "token-a",
            self.conversation_a["conversation_id"],
        )

        self.assertEqual(result["preflight_status"], "PREFLIGHT_BLOCKED")
        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertEqual(result["intent_id"], intent.intent_id)
        self.assertEqual(
            result["authority_status"],
            "HOLD_REAL_EXECUTION_AUTHORITY_UNAVAILABLE",
        )
        self.assertEqual(result["authority_source"], "NONE")
        self.assertEqual(result["controller_decision"], "NOT_RUN")
        self.assertIn(
            "CFC_AUTHORITY_NOT_ESTABLISHED",
            result["blockers"],
        )
        self.assertFalse(result["execution"]["attempted"])
        self.assertFalse(result["execution"]["executed"])

        self.assertEqual(self.store.hawm_snapshots, before["snapshots"])
        self.assertEqual(
            self.store.hawm_snapshot_identities,
            before["identities"],
        )
        self.assertEqual(self.store.cfc_runs, before["runs"])
        self.assertEqual(self.store.execution_intents, before["intents"])
        self.assertEqual(self.store.execution_receipts, before["receipts"])

    def test_newer_snapshot_makes_old_intent_stale(self):
        first = self._save_snapshot(value=1)
        self._intent(first["snapshot_id"])
        second = self._save_snapshot(value=2)

        result = self.api.assess_execution_preflight(
            "token-a",
            self.conversation_a["conversation_id"],
        )

        self.assertEqual(result["gate_status"], "EXECUTION_BLOCKED")
        self.assertEqual(result["current_state_id"], second["snapshot_id"])
        self.assertIn(
            "PRE_EXECUTION_STATE_ID_MISMATCH",
            result["blockers"],
        )
        self.assertIn(
            "PRE_EXECUTION_STATE_VERSION_MISMATCH",
            result["blockers"],
        )
        self.assertFalse(result["execution"]["attempted"])

    def test_cross_user_preflight_is_forbidden(self):
        self._save_snapshot()

        with self.assertRaises(APIError) as ctx:
            self.api.assess_execution_preflight(
                "token-b",
                self.conversation_a["conversation_id"],
            )

        self.assertEqual(ctx.exception.status, 403)


if __name__ == "__main__":
    unittest.main(verbosity=2)
