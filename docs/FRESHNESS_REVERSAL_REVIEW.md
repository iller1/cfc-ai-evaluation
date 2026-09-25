# Freshness reversal — semantic review

## Question

The full state-space sweep found cases where changing one evidence record from
CURRENT to STALE increased closure.

That observation is counter-intuitive if freshness is interpreted as a simple
monotonic quality score. CFC, however, evaluates an active evidence universe,
so the semantic question is different:

> Does making E1 stale incorrectly strengthen the claim, or does it correctly
> remove E1 from the active decision-relevant universe, leaving another current
> record sufficient for closure?

## Minimal pairs

This review holds constant:

- conclusion = POSITIVE;
- required independent supports = 1;
- scope = EXPECTED;
- provenance = DISTINCT;
- independence authority = NONE;
- E2 = POSITIVE / CURRENT.

Only E1 validity changes CURRENT -> STALE.

Two E1 polarities are checked:

1. E1 POSITIVE — two current matching supports become one stale + one current;
2. E1 NEGATIVE — active contradiction becomes stale contradiction + one current support.

## Classification rule

A closure increase is not automatically a freshness failure.

It is compatible with the intended semantics if all of the following are true:

- stale E1 is not counted as current support;
- stale E1 is not used to justify closure;
- remaining current evidence independently satisfies the one-support policy;
- any prior block was caused by the presence of E1 in the active support/conflict
  universe rather than by an inference that STALE is favorable evidence.

If the controller instead uses stale E1 as support, the case would become a
candidate false closure.

The frozen controller is not modified by this review.


## Result

The targeted CI review completed successfully.

### Pair A — matching support becomes stale

Before:

- E1 = POSITIVE / CURRENT
- E2 = POSITIVE / CURRENT
- required supports = 1
- independence authority = NONE
- result = STOP / SUPPORTED
- violation = `CERTIFIED_SUBSET_BUT_UNIVERSE_UNRESOLVED`
- active universe = E1 + E2

After changing only E1 CURRENT -> STALE:

- result = ALLOW / VERIFIED
- reason = `policy-satisfied support set (1)`
- no claim-support-policy violations
- no false gates
- no critical unresolved state

The stale E1 is not used as support. The active support universe contracts to the
remaining current support E2.

### Pair B — opposing record becomes stale

Before:

- E1 = NEGATIVE / CURRENT
- E2 = POSITIVE / CURRENT
- result = STOP / QUARANTINED
- global consistency violation = `POLARITY_CONFLICT` over E1 + E2

After changing only E1 CURRENT -> STALE:

- result = ALLOW / VERIFIED
- no global consistency violation
- no false gates
- reason = `policy-satisfied support set (1)`

Again, stale E1 is not treated as favorable evidence. It is excluded from the
active contradiction set, leaving current E2 as the valid support.

## Classification

**INTENDED / EXPLAINED ACTIVE-UNIVERSE CONTRACTION**

The apparent freshness reversal is not:

`STALE -> stronger evidence`

It is:

`CURRENT record participates in active universe -> STALE record no longer participates -> remaining current state is re-evaluated`

Therefore a decrease in freshness can increase closure only indirectly by
removing a record that previously created unresolved support-selection state or
an active contradiction.

This is not classified as false closure.

## New permanent regression classes

### STALE EXCLUSION / ACTIVE-UNIVERSE CONTRACTION

Rule:

> Evidence that is stale at the audit date must not remain in the active support
> universe merely because it was previously current.

### STALE CONFLICT NON-PROPAGATION

Rule:

> A stale opposing record must not continue to create an active polarity
> conflict when a current supporting record remains valid.

These should be preserved as external regression tests around the frozen
controller.
