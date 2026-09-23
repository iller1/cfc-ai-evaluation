# CFC + HAWM Founding Beta RC1 — Scope

Status: candidate definition, not yet released.

## Purpose

Founding Beta RC1 packages the existing bounded productization work into one controlled external-use candidate.

It does not change the frozen CFC Anchor or Operator Wrapper.

## Component identities

- Operator Wrapper: v1.23 — frozen
- CFC Anchor: 0.2.90rc1 — frozen
- CFC Demonstrator: v1.0 — presentation/replay layer
- Integration Layer: v0.4 RC — bounded integration candidate
- Pro Beta application: v0.1 line
- Benchmark: CFC_HAWM_NL_CLOSURE_BENCHMARK_V2

## Founding Beta boundary

RC1 is intended only for:
- a small number of invited companies,
- one or a few bounded low-risk workflows per company,
- human-reviewed use,
- full version/context logging,
- structured feedback and replay.

RC1 is not:
- externally validated protection,
- a certification system,
- a production safety standard,
- a sole authority for high-risk decisions.

## Required pre-release evidence

Before tagging RC1:

- Pro Beta test suite passes on the exact candidate commit.
- Frontend regression tests pass.
- Production health remains green on the currently deployed production baseline.
- Frozen controller identities are unchanged.
- A sample workflow can be completed and replayed.
- START HERE / limitations / feedback / terms-data drafts are present.
- The feedback intake channel is functional.
- Known external-validation gaps remain explicitly documented.

## Non-blocking open evidence

The following remain desirable but are not launch blockers for an explicitly experimental Founding Beta:

- independent methods review,
- independent semantic second-pass review,
- external replication,
- external usability timing gates.

Their absence must remain visible in status/claims.

## Hard blockers to paid onboarding

- no agreed data/privacy policy,
- no retention/deletion process,
- no beta terms,
- no payment/billing mechanism,
- no identified first companies,
- no bounded workflow definition for each participant.

## Release rule

RC1 may be tagged only after the exact candidate commit has passed tests and the release checklist contains no unresolved technical blocker for controlled low-risk use.
