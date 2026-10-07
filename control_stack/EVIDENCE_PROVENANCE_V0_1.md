# Evidence Provenance v0.1

Date: 2026-10-07

Status: **IMPLEMENTATION CANDIDATE — NOT PRODUCTION PROMOTED**

## Purpose

Evidence Provenance v0.1 is the first bounded Control Stack Layer B primitive beyond Evidence Drift.

It determines whether an explicitly represented evidence set is structurally coherent enough to occupy one of the shared Control Stack evidence states.

It does **not** discover evidence from free text and does **not** authenticate real-world source truth.

Boundary:

`EXPLICIT_EVIDENCE_RECORDS_BOUND_RECEIPTS_AND_DRIFT_ONLY_NO_FREE_TEXT_SOURCE_TRUTH_OR_INDEPENDENCE_INFERENCE`

Authorization boundary:

`DOES_NOT_AUTHORIZE_CLOSURE`

## Inputs

The primitive receives:

- exact current `state_id`;
- explicit `evidence_set`;
- explicit provenance receipts;
- one explicit dependency-resolution receipt or no receipt;
- explicit `missing_evidence` ledger;
- explicit Evidence Drift state.

Each evidence record uses the shared v0.1 fields:

- `evidence_id`;
- `source_id`;
- `validity`;
- `scope_status`;
- `failure_domain_id`.

## Provenance rule

A `source_id` is not provenance by itself.

For `provenance_state = ESTABLISHED`, every evidence record must have exactly one explicit provenance receipt bound to:

- the current `state_id`;
- the same `evidence_id`;
- the same `source_id`;
- status `ESTABLISHED`.

A receipt from another state, another evidence record or another source fails closed.

This primitive validates receipt binding only.

It does not establish that the receipt issuer is trustworthy or that the underlying source is factually correct.

## Dependency rule

Different `source_id` values do not establish independence.

For `dependency_state = RESOLVED`, the dependency receipt must:

- be bound to the exact current `state_id`;
- cover the exact current evidence-ID set;
- cover every evidence record with a non-empty failure-domain value;
- reproduce the exact failure-domain mapping represented by the evidence records;
- explicitly carry status `RESOLVED`.

A resolved dependency representation is not the same as a claim that all sources are independent.

Independence remains a separate CFC/control concern.

## Applicability rule

The record-level applicability state is deterministic:

- any `INVALID` validity -> `INVALID`;
- any `UNKNOWN` validity/scope -> `UNKNOWN`;
- any `STALE` validity or `WRONG` scope -> `NOT_APPLICABLE`;
- any `PARTIAL` scope -> `PARTIAL`;
- otherwise all records are `CURRENT / MATCH` -> `APPLICABLE`.

## Overall states

### `EVIDENCE_APPLICABLE`

Returned only when all of the following are true:

- evidence set is non-empty;
- provenance is `ESTABLISHED`;
- applicability is `APPLICABLE`;
- dependency state is `RESOLVED`;
- missing-evidence ledger is empty;
- drift state is `NO_DRIFT`.

Effect:

`NO_ADDITIONAL_BLOCK_FROM_EVIDENCE_PROVENANCE_ONLY`

This does not authorize closure.

### `EVIDENCE_PARTIAL`

Used for known incomplete or currently non-applicable states, including:

- partial provenance;
- stale or wrong-scope evidence;
- partial/conflicting dependency representation;
- explicit missing evidence;
- material drift requiring re-evaluation.

Effect:

`BLOCK_EVIDENCE_PROPAGATION_REVIEW_REQUIRED`

### `EVIDENCE_UNKNOWN`

Used when a required Layer B fact remains unresolved, including:

- source IDs without provenance receipts;
- no dependency receipt;
- unknown record validity/scope;
- unresolved/not-assessed drift;
- empty evidence set.

Effect:

`BLOCK_EVIDENCE_PROPAGATION_REVIEW_REQUIRED`

### `EVIDENCE_INVALID`

Used for explicit structural/binding contradictions, including:

- duplicate evidence IDs;
- malformed records/receipts;
- provenance receipt state/evidence/source mismatch;
- multiple provenance receipts for one evidence record;
- dependency receipt state/coverage mismatch;
- resolved failure-domain mapping mismatch;
- invalid evidence record state.

Effect:

`BLOCK_EVIDENCE_PROPAGATION_REVIEW_REQUIRED`

## No semantic laundering

The result exposes a shared-schema-compatible `evidence` object.

`EVIDENCE_APPLICABLE` is never emitted merely because:

- evidence exists;
- source IDs are distinct;
- the user declared sources independent;
- a source is current;
- a scope matches;
- a previous CFC run succeeded.

The v0.1 strong state requires all declared Layer B prerequisites simultaneously.

## Relationship to Evidence Drift

Evidence Drift v0.1 remains a separate bounded submodule.

Evidence Provenance v0.1 consumes the explicit drift result as one input.

`MATERIAL_DRIFT`, `UNRESOLVED` or `NOT_ASSESSED` cannot be laundered into `EVIDENCE_APPLICABLE`.

## Relationship to current Pro Beta HAWM

Current Pro Beta `cfc_structured.evidence` does not contain the full shared Layer B record contract and current human-reviewed source mapping is explicitly:

`SCHEMA_ONLY_USER_DECLARATION_NOT_EVIDENCE_VERIFICATION`

Therefore v0.1 must **not** be wired directly to current HAWM source declarations as though they were provenance receipts.

A future adapter must supply independently governed, state-bound provenance/dependency records.

## Acceptance matrix

The implementation tests at least:

- complete explicit state -> `EVIDENCE_APPLICABLE`;
- source IDs without provenance receipts -> `EVIDENCE_UNKNOWN`;
- distinct source IDs without dependency receipt -> `EVIDENCE_UNKNOWN`;
- wrong-state provenance receipt -> `EVIDENCE_INVALID`;
- wrong-source provenance receipt -> `EVIDENCE_INVALID`;
- duplicate provenance receipt -> `EVIDENCE_INVALID`;
- stale evidence -> `EVIDENCE_PARTIAL`;
- wrong scope -> `EVIDENCE_PARTIAL`;
- unknown record state -> `EVIDENCE_UNKNOWN`;
- invalid record state -> `EVIDENCE_INVALID`;
- explicit missing evidence -> `EVIDENCE_PARTIAL`;
- material drift -> `EVIDENCE_PARTIAL`;
- unresolved/not-assessed drift -> `EVIDENCE_UNKNOWN`;
- dependency conflict -> `EVIDENCE_PARTIAL`;
- resolved dependency coverage mismatch -> `EVIDENCE_INVALID`;
- failure-domain mapping mismatch -> `EVIDENCE_INVALID`;
- duplicate evidence ID -> `EVIDENCE_INVALID`;
- empty evidence set -> `EVIDENCE_UNKNOWN`.

## Promotion ceiling

This implementation candidate proves only deterministic handling of explicitly represented evidence/provenance/dependency state.

Before production promotion it requires:

1. dedicated CI and shared schema regression;
2. explicit adapter design for persisted provenance/dependency records;
3. server-side ownership and exact-state binding;
4. no client-supplied receipt authority;
5. authenticated production positive and fail-closed controls;
6. an append-only production verification receipt;
7. no frozen CFC changes.
