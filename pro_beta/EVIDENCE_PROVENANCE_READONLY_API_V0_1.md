# Pro Beta Evidence Provenance read-only API v0.1

Date: 2026-10-07

Status: **API CANDIDATE — NOT PRODUCTION PROMOTED**

## Endpoint

`GET /api/conversations/{conversation_id}/evidence-provenance`

The endpoint is authenticated and owner-scoped.

It accepts no evidence, provenance, dependency, identity, fingerprint or closure-authority fields from the client.

## Evaluation order

The endpoint preserves Control Stack order:

`State Integrity -> persisted Evidence Registry -> Evidence Drift -> Evidence Provenance`

If ordinary State Integrity for the current persisted HAWM snapshot is not:

`STATE_VALID`

the endpoint returns a fail-closed Layer B unresolved result and does not attempt to upgrade the evidence state.

## Server-derived inputs

After Layer A passes, the endpoint derives only from server-side persistence:

- current HAWM snapshot;
- HAWM snapshot identity;
- exact evidence-set registration for that snapshot;
- exact provenance receipts for that registration;
- exact dependency receipt when present;
- Evidence Drift assessment derived from persisted CFC-run binding.

The endpoint does not consume the current free-text conversation as evidence.

The current human-reviewed `review_manifest` is not treated as provenance authority.

## Missing-state behavior

Examples:

- no HAWM snapshot -> `EVIDENCE_UNKNOWN`;
- State Integrity not valid -> `EVIDENCE_UNKNOWN / STATE_INTEGRITY_NOT_VALID`;
- no evidence-set registration -> `EVIDENCE_UNKNOWN / EVIDENCE_SET_REGISTRATION_NOT_FOUND`;
- no dependency receipt -> dependency remains `UNKNOWN`;
- no bound CFC baseline -> drift remains `UNRESOLVED`.

No missing server record is synthesized or backfilled.

## Positive bounded state

`EVIDENCE_APPLICABLE` is possible only when all of these persisted/derived conditions hold simultaneously:

- State Integrity is `STATE_VALID` for the exact current snapshot;
- evidence-set registration is bound to that exact state;
- provenance receipts establish every registered evidence record;
- dependency receipt resolves the exact evidence set and failure-domain map;
- missing-evidence ledger is empty;
- Evidence Drift is `NO_DRIFT`.

Even then:

`authorization_effect = DOES_NOT_AUTHORIZE_CLOSURE`

## Side effects

The endpoint is read-only.

It:

- creates no HAWM snapshot;
- creates no identity receipt;
- creates no evidence registration;
- creates no provenance or dependency receipt;
- creates no CFC run;
- modifies no audit record.

Adapter boundary:

`PERSISTED_STATE_BOUND_EVIDENCE_REGISTRY_AND_DRIFT_ONLY`

Primitive boundary:

`EXPLICIT_EVIDENCE_RECORDS_BOUND_RECEIPTS_AND_DRIFT_ONLY_NO_FREE_TEXT_SOURCE_TRUTH_OR_INDEPENDENCE_INFERENCE`

## Promotion ceiling

This endpoint candidate is not production verified.

Before promotion it requires:

1. Pro Beta contract/PostgreSQL CI success;
2. read-only route auth regression success;
3. review confirming no public registry write endpoint was added;
4. narrow production port;
5. database bootstrap success with the three registry tables;
6. authenticated live negative control before any positive registration path;
7. separately governed source of positive provenance/dependency receipts;
8. append-only production verification receipt.

Frozen CFC Anchor `0.2.90rc1` remains unchanged.
