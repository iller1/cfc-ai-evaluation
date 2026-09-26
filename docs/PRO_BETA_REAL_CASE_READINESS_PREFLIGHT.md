# Real-case readiness preflight (front-end only)

This is a fail-closed inventory of what is still missing between a human-declared, synthetic HAWM mapping and the verification of actual third-party documents. It is **not** a second controller, evidence verifier, classifier, or authorization endpoint.

## Inputs and decision boundary

`assessRealCaseReadiness(manifest)` accepts an existing `HUMAN_REVIEWED_SYNTHETIC_DEMO_V1` manifest only for display of the declared source list. It does not trust or interpret the user's/model's `full_case_authorization`, `synthetic_independence_authority`, or universe claims as actual certifications. Every response has:

- `status: REAL_CASE_NOT_CHECKED`
- `real_cfc_executed: false`
- `real_decision_authorized: false`

No code path calls the frozen CFC or creates a real-case `ALLOW` in this feature. The existing synthetic demonstrator is unchanged.

## Explicit missing upstream contracts

- Real subject/event/batch identity and decision/retrieval scope binding.
- Source authenticity/authority, provenance and failure-domain/independence attestation.
- Externally resolved completeness of the support universe; the self-declared four-slot list is not a discovery algorithm.
- Actual as-of date, validity interval and referent/batch relevance validation. `2026-09-03` is the synthetic fixture reference date only.
- Disposition of excluded records and investigation of unresolved alerts.
- Durable HAWM snapshot → CFC run binding for reporting and retries, rather than merely checking the live response snapshot ID.
- Actual non-synthetic evidence-state execution through the frozen public API after those upstream checks.

## NW-0926 example

For A and B mapped in synthetic mode, C excluded as a different batch, and D recorded as a warehouse issue, the visible preflight identifies C/D as outside the demo, notes their unresolved/excluded statuses and notes that all documents dated 24–25 Sep 2026 occur *after* the fixture's 3 Sep 2026 reference date. An AI answer that happens to be correct does not provide source attestations; an illustrative demo STOP also does not verify the actual shipment. No automatic conversion of any ordinary AI text to a CFC-verified record occurs.

## Test contract and scope

Node tests assert never-authorized output even with forged input flags, absence of review, open issues, source scope beyond 2, and timing mismatch. Python frontend contract checks separate visible readiness status. No API, schema, retention, external document parser, or frozen CFC changes. This preflight is intentionally static: complete real-case verification needs a separately reviewed server-side source/authority integration, not a browser checkbox.
