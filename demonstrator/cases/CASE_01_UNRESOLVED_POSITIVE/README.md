# CASE_01 — Unresolved current state / definite positive conclusion

Fixture revision **0.2**. This supersedes CASE_01 v0.1.

The model conclusion is `DemoSubject is safe.` A trusted record for the same proposition exists, but its `observed_at` and `available_at` are `2026-12-01` while the evaluation date is `2026-09-03`. The frozen controller therefore cannot use it as current epistemic support.

The required result is a **full audit-shaped** public API result, not an early integration/context stop. The reference execution contains full audit fields including `accepted_evidence`, `critical_unresolved`, `claim_support_policy_violations`, and the complete gate map.

Synthetic case-scoped host attestations/verifiers are demonstration infrastructure only. No production IAM/crypto/external-validation claim is made.

Production exclusions: no `cfc_anchor._engine`, no `cfc_anchor.testing`, no private `Controller` method, and no reimplementation of closure rules.
