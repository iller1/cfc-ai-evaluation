# Evidence Drift v0.1 — bounded host-side contract

## Status

**IMPLEMENTATION CANDIDATE — NOT YET PRODUCTION PROMOTED**

This module is a host/application-layer extension over persisted HAWM snapshots.

It does **not** modify or reinterpret:

- frozen CFC Anchor `0.2.90rc1`;
- Operator Wrapper v1.23;
- frozen CFC closure semantics;
- ordinary model replies;
- free-text HAWM fields as verified evidence.

## Purpose

Evidence Drift answers one narrow question:

> Has the explicit CFC-relevant structured HAWM state changed since the snapshot that formed the comparison baseline?

The immediate use case is:

`run-bound HAWM snapshot → later HAWM snapshot → deterministic drift assessment`

A material or unresolved change must prevent silent carry-forward of an earlier closure until re-evaluation occurs.

## Input boundary

v0.1 compares only:

`HAWMSnapshot.state["cfc_structured"]`

It does not infer evidence semantics from:

- free-text `goal`;
- free-text `claims`;
- free-text `evidence`;
- ordinary model replies;
- natural-language conversation history.

Boundary label:

`STRUCTURED_HAWM_CFC_STATE_ONLY_NO_FREE_TEXT_EVIDENCE_INFERENCE`

## Output states

### `NO_DRIFT`

The canonical structured state is unchanged.

Effect:

`NO_ADDITIONAL_BLOCK_FROM_DRIFT_ONLY`

This is **not** an authorization to close or act. It means only that this drift layer found no additional drift blocker.

### `MATERIAL_DRIFT`

The canonical structured state changed.

Effect:

`BLOCK_CARRY_FORWARD_REEVALUATION_REQUIRED`

An earlier closure must not be silently inherited as current.

### `UNRESOLVED`

A trustworthy comparison cannot be completed.

Examples:

- missing structured baseline;
- missing structured current state;
- malformed structured state;
- cross-conversation comparison;
- same immutable snapshot ID with different structured content.

Effect:

`BLOCK_CARRY_FORWARD_REEVALUATION_REQUIRED`

## Canonical comparison

The complete explicit `cfc_structured` object is canonicalized.

Dictionary key order is ignored.

The `cfc_structured.evidence` collection is treated as order-insensitive so that reordering identical evidence records alone does not create drift.

Any substantive difference in the structured object is material, including present or future structured fields.

Current examples include changes to:

- conclusion;
- required independent support count;
- provenance shape;
- independence authority;
- scope;
- evidence membership;
- evidence polarity;
- evidence validity.

Both structured states receive deterministic SHA-256 fingerprints.

## Snapshot identity invariant

HAWM snapshots are treated as immutable.

If two supplied snapshots have the same `snapshot_id` but different canonical structured fingerprints, the result is:

`UNRESOLVED / SNAPSHOT_ID_CONTENT_MISMATCH`

This is fail-closed.

## Carry-forward rule

The module never returns `ALLOW`.

It emits:

`authorization_effect = DOES_NOT_AUTHORIZE_CLOSURE`

Only `NO_DRIFT` avoids adding a new drift blocker.

Both `MATERIAL_DRIFT` and `UNRESOLVED` require re-evaluation before inherited closure can be treated as current.

## Acceptance matrix

| Case | Expected |
| --- | --- |
| Same structured state, new snapshot ID | `NO_DRIFT` |
| Free-text-only change | `NO_DRIFT` within v0.1 boundary |
| Evidence CURRENT → STALE | `MATERIAL_DRIFT` |
| Evidence removed | `MATERIAL_DRIFT` |
| Scope changes | `MATERIAL_DRIFT` |
| Required support count changes | `MATERIAL_DRIFT` |
| Evidence records only reordered | `NO_DRIFT` |
| Structured baseline missing | `UNRESOLVED` |
| Current structured state missing | `UNRESOLVED` |
| Same snapshot ID, changed content | `UNRESOLVED` |
| Different conversation IDs | `UNRESOLVED` |

## Relationship to durable snapshot→run binding

The production-verified durable binding supplies the missing historical anchor:

`CFC run → exact persisted HAWM snapshot ID`

Evidence Drift can therefore compare that exact execution input with a later HAWM snapshot without guessing which state belonged to the run.

This module does not itself select a CFC run or latest snapshot yet. v0.1 is intentionally a deterministic comparison primitive first.

## Promotion gate

Before production promotion:

1. unit acceptance matrix must pass;
2. existing Pro Beta regression must remain green;
3. an API/service integration must resolve the baseline only from persisted run binding, never from "latest";
4. material drift must be demonstrated in an authenticated end-to-end sequence;
5. no frozen CFC artifact may change.
