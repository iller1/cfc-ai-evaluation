# Decision accounting core bindability

## Goal

Localize the decision-accounting reachability boundary one layer below the
public Controller API.

The established stale-E2 boundary has:

- E1 = CURRENT and selected justificatory support;
- E2 = STALE and not selected / not claim-owned;
- a decision-level generic dependency obligation whose endpoint set contains
  both E1 and E2;
- no public Controller draft path that can represent the exact obligation
  without changing the selected-support state.

This probe asks a narrower question:

> If the exact engine-selected support map and exact engine-emitted obligation
> are registered directly through the frozen engine's own accounting registry,
> can the frozen core bind that accounting and satisfy
> `decision_support_closure_valid`?

## Constraint

This is a non-production localization control. It may mutate runtime registry
state inside the isolated test process, but it does not modify frozen source,
policy, or the CFC Anchor artifact.

The result must not be treated as a supported public workflow.

## Interpretation

- If the core binds the exact mixed selected/stale obligation and
  `decision_support_closure_valid` becomes true, the obstruction is localized
  to the public accounting reachability contract.
- If the core cannot bind it, the obstruction is deeper in frozen decision
  accounting semantics.
