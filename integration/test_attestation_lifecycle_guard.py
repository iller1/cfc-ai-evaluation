import unittest

from attestation_lifecycle_guard import (
    ELIGIBLE,
    STOP,
    UNRESOLVED,
    apply_revalidation_result,
    commit_nonce_consumption,
    commit_replay_state,
    validate_attestation,
    validate_independence_set,
)


def context():
    return {
        "decision_time": "2026-09-13T20:17:00+01:00",
        "decision_id": "DEC-001",
        "session_id": "SESSION-A",
        "case_id": "CASE-42",
        "scope_id": "scope-A",
        "purpose_id": "independence-check",
        "resource_id": "resource-42",
        "audience_id": "pilot-host",
        "trusted_issuers": {"issuer-A", "issuer-B"},
        "max_revocation_age_seconds": 3600,
    }


def attestation(**changes):
    base = {
        "attestation_id": "ATT-A",
        "issuer_id": "issuer-A",
        "issued_at": "2026-09-13T18:00:00+01:00",
        "valid_from": "2026-09-13T18:00:00+01:00",
        "valid_to": "2026-09-13T22:00:00+01:00",
        "ttl_seconds": 14400,
        "case_id": "CASE-42",
        "scope_id": "scope-A",
        "purpose_id": "independence-check",
        "resource_id": "resource-42",
        "audience_id": "pilot-host",
        "authenticity_status": "verified",
        "revocation_status": "good",
        "revocation_checked_at": "2026-09-13T20:00:00+01:00",
        "root_id": "ROOT-A",
        "failure_domain_id": "FD-A",
        "decision_id": "DEC-001",
        "session_id": "SESSION-A",
        "nonce": "NONCE-A",
    }
    base.update(changes)
    return base


class AttestationLifecycleTests(unittest.TestCase):
    def test_T01_expired_attestation_stops(self):
        result = validate_attestation(attestation(valid_to="2026-09-13T19:00:00+01:00"), context())
        self.assertEqual(STOP, result.status)

    def test_T02_wrong_scope_stops(self):
        result = validate_attestation(attestation(scope_id="scope-B"), context())
        self.assertEqual(STOP, result.status)

    def test_T03_revoked_before_expiry_stops(self):
        result = validate_attestation(attestation(revocation_status="revoked"), context())
        self.assertEqual(STOP, result.status)

    def test_T04_replayed_nonce_stops(self):
        a = attestation(decision_id=None)
        result = validate_attestation(a, context(), consumed_nonces={"NONCE-A"})
        self.assertEqual(STOP, result.status)

    def test_T05_two_attestations_one_root_not_independent(self):
        a = attestation(attestation_id="ATT-A", root_id="ROOT-X", failure_domain_id="FD-A")
        b = attestation(
            attestation_id="ATT-B",
            issuer_id="issuer-B",
            root_id="ROOT-X",
            failure_domain_id="FD-B",
            nonce="NONCE-B",
        )
        result = validate_independence_set([a, b], context())
        self.assertEqual(STOP, result.status)

    def test_T06_valid_current_right_scope_only_becomes_eligible(self):
        result = validate_attestation(attestation(), context())
        self.assertEqual(ELIGIBLE, result.status)
        self.assertNotEqual("ALLOW", result.status)

    def test_T07_not_yet_valid_stops(self):
        result = validate_attestation(attestation(valid_from="2026-09-13T21:00:00+01:00"), context())
        self.assertEqual(STOP, result.status)

    def test_T08_wrong_audience_stops(self):
        result = validate_attestation(attestation(audience_id="other-host"), context())
        self.assertEqual(STOP, result.status)

    def test_T09_stale_revocation_status_is_unresolved(self):
        result = validate_attestation(
            attestation(revocation_checked_at="2026-09-13T18:00:00+01:00"),
            context(),
        )
        self.assertEqual(UNRESOLVED, result.status)

    def test_T10_unknown_authenticity_is_unresolved(self):
        result = validate_attestation(attestation(authenticity_status="unknown"), context())
        self.assertEqual(UNRESOLVED, result.status)

    def test_T11_known_compromised_root_stops(self):
        result = validate_attestation(attestation(), context(), compromised_roots={"ROOT-A"})
        self.assertEqual(STOP, result.status)

    def test_T12_two_distinct_roots_and_domains_can_be_eligible(self):
        a = attestation(attestation_id="ATT-A", root_id="ROOT-A", failure_domain_id="FD-A")
        b = attestation(
            attestation_id="ATT-B",
            issuer_id="issuer-B",
            root_id="ROOT-B",
            failure_domain_id="FD-B",
            nonce="NONCE-B",
        )
        result = validate_independence_set([a, b], context())
        self.assertEqual(ELIGIBLE, result.status)

    def test_T13_session_bound_nonce_is_consumed_and_then_replay_stops(self):
        c = context()
        c["decision_id"] = "DEC-OTHER"
        a = attestation(decision_id=None)
        consumed = set()
        first = validate_attestation(a, c, consumed_nonces=consumed)
        self.assertEqual(ELIGIBLE, first.status)
        commit_nonce_consumption(first, consumed)
        second = validate_attestation(a, c, consumed_nonces=consumed)
        self.assertEqual(STOP, second.status)

    def test_T14_missing_failure_domain_is_unresolved(self):
        result = validate_attestation(attestation(failure_domain_id=None), context())
        self.assertEqual(UNRESOLVED, result.status)

    def test_T15_shared_failure_domain_not_independent(self):
        a = attestation(attestation_id="ATT-A", root_id="ROOT-A", failure_domain_id="FD-X")
        b = attestation(
            attestation_id="ATT-B",
            issuer_id="issuer-B",
            root_id="ROOT-B",
            failure_domain_id="FD-X",
            nonce="NONCE-B",
        )
        result = validate_independence_set([a, b], context())
        self.assertEqual(STOP, result.status)

    def test_T16_invalid_authenticity_stops(self):
        result = validate_attestation(attestation(authenticity_status="invalid"), context())
        self.assertEqual(STOP, result.status)

    def test_T17_untrusted_issuer_stops(self):
        result = validate_attestation(attestation(issuer_id="issuer-X"), context())
        self.assertEqual(STOP, result.status)

    def test_T18_ttl_expired_stops(self):
        result = validate_attestation(attestation(ttl_seconds=60), context())
        self.assertEqual(STOP, result.status)

    def test_T19_no_decision_or_session_binding_is_unresolved_or_stop(self):
        c = context()
        c.pop("decision_id")
        a = attestation(decision_id=None, session_id=None, nonce=None)
        result = validate_attestation(a, c)
        self.assertIn(result.status, {STOP, UNRESOLVED})
        self.assertNotEqual(ELIGIBLE, result.status)

    def test_T20_failed_revalidation_removes_cached_eligibility(self):
        cache = set()
        good = validate_attestation(attestation(), context())
        self.assertEqual(ELIGIBLE, good.status)
        apply_revalidation_result(good, cache)
        self.assertIn("ATT-A", cache)

        failed = validate_attestation(attestation(revocation_status="revoked"), context())
        self.assertEqual(STOP, failed.status)
        apply_revalidation_result(failed, cache)
        self.assertNotIn("ATT-A", cache)

    def test_T21_decision_bound_replay_stops_after_commit(self):
        consumed_nonces = set()
        consumed_decisions = set()
        a = attestation()
        first = validate_attestation(a, context(), consumed_decision_ids=consumed_decisions)
        self.assertEqual(ELIGIBLE, first.status)
        commit_replay_state(first, consumed_nonces, consumed_decisions)
        second = validate_attestation(a, context(), consumed_decision_ids=consumed_decisions)
        self.assertEqual(STOP, second.status)

    def test_T22_duplicate_attestation_id_cannot_count_twice(self):
        a = attestation(attestation_id="ATT-X", root_id="ROOT-A", failure_domain_id="FD-A")
        b = attestation(
            attestation_id="ATT-X",
            issuer_id="issuer-B",
            root_id="ROOT-B",
            failure_domain_id="FD-B",
            nonce="NONCE-B",
        )
        result = validate_independence_set([a, b], context())
        self.assertEqual(STOP, result.status)

    def test_T23_wrong_case_stops(self):
        result = validate_attestation(attestation(case_id="CASE-OTHER"), context())
        self.assertEqual(STOP, result.status)


if __name__ == "__main__":
    unittest.main()
