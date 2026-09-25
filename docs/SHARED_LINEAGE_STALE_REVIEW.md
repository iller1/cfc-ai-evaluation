# Shared-lineage stale-record review

## Purpose

Resolve the remaining state-space Finding D:

> In SHARED_LINEAGE cases, adding a stale second record can appear to change
> authorization.

The original E2 OMIT -> INCLUDE comparison is not a clean one-factor mutation
because the custom fixture also rewrites E1 provenance into shared-lineage form
when the second record is introduced.

This review therefore uses a cleaner pair:

- E1 and E2 are present in both states;
- provenance remains SHARED_LINEAGE in both states;
- independence authority remains NONE;
- only E2 validity changes CURRENT -> STALE.

## Question

Does stale E2 itself continue to affect closure through dependency/common-mode
semantics, or was the earlier effect caused by the derived E1 provenance rewrite
that accompanied E2 addition?

## Interpretation boundary

This is an external semantic review over frozen CFC Anchor 0.2.90rc1.
The controller is not modified.


## Result

The controlled two-record pair produced:

### E2 CURRENT

- E1 = POSITIVE / CURRENT
- E2 = POSITIVE / CURRENT
- provenance = SHARED_LINEAGE
- required supports = 1
- result = STOP / SUPPORTED
- violation = `CERTIFIED_SUBSET_BUT_UNIVERSE_UNRESOLVED`

### E2 STALE

Only E2 validity changed CURRENT -> STALE.

Observed:

- claim state = VERIFIED
- control closure = false
- decision = STOP
- critical unresolved = none
- claim-support-policy violations = none
- global-consistency violations = none
- only false gate = `decision_support_closure_valid`

Therefore making E2 stale removes its effect from claim-support qualification, but
does not fully remove its effect from closure authorization.

## Isolation control

A second external fixture removed E2 entirely while preserving E1's shared
lineage/common-mode provenance identifiers.

Observed for single E1 with preserved shared provenance:

- reason = `policy-satisfied support set (1)`
- control closure = true
- false gates = none
- critical unresolved = none
- stop type = `EPISTEMIC_STOP`

This rules out the simple explanation that E1's shared-provenance identifiers
alone are sufficient to cause the STOP.

## Classification

**BOUNDARY FINDING — STALE DEPENDENCY AUTHORIZATION RESIDUE**

The current evidence supports this narrower statement:

> A stale second record can stop affecting claim qualification while still
> affecting downstream closure authorization through the dependency/shared-
> lineage state.

This is **not classified as false closure**. It is also not yet classified as a
false block because the frozen contract does not currently establish whether
stale dependency relations are required to disappear completely from decision
authorization.

## New test class

**STALE CLAIM EXCLUSION / AUTHORIZATION PERSISTENCE**

Required comparison:

1. current E1 + current E2, shared lineage;
2. current E1 + stale E2, same shared lineage;
3. current E1 only, while preserving E1 shared-lineage provenance identifiers.

The key invariant to track is the separation:

`claim qualification != downstream authorization`

A future CFC-next design review should decide explicitly whether stale evidence
may retain dependency-level authority effects after it has ceased to qualify as
active claim evidence.

Frozen CFC remains unchanged.
