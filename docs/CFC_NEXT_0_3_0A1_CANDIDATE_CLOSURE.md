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

## Pinned candidate commitments

The authoritative closure manifest is:

`research/cfc_next_0_3_0a1_candidate_closure_manifest.json`

It pins the accepted experimental candidate to the following SHA-256
commitments:

- candidate source:
  `c8012d897ccbf0c44c6f298f408c5d0b850489e311c88fb0ebb385e845312dbe`
- candidate acceptance harness:
  `edb6f92dd29a80d8b2b52759a1038df97f0f320a1c67c2dab87380f61abcfb83`
- acceptance manifest:
  `31191438ea7ceffd8acdceb352c79f38f58900b5a4b3c991119e6d4c8e0ede60`
- repair specification:
  `275e261279e1861dd5b2233829b60d535a9f95b6fc57a763dd30d4d2f0f38f56`
- frozen CFC Anchor 0.2.90rc1 wheel:
  `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`

The closure workflow recomputes these commitments and must match the pinned
manifest exactly. A later change to the candidate source, acceptance harness,
acceptance manifest, repair specification, or frozen reference wheel therefore
fails closure instead of silently moving the reference point.

## Acceptance result

The accepted candidate contract is:

- positive fixtures: **14/14 PASS**;
- negative controls: **12/12 fail-closed**;
- unexpected BOUND negative paths: **0**;
- frozen reference modified: **false**;
- historical rescore performed: **false**.

This status is intentionally narrower than a release or frozen baseline.
`0.3.0a1` is an accepted experimental candidate only.

