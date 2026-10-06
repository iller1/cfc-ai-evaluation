# CFC Control Stack Architecture v0.1

Date: 2026-10-06  
Status: **NORMATIVE ARCHITECTURE CANDIDATE**

## 1. Purpose

CFC Control Stack is a layered control architecture around the frozen CFC controller.

The architecture must preserve one central separation:

> factual validity, representational validity, continuity and technical possibility do not by themselves establish current authority to propagate a conclusion into a consequential action.

The frozen CFC Core remains the authority/closure gate. New capabilities are implemented as separate modules before or after it.

## 2. Top-level flow

`STATE INTEGRITY`
→ `EVIDENCE / PROVENANCE`
→ `CONTINUITY / TRANSITION`
→ `FROZEN CFC CORE`
→ `EXECUTION GATE`
→ `AUDIT / INFORMATION PASSPORT`

A downstream layer may consume an upstream result.

It may not silently upgrade it.

## 3. Global rules

### 3.1 Fail closed

If a layer cannot establish a required fact, it must return an explicit unresolved/unknown/hold state.

Missing information is not completed by inference.

### 3.2 No semantic laundering

A transformation, adapter, serializer or UI mapping must not convert:

- `UNKNOWN -> VALID`;
- `PARTIAL -> SUFFICIENT`;
- `HOLD -> CONTINUE`;
- `UNVERIFIED -> AUTHORIZED`;
- `CONTINUITY_ESTABLISHED -> PERMISSION`;

unless a separately represented, versioned and testable control step explicitly establishes the new state.

### 3.3 Historical immutability

A later module/version does not rewrite historical receipts.

Supersession creates a new state/receipt and preserves the old one.

### 3.4 Explicit authority boundary

Only the frozen CFC Core decides whether the represented current state satisfies the controller's authority/closure conditions.

Pre-core modules prepare and constrain the input.

Post-core modules enforce and record the decision.

### 3.5 Exact-state binding

Any execution or audit claim that refers to a controller run must identify the exact state/snapshot used for that run.

"Latest state" is not a substitute for historical execution input.

## 4. Layer A — State Integrity

### Responsibility

Establish that the system is operating on the intended case, arm, context, state version and snapshot lineage.

### Minimum inputs

- case identity;
- arm/context identity where applicable;
- snapshot/state identity;
- predecessor/lineage information;
- version identity;
- immutable state fingerprint.

### Minimum outputs

- `state_id`;
- `snapshot_id`;
- `lineage_status`;
- `binding_status`;
- `state_fingerprint`;
- `unresolved[]`;
- one of:
  - `STATE_VALID`;
  - `STATE_UNRESOLVED`;
  - `STATE_INVALID`.

### Must detect

- cross-case substitution;
- cross-arm substitution;
- stale snapshot use;
- broken lineage;
- same immutable ID with different content;
- reconstructed state presented as original without a valid provenance link.

### Forbidden upgrade

State Integrity may not infer semantic evidence validity or decision authority.

## 5. Layer B — Evidence & Provenance

### Responsibility

Represent where evidence came from, whether it applies now, whether dependencies/common-mode relationships exist, what is missing and whether the evidence state materially changed.

### Minimum inputs

- state identity from Layer A;
- evidence records;
- source identity;
- provenance/dependency relations;
- temporal applicability;
- scope/purpose/resource/audience;
- explicit missing-evidence ledger.

### Minimum outputs

- `evidence_set`;
- `provenance_state`;
- `applicability_state`;
- `dependency_state`;
- `missing_evidence[]`;
- `drift_state`;
- one of:
  - `EVIDENCE_APPLICABLE`;
  - `EVIDENCE_PARTIAL`;
  - `EVIDENCE_UNKNOWN`;
  - `EVIDENCE_INVALID`.

### Existing v0.1 submodule

Evidence Drift v0.1 is incorporated as a bounded submodule.

It compares explicit CFC-relevant structured state with the exact run-bound historical HAWM baseline.

### Forbidden upgrade

Presence of evidence does not imply sufficiency.

Evidence applicability does not imply current authority.

Two source records do not become independent merely because they have different IDs.

## 6. Layer C — Continuity & Transition

### Responsibility

Represent how the current state relates to the previous state without treating continuity as permission.

### Minimum inputs

- previous and current state identities;
- transition metadata;
- explicit unresolved/hold markers;
- threshold/envelope state;
- reproducibility state;
- evaluation provenance.

### Minimum outputs

- `continuity_state`;
- `transition_type`;
- `reproducibility_state`;
- `threshold_state`;
- `unresolved[]`;
- one of:
  - `CONTINUITY_ESTABLISHED`;
  - `CONTINUITY_DEGRADED`;
  - `CONTINUITY_UNKNOWN`.

### Existing v0.1 submodule

State Monitor v0.1 is incorporated as the first transition invariant.

It detects:

`unresolved present -> unresolved absent`

without exact-current-snapshot CFC evaluation and blocks silent carry-forward.

### Forbidden upgrade

Continuity and reproducibility must not be converted into action authority.

## 7. Layer D — Frozen CFC Core

### Responsibility

Make the bounded control decision over the explicit current state supplied through the adapter.

### Frozen baseline

`CFC Anchor 0.2.90rc1`

### Outputs

At the Control Stack architecture level, the adapter exposes:

- decision;
- authority/closure state;
- blockers;
- reason;
- controller version/identity;
- replay/integrity evidence where available.

The architecture may normalize presentation labels such as:

- `CONTINUE`;
- `HOLD`;
- `STOP`;
- `ESCALATE`;

but must preserve the exact underlying frozen controller result.

### Forbidden behavior

The CFC Core is not responsible for repairing or inferring missing upstream semantics.

The Control Stack development line does not edit its bytes.

## 8. Layer E — Execution Gate

### Responsibility

Enforce the controller result at the action boundary.

A model or workflow may propose an action.

The Execution Gate decides whether the action can actually be attempted under the current exact state and authority.

### Required checks

- current controller decision;
- pre-execution state/version recheck;
- optimistic concurrency/version match;
- idempotency/replay protection;
- human escalation where required;
- transactional boundary where supported.

### Minimum outputs

- `attempted`;
- `executed`;
- `execution_status`;
- `effect_handle`;
- `idempotency_key`;
- `pre_execution_state_id`;
- `receipt_id`;
- blockers/reason.

### Forbidden behavior

`attempted` must never be reported as `executed`.

A `HOLD` or `STOP` may not be bypassed through an alternate execution path.

A stale controller result may not authorize execution after a material state change.

## 9. Layer F — Audit & Information Passport

### Responsibility

Preserve the decision context and receipts across layers and systems.

### Minimum contents

- claim;
- evidence references;
- scope;
- time;
- actor;
- exact state/snapshot identity;
- authority state;
- controller decision/reason/blockers;
- unresolved set;
- component versions;
- hashes/fingerprints;
- lineage/supersession;
- execution outcome;
- portable receipts.

### Core rule

The Passport records what was:

- proposed;
- checked;
- authorized;
- attempted;
- executed;

as separate states.

It must not collapse them.

## 10. Inter-layer contract

| Producer | Minimum contract | Consumer must not |
| --- | --- | --- |
| State Integrity | identity, lineage, binding, unresolved | infer missing identity or convert unknown to valid |
| Evidence & Provenance | evidence set, provenance, applicability, dependencies, gaps | equate evidence presence with authority |
| Continuity & Transition | transition, continuity, reproducibility, thresholds | equate continuity with permission |
| Frozen CFC Core | exact decision, authority/closure state, blockers, reason | be reinterpreted by Execution Gate |
| Execution Gate | attempted/executed distinction, effect receipt | report proposal/attempt as execution |
| Audit / Passport | immutable/versioned receipts and lineage | rewrite historical state after supersession |

## 11. Adapter rule

Domain adapters and the CFC Core Adapter are translators, not decision-makers.

An adapter may:

- map domain fields into a declared common schema;
- reject malformed/ambiguous input;
- preserve explicit unknowns;
- attach versioned transformation receipts.

An adapter may not:

- generate evidence;
- generate source independence;
- generate current authority;
- repair scope;
- infer a missing binding;
- convert free text into verified structured facts without an explicit, separately governed extraction/review step.

## 12. Domain isolation

The frozen CFC Core should not encode domain-specific medicine, law, finance or business semantics.

Those belong in versioned domain adapters.

The common architecture asks one invariant question:

> Given the explicitly represented current state, evidence, scope and authority conditions, may this state propagate to the proposed next effect?

## 13. Cross-layer acceptance tests

The first full-stack release must include at least:

### T1 — State substitution

Correct-looking state from the wrong case/arm/snapshot.

Expected: fail closed.

### T2 — Stale evidence

Evidence remains historically valid but is stale or outside current applicability.

Expected: revalidation / HOLD.

### T3 — Continuity without authority

Continuity and reproducibility are established, but current scope-bound authority is not.

Expected: no inherited permission.

### T4 — Authority without evidence sufficiency

Formal role/approval exists, but evidence applicability is unresolved.

Expected: no closure.

### T5 — Good evidence, expired/revoked authority envelope

Content may remain correct, but authority is no longer active.

Expected: HOLD/STOP.

### T6 — Concurrent state change

State changes after check and before execution.

Expected: version mismatch, re-check, no execution.

### T7 — Audit replay

Same frozen input and same component versions.

Expected: same decision context and deterministic control result.

## 14. Release discipline

Each component has its own:

- semantic version;
- changelog;
- tests;
- hash/fingerprint where applicable;
- claim ceiling;
- verification receipt.

The full stack release manifest records all component versions and identities.

No release is promoted on a happy-path demonstration alone.

## 15. Current implementation mapping

As of 2026-10-06:

- durable snapshot→run binding supplies part of State Integrity;
- Evidence Drift v0.1 supplies the first material-change control in Evidence & Provenance;
- State Monitor v0.1 supplies the first transition invariant in Continuity & Transition;
- CFC Anchor `0.2.90rc1` remains the frozen authority/closure controller;
- Execution Gate is not yet implemented;
- Information Passport remains a separate pre-v1 integration track.

## 16. Next architecture gate

The next required artifact is:

`CONTROL_STACK_SCHEMA_v0.1.json`

It must encode the shared inter-layer envelope and pass:

- schema validation;
- round-trip preservation;
- invalid-state rejection;
- unknown-preservation;
- no-implicit-upgrade tests.

Until that schema exists and passes, later Control Stack modules must not invent incompatible private contracts.
