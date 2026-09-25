# CFC-next 0.3.0a2 freeze review

## Purpose

This is the explicit freeze-review stage for CFC-next 0.3.0a2.

It does not modify or rescore frozen CFC Anchor 0.2.90rc1 and it does not
rewrite the pinned 0.3.0a1 accepted experimental candidate.

## Required evidence

The freeze review re-executes and requires:

- 14/14 positive decision-accounting fixtures;
- 12/12 negative controls fail-closed;
- zero unexpected BOUND negative paths;
- deterministic full acceptance rerun;
- concurrent representative fresh-process positives;
- no import-time or operation-time frozen-engine mutation;
- 14/14 same-process state-isolation cases with no candidate authorization
  visible to frozen evaluation;
- pinned frozen wheel SHA-256;
- no historical rescore.

It also emits SHA-256 commitments for the 0.3.0a2 source and the complete
acceptance / readiness / state-isolation evidence chain.

## Freeze rule

The first run may only classify the candidate as
READY_FOR_PINNED_FREEZE_MANIFEST.

A later commit must pin the emitted commitments into a machine-readable freeze
manifest and make the freeze-review script verify those exact values. Only that
pinned, re-verified state can become the frozen CFC-next baseline.
