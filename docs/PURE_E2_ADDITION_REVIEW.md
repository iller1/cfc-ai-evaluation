# Pure E2 addition — semantic review

## Purpose

Review the closure increases and decreases found in the 128 **PURE_E2_ADDITION**
edges from the structured HAWM state-space sweep.

This review deliberately excludes the two fixture-coupled E2 classes:

- no SHARED_LINEAGE provenance rewrite;
- no VERIFIED independence-certificate installation.

Therefore every pair uses:

- provenance = DISTINCT;
- independence authority = NONE.

Only the presence/state of E2 changes.

## Minimal cases

Four canonical cases are tested:

1. current matching support + add current matching support;
2. current matching support + add current opposing evidence;
3. stale matching record + add current matching support;
4. stale opposing record + add current matching support.

## Questions

The review asks:

- can adding a second matching current record reduce closure because the active
  support universe expands beyond what is justified for a one-support policy?
- can adding current opposing evidence correctly convert a valid closure into
  QUARANTINED conflict?
- can adding one current support to a stale-only state correctly establish
  closure without using the stale record?

Observed output is not classified until exact gates/violations are inspected.

Frozen CFC remains unchanged.


## Result

The targeted CI review completed successfully.

### Case 1 — current support + add current matching support

Before:

- E1 = POSITIVE / CURRENT
- result = ALLOW / VERIFIED
- reason = `policy-satisfied support set (1)`

After adding E2 = POSITIVE / CURRENT:

- result = STOP / SUPPORTED
- violation = `CERTIFIED_SUBSET_BUT_UNIVERSE_UNRESOLVED`
- candidate subset = `[E1]`
- universe evidence IDs = `[E1, E2]`
- `selection_certificate_valid = false`
- `universe_coverage_certificate_valid = false`

Classification: **INTENDED SUPPORT-UNIVERSE EXPANSION**.

Adding another current matching record enlarges the active support universe. Under
a one-support policy the controller cannot silently ignore the extra current
record and preserve the previous single-support closure without justified subset
selection / universe coverage.

### Case 2 — current support + add current opposition

Before:

- result = ALLOW / VERIFIED

After adding E2 = NEGATIVE / CURRENT:

- result = STOP / QUARANTINED
- violation = `POLARITY_CONFLICT` over E1 + E2
- false gates = `decision_support_closure_valid`,
  `global_consistency_valid`, `no_critical_unresolved`

Classification: **INTENDED ACTIVE-CONFLICT INTRODUCTION**.

### Case 3 — stale matching record + add current matching support

Before:

- stale-only state
- result = STOP / UNRESOLVED
- violation = `INSUFFICIENT_SUPPORT_COUNT`, observed 0, required 1

After adding E2 = POSITIVE / CURRENT:

- result = ALLOW / VERIFIED
- reason = `policy-satisfied support set (1)`
- no false gates

Classification: **INTENDED CURRENT-SUPPORT INTRODUCTION**.

The stale record is not counted as support.

### Case 4 — stale opposition + add current matching support

Before:

- stale opposing record only
- result = STOP / UNRESOLVED
- violation = `INSUFFICIENT_SUPPORT_COUNT`, observed 0, required 1

After adding E2 = POSITIVE / CURRENT:

- result = ALLOW / VERIFIED
- no polarity conflict
- no false gates

Classification: **INTENDED STALE-CONFLICT NON-PROPAGATION + CURRENT-SUPPORT INTRODUCTION**.

## Overall classification

The pure E2 additions do not expose a false closure or false block in these
minimal representatives.

They demonstrate that:

`more evidence != more authorization`

because adding evidence can:

- expand the active support universe and require new selection justification;
- introduce an active contradiction;
- add the first current support to a stale-only state.

## New permanent regression classes

### ACTIVE SUPPORT-UNIVERSE EXPANSION

> Adding a new current matching evidence record must trigger re-evaluation of the
> support universe; prior single-support authorization must not be blindly
> inherited.

### ACTIVE CONFLICT INTRODUCTION

> Adding current opposing evidence must invalidate prior closure until the
> contradiction is validly resolved.

### CURRENT SUPPORT INTRODUCTION OVER STALE BACKGROUND

> A new current support may establish closure when previous records are stale,
> but stale records must not be counted as the support that satisfies policy.
