# Pro Beta Evidence Provenance Registry v0.1

Date: 2026-10-07

Status: **INTEGRATION CANDIDATE — NOT PRODUCTION PROMOTED**

## Purpose

This registry supplies persisted, server-side Layer B records to the bounded Control Stack Evidence Provenance v0.1 primitive.

It is deliberately separate from:

- free-text HAWM evidence;
- the human-reviewed synthetic demo manifest;
- ordinary model replies;
- CFC execution;
- source authenticity claims.

## Persistence model

The registry stores three separately typed record classes for one exact HAWM snapshot:

1. `EvidenceSetRegistration`
2. `EvidenceProvenanceReceipt`
3. `EvidenceDependencyReceipt`

Every record is bound to:

- `snapshot_id`;
- `conversation_id`;
- `state_id`.

For v0.1:

`state_id == snapshot_id`

The database additionally enforces the owned snapshot/conversation relationship.

Historical HAWM snapshots are not backfilled.

## Evidence-set registration

A registration stores:

- exact snapshot/state identity;
- the explicit shared Layer B evidence record set;
- the explicit missing-evidence ledger;
- registry adapter version.

Registration requires an existing HAWM snapshot with an existing HAWM identity anchor.

A legacy snapshot without an identity anchor cannot be registered through the service.

## Provenance receipt

One provenance receipt binds:

- one exact state;
- one exact evidence ID;
- one exact source ID;
- one explicit provenance status.

A provenance receipt is rejected when its source does not match the registered evidence record.

The persistence layer allows at most one provenance receipt per evidence ID within one registered snapshot.

A source ID alone remains insufficient to establish provenance.

## Dependency receipt

One dependency receipt binds:

- one exact state;
- the represented evidence-ID set;
- its represented failure-domain map;
- one explicit dependency-resolution status.

For `RESOLVED`, the Control Stack primitive requires exact evidence-set coverage and exact failure-domain coverage/value agreement.

Different source IDs do not imply resolved dependencies or source independence.

## No public write authority

v0.1 adds no public HTTP/API endpoint that accepts:

- evidence registration;
- provenance receipt;
- dependency receipt;
- provenance authority;
- dependency authority.

The write methods exist only at the authenticated server service/persistence boundary for governed future integrations and test harnesses.

Current Pro Beta `review_manifest` remains:

`SCHEMA_ONLY_USER_DECLARATION_NOT_EVIDENCE_VERIFICATION`

It is not automatically converted into provenance receipts.

## Read-only adapter

`pro_beta/evidence_provenance_adapter.py` consumes only persisted server records and a state-bound Evidence Drift result.

The adapter rejects or blocks:

- unsupported registry/receipt versions;
- wrong snapshot/state/conversation bindings;
- provenance receipt reuse across states;
- dependency receipt reuse across states;
- drift results for a different current snapshot.

It performs no persistence and does not execute CFC.

Adapter boundary:

`PERSISTED_STATE_BOUND_EVIDENCE_REGISTRY_AND_DRIFT_ONLY`

Every outcome preserves:

`DOES_NOT_AUTHORIZE_CLOSURE`

## Database contract

New tables:

- `evidence_set_registrations`;
- `evidence_provenance_receipts`;
- `evidence_dependency_receipts`.

Database bootstrap treats all three as required once this integration candidate is promoted to a production branch.

The tables are not yet deployed to production by this main-branch candidate.

## Promotion ceiling

This integration candidate establishes storage, ownership, state binding and read-only adapter semantics only.

Before production promotion:

1. full Pro Beta CI and PostgreSQL integration must pass;
2. no public client write authority may be introduced accidentally;
3. an authenticated read-only API assessment path must be separately reviewed;
4. a controlled source of governed provenance/dependency receipts must be defined;
5. live production must demonstrate fail-closed behavior before any positive receipt path is trusted;
6. frozen CFC Anchor `0.2.90rc1` remains unchanged.
