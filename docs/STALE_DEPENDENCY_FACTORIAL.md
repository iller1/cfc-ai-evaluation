# Stale dependency factorial — 16-state isolation

## Goal

Decompose the open `STALE DEPENDENCY AUTHORIZATION RESIDUE` boundary finding.

The prior review established that:

- E2 can become STALE and cease to affect claim qualification;
- closure can still remain blocked;
- E1 alone with preserved shared-looking provenance can close.

The remaining question is **which shared relation family leaves the authorization residue**.

## Factorial design

Hold constant:

- E1 = POSITIVE / CURRENT;
- E2 = POSITIVE / STALE;
- conclusion = POSITIVE;
- required supports = 1;
- scope = EXPECTED;
- no explicit independence certificate.

Vary four binary factor groups independently:

1. source semantics shared:
   repository / producer / process / failure-domain IDs;
2. origin-lineage shared:
   root origin / origin / extractor / lineage chain;
3. common-mode group shared;
4. dependency IDs shared:
   data source / sensor / transform / model / extractor / cache /
   upstream DB / operator / preprocessing / runtime.

This yields exactly **16 states**.

## Analysis rule

Do not infer a controller defect from STOP alone.

First identify the **minimal blocking masks**: shared-factor sets for which closure
is blocked while every strict subset of the same shared factors allows closure.

Those masks isolate the smallest relation family, or interaction between
families, sufficient to preserve downstream authorization effects from stale E2.

Frozen CFC remains unchanged.


## Result

The final run executes every state in a fresh subprocess. This matters because
the frozen engine enforces immutable identities and relation state; running all
16 states in one process created cross-case fixture contamination.

The isolated factorial passed its equivalence control:

- original SHARED_LINEAGE fixture:
  - claim state = VERIFIED
  - control closure = false
  - false gates = [`decision_support_closure_valid`]
- factorial `1111`:
  - claim state = VERIFIED
  - control closure = false
  - false gates = [`decision_support_closure_valid`]

All three equivalence checks matched.

### Counts

- states: **16**
- ALLOW: **2**
- STOP: **14**

The two ALLOW states are:

- `0000` — no shared factor groups;
- `1000` — source-semantics group shared only.

Factor order is:

`source semantics | origin/lineage | common-mode group | dependencies`

### Minimal blocking masks

Three one-factor masks are sufficient to produce:

- claim state = VERIFIED
- control closure = false
- only false gate = `decision_support_closure_valid`

They are:

- `0100` — origin/lineage shared only;
- `0010` — common-mode group shared only;
- `0001` — dependency IDs shared only.

By contrast:

- `1000` — source semantics shared only — remains ALLOW / VERIFIED.

## Refined boundary finding

The stale-E2 authorization residue is therefore not explained by shared source
semantics alone in this fixture.

It is independently triggered by at least three provenance/dependency relation
families:

1. origin/lineage identity;
2. explicit common-mode group;
3. generic dependency identities.

Observed rule:

`STALE E2 + any active shared provenance/dependency relation -> claim may remain VERIFIED while closure authorization remains blocked`

This remains a boundary finding rather than a false-block classification. The
frozen contract still does not specify whether stale evidence must lose all
relation-level authorization effects once it ceases to count as active claim
evidence.

## Next decomposition

The next external experiment should split:

- origin/lineage into root origin, origin, extractor and lineage-chain factors;
- generic dependencies into their individual dependency dimensions.

The common-mode-group factor is already atomic at this abstraction level.
