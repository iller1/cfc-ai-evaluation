# Stale relation polarity review

## Goal

Test whether the open stale-relation authorization boundary depends on the
semantic polarity of the stale record.

Hold constant:

- conclusion = POSITIVE;
- E1 = POSITIVE / CURRENT;
- E1 alone satisfies required supports = 1;
- E2 = STALE;
- scope = EXPECTED;
- no explicit support-set independence certificate.

For E2, compare:

- POSITIVE / STALE;
- NEGATIVE / STALE.

Repeat that comparison with one minimal shared relation at a time:

1. common-mode group;
2. root-origin identity;
3. one generic dependency identity (data_source).

Total: **6 isolated states**.

## Interpretation

If positive-stale and negative-stale produce the same VERIFIED/STOP
authorization state with the same false gate, the residue is polarity-insensitive
at the tested relation level.

If they differ, stale semantic role still matters after the record stops
qualifying as active claim evidence.

This is an external review. Frozen CFC remains unchanged.


## Result

All six isolated states completed successfully.

For each tested shared-relation family:

- common-mode group;
- root-origin identity;
- generic dependency identity;

the two stale-polarity variants were identical.

### POSITIVE / STALE

- claim state = VERIFIED
- control closure = false
- false gates = [`decision_support_closure_valid`]
- no global-consistency violation

### NEGATIVE / STALE

- claim state = VERIFIED
- control closure = false
- false gates = [`decision_support_closure_valid`]
- no global-consistency violation

For all three relation families:

- same claim state = true;
- same control closure = true;
- same false gates = true.

## Classification

**POLARITY-INSENSITIVE RELATION-LEVEL STALE AUTHORIZATION PERSISTENCE**

Within the tested boundary, the downstream authorization residue does not depend
on whether stale E2 supports or opposes the claim.

Observed rule:

`stale record polarity changes, shared relation held fixed -> authorization result unchanged`

This narrows the mechanism further:

> The tested persistence is associated with the existence of a shared
> provenance/dependency relation to stale evidence, not with the stale record's
> positive or negative semantic role.

This remains a boundary finding rather than a false-block classification.
