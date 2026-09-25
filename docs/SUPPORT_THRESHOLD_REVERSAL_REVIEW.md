# Support-threshold reversal — semantic review

## Question

Why can the same two current matching evidence records with explicit VERIFIED
independence produce:

- required supports = 1 -> STOP / SUPPORTED
- required supports = 2 -> ALLOW / VERIFIED

when every other structured input is unchanged?

## Controlled pair

The review holds constant:

- conclusion polarity;
- two CURRENT matching evidence records;
- EXPECTED scope;
- DISTINCT provenance;
- VERIFIED independence authority.

Only `required_independent_supports` changes from 1 to 2.

Both positive and polarity-inverted negative forms are tested.

## Important adapter fact

The custom fixture installs one explicit support-set independence certificate
over exactly E1 + E2 when `independence_authority=VERIFIED` and two evidence
records are present.

Therefore the certificate directly matches the two-support selection.

For the one-support policy, the controller must justify selecting a one-record
subset from a two-record evidence universe while the available independence
certificate is defined over the E1+E2 pair.

## Classification rule for this review

Do not call the observed reversal a bug merely because increasing a threshold
appears to make closure easier.

First inspect the exact gates removed/added and determine whether the frozen
contract intentionally distinguishes:

1. validating the full certified E1+E2 support set; from
2. justifying a one-record support selection from that same evidence universe.

If the one-support case is blocked specifically by support-selection /
support-universe / relation-coverage gates, while the two-support case satisfies
them using the pair-bound certificate, the reversal may be an intended
consequence of set-specific authorization rather than a false closure.

The frozen controller is not modified by this review.


## Result

GitHub Actions targeted run #1 completed successfully for both polarity-symmetric
minimal pairs.

Observed for required supports = 1:

- decision: STOP
- claim state: SUPPORTED
- violation type: `CERTIFIED_SUBSET_BUT_UNIVERSE_UNRESOLVED`
- candidate subset: `[E1]`
- universe evidence IDs: `[E1, E2]`
- `selection_certificate_valid = false`
- `universe_coverage_certificate_valid = false`

The false gates include:

- `claim_specific_support_policy_valid`
- `claim_support_universe_common_mode_coverage_valid`
- `decision_relevant_relation_discovery_complete_valid`
- `decision_support_closure_valid`
- `no_critical_unresolved`
- `source_independence_semantics_valid`
- `support_relation_instance_resolution_coverage_valid`
- `support_selection_justification_valid`
- `support_set_common_mode_coverage_valid`

Observed for required supports = 2:

- decision: ALLOW
- claim state: VERIFIED
- reason: `policy-satisfied support set (2)`
- no claim-support-policy violations
- no false gates
- no critical unresolved claims

The negative-polarity inversion produced the same structural result.

## Classification

**INTENDED / EXPLAINED SET-SPECIFIC AUTHORIZATION BEHAVIOR**

The apparent monotonicity reversal is explained by the fact that the explicit
independence certificate is bound to the full E1+E2 support set.

When the policy requires only one support, the controller is not simply allowed
to discard E2 and reuse the pair certificate as authorization for E1 alone. It
requires a justified subset selection and universe coverage. Those conditions
are unresolved, so closure is withheld.

When the policy requires two supports, the selected support set is the exact
certified E1+E2 pair. The set-specific authorization matches the selected set and
closure can proceed.

Therefore:

`higher numeric threshold != strictly harder closure`

when changing the threshold also changes which support set must be justified
against set-bound authorization evidence.

This is not classified as false closure or false block.

## New permanent test class

The combinatorial sweep has still exposed a useful regression class:

**SET-BOUND AUTHORIZATION / SUBSET-SELECTION NON-INHERITANCE**

Rule:

> Authorization for a support set must not be silently inherited by an
> uncertified subset of that set.

A future regression fixture should preserve this behavior explicitly.
