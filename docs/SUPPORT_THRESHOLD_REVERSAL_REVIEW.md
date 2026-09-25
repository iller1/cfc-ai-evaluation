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
