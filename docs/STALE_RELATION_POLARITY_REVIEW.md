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
