# Decision accounting contract review

## Goal

Determine whether the core-bindable / public-reachability boundary is merely an
unexposed capability or whether the frozen system's own policy contract requires
preservation and resolution of decision-relevant relations through excluded
supports while the public accounting surface makes the exact required state
unrepresentable.

This review is read-only.

It inspects:

- the pinned `SUPPORT_UNIVERSE_POLICY`;
- decision-level generic-dependency assessment and universe construction;
- decision support closure certificate requirements;
- exact generic accounting lookup/binding rules;
- public Controller generic-accounting draft/install/finalize methods.

## Decision rule

Do **not** classify the stale-E2 boundary as a false block merely because the
core can close it.

A stronger classification requires explicit contract evidence showing both:

1. the frozen policy requires the excluded/stale relation to remain a
   decision-level closure obligation; and
2. the supported public accounting surface is intended to provide a path to
   satisfy such engine-required obligations, yet rejects the exact state.

If only (1) is established, retain the reachability-boundary classification.

Frozen CFC Anchor 0.2.90rc1 remains unchanged.

## Result

The frozen contract is explicit about excluded-support relation preservation.

Relevant `SUPPORT_UNIVERSE_POLICY` values are:

- `selection_does_not_delete_evidence_relations = true`;
- `selected_excluded_relation_coverage_required = true`;
- `generic_dependency_path_through_excluded_supports_preserved = true`;
- `generic_dependency_selected_support_path_closure_required = true`;
- `decision_level_relation_discovery_required = true`;
- `decision_level_relation_resolution_exact_binding_required = true`;
- `decision_dependency_accounting_exact_context_binding_required = true`;
- required resolution type =
  `DEPENDENCY_ACCOUNTED_NOT_COUNTED`.

The frozen decision-level assessment code then makes the mixed modeled /
snapshot-only case an explicit required obligation:

`modeled_endpoints and snapshot_only_endpoints -> decision_level_required=True`

with classification:

`DECISION_GENERIC_MODELED_SNAPSHOT_MIXED_UNCOVERED`.

The closure certificate requires every `decision_level_required` generic
candidate to have an exact bound generic-dependency accounting record. Missing
accounting returns no decision-support closure certificate.

The supported public Controller surface provides the corresponding lifecycle:

1. `draft_decision_generic_dependency_accounting`;
2. `install_verified_decision_generic_dependency_accounting`;
3. `finalize_verified_decision_dependency_accountings_for_prepare`.

However, the public draft contract rejects the exact mixed obligation because it
requires:

`evidence_ids ⊆ selected_supports`

and raises:

`ValueError: generic dependency endpoints must be selected supports`.

For the established stale-E2 case, the frozen engine itself produces:

- selected support map = E1 only;
- obligation endpoints = E1 + stale E2;
- E2 = snapshot-only / non-selected.

Therefore the exact engine-required obligation cannot enter the supported public
draft -> verify/install -> finalize lifecycle without changing the selected
support map and thereby changing the decision state being accounted for.

The core-bindability control independently showed that this exact obligation is
semantically resolvable by the frozen core when the exact accounting row is
present: `decision_support_closure_valid=true`, closure certificate present,
and `control_closure=true`.

## Classification

**UNSATISFIABLE PUBLIC DECISION-ACCOUNTING OBLIGATION / FROZEN CONTRACT INCONSISTENCY**

This is stronger than a generic API reachability boundary:

- the frozen policy requires the selected/excluded relation to remain
  decision-relevant;
- the frozen engine turns the mixed endpoint into a required accounting
  obligation;
- frozen closure requires exact accounting for that obligation;
- the supported public accounting constructor forbids the exact endpoint set;
- the frozen core can close the exact state if the required accounting is
  present.

The inconsistency is localized to the supported public accounting contract, not
to the core closure semantics.

We still avoid the shorthand label `false block` in the research record. The
more precise demonstrated result is that a frozen-policy-required decision
obligation is unsatisfiable through the supported public accounting lifecycle.

Frozen CFC Anchor 0.2.90rc1 remains unchanged.

