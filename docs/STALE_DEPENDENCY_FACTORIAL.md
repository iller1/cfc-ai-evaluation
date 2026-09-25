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
