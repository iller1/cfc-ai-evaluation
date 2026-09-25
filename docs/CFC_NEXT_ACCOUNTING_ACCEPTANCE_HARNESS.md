# CFC-next decision-accounting acceptance harness

## Purpose

Create one reusable contract that separates:

1. what frozen CFC Anchor 0.2.90rc1 demonstrably does today; and
2. what a separately versioned CFC-next candidate must do after the proposed
   decision-accounting repair.

This harness does **not** patch or reinterpret the frozen controller.

## Positive fixture set

The positive set is exactly the 14 minimal blockers established by the frozen
taxonomy. The frozen-reference phase reruns every fixture in a fresh subprocess
and requires the already documented split:

- 3 engine-emitted/accounting-schema incompatibilities;
- 11 schema-valid public selected/excluded reachability inconsistencies that are
  core-bindable.

The target contract for a future CFC-next candidate requires the exact same
fixtures to become publicly representable and exactly bindable **without
changing the engine-selected support map**.

## Negative contract

The manifest also freezes 12 negative-control classes that a future candidate
must reject or leave non-authorizing. These cover wrong nodes, wrong endpoint
sets, out-of-snapshot evidence, absent obligations, wrong selected maps, wrong
scope/context, source-semantic misuse, malformed nodes, attestation failures and
failed fresh-universe binding.

## Current CI meaning

Today CI runs only the frozen-reference phase. It verifies that the historical
baseline still matches the empirical record and that the future target contract
covers exactly the same 14 positive fixtures.

A future CFC-next implementation should reuse this manifest and add a second
execution profile that enforces the target outcomes. Frozen historical results
must never be rescored.
