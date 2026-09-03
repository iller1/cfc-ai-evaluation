# CASE_03 — Active polarity conflict / no resolution

The model conclusion is `DemoSubject is safe.` Two current trusted records address that exact proposition: one positive and one negative. No relation-resolution certificate is installed.

The frozen controller returns `QUARANTINED`, reason `direct contradiction`, records a `POLARITY_CONFLICT` over `E1` and `E2`, and does not allow closure.

Synthetic case-scoped host attestations/verifiers are demonstration infrastructure only. No production IAM/crypto/external-validation claim is made.

Production exclusions: no `cfc_anchor._engine`, no `cfc_anchor.testing`, no private `Controller` method, and no reimplementation of closure rules.
