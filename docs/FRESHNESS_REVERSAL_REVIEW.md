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
