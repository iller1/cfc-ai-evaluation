# Stale relation age review

## Goal

Test whether the open stale-relation authorization boundary changes as the same
stale record becomes older.

Hold constant:

- conclusion = POSITIVE;
- E1 = POSITIVE / CURRENT;
- E1 alone satisfies required supports = 1;
- E2 = POSITIVE / STALE;
- E2 valid_to = 2026-08-31;
- scope = EXPECTED;
- no explicit support-set independence certificate;
- one minimal shared relation at a time.

Shared relation families:

1. common-mode group;
2. root-origin identity;
3. one generic dependency identity (data_source).

Evaluation windows:

- D3: as_of = 2026-09-03 (3 days after stale valid_to);
- D31: as_of = 2026-10-01 (31 days after stale valid_to);
- D92: as_of = 2026-12-01 (92 days after stale valid_to).

Total: **9 isolated states**.

Each state runs in a fresh subprocess. Frozen CFC Anchor 0.2.90rc1 is not
modified.

## Interpretation

If all three time windows produce the same authorization signature for a given
shared relation, the tested persistence is insensitive to stale age over the
observed interval.

If a later window differs, reduce that relation/window transition to the minimal
pair and identify which gate or consistency layer changes.

This is an external research-harness review. It does not classify the behavior
as a false block without a contract-level basis.


## Result

All nine isolated states completed successfully.

For each tested shared-relation family:

- common-mode group;
- root-origin identity;
- generic dependency identity (`data_source`);

the authorization signature was identical at all three stale ages:

- 3 days after E2 `valid_to`;
- 31 days after E2 `valid_to`;
- 92 days after E2 `valid_to`.

At D3, D31, and D92:

- claim state = VERIFIED
- control closure = false
- false gates = [`decision_support_closure_valid`]
- no claim-support-policy violation
- no critical unresolved item
- no global-consistency violation

For all three relation families:

- same authorization signature across all windows = true.

## Classification

**STALE-AGE-INSENSITIVE RELATION-LEVEL AUTHORIZATION PERSISTENCE**

Within the tested interval, the observed downstream authorization residue does not
decay or change as the same stale E2 ages from 3 to 92 days beyond its `valid_to`.

Observed rule:

`stale age increases, shared relation and evaluated-snapshot membership held fixed -> authorization result unchanged`

Combined with the previous polarity, subject-relevance, and snapshot-locality
reviews, the tested persistence is currently characterized as:

- polarity-insensitive;
- claim-subject-insensitive;
- stale-age-insensitive over 3-92 days;
- bound to stale E2 participating in the evaluated snapshot;
- relation-specific through `decision_support_closure_valid`.

This remains a boundary finding rather than a false-block classification.
