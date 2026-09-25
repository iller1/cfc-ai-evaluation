# CFC-next 0.3.0a1 candidate closure

## Purpose

Close the first separately versioned CFC-next implementation milestone without
changing the frozen reference.

The candidate is not promoted to a new frozen baseline by this step.

## Closure requirements

The closure gate must prove all of the following in one run:

- candidate version is 0.3.0a1;
- all 14 positive decision-accounting fixtures pass;
- all 12 negative controls remain fail-closed;
- there are zero unexpected BOUND negative paths;
- the pinned CFC Anchor 0.2.90rc1 wheel still matches its recorded SHA-256;
- no historical result is rescored;
- exact SHA-256 commitments are emitted for the candidate source, acceptance
  harness, acceptance manifest, and repair specification.

## Status model

On success the candidate status is:

ACCEPTED_EXPERIMENTAL_CANDIDATE

Promotion status remains:

NOT_FROZEN_NOT_RELEASE_BASELINE

A later promotion/freeze step, if any, must be separate and must not rewrite the
frozen 0.2.90rc1 history.
