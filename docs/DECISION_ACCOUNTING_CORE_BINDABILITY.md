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

## Result

The baseline reproduced the established mixed-endpoint boundary:

- claim state = `VERIFIED`;
- `control_closure = false`;
- the only false gate = `decision_support_closure_valid`;
- engine-selected support map = `{c1: [E1]}`;
- decision-level generic dependency endpoints = `[E1, E2]`;
- E2 is stale, non-selected, and not claim-owned.

Using the frozen engine registry directly inside the isolated test process, the
exact accounting state was accepted without changing the selected-support map:

- registration: `PENDING`;
- bind error: none;
- post-bind state: `BOUND`;
- selected-support map remained E1 only;
- endpoint set remained E1 + stale E2.

A direct frozen-core `prepare -> audit_text` after that exact bind produced:

- claim state = `VERIFIED`;
- `control_closure = true`;
- `decision_support_closure_valid = true`;
- decision support closure certificate = present;
- false gates = none.

The public `Controller.evaluate_snapshot` does **not** accept the injected
record as a supported workaround. It stops at
`integration_decision_dependency_accounting_runtime_verified=false` with
`DECISION_GENERIC_DEPENDENCY_ACCOUNTING_EXTERNAL_TRUST_NOT_VERIFIED`, because
the test deliberately bypasses the public external-trust verification/install
surface.

## Classification

**CORE-BINDABLE / PUBLIC-REACHABILITY DECISION-ACCOUNTING BOUNDARY**

The frozen core can bind and close the exact mixed selected/current +
stale/non-selected decision obligation. The observed obstruction is therefore
localized outside the core closure semantics, at the public construction /
verification reachability boundary for the required accounting state.

This is a localization result, not a supported workaround. It remains a boundary
finding rather than a `false block` classification until a normative contract
is established that requires the public surface to make every engine-required
decision obligation resolvable.

Frozen CFC Anchor 0.2.90rc1 remains unchanged.

