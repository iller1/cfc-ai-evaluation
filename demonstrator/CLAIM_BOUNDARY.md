# Demonstrator claim boundary

## What this demonstrator establishes

Across the ten configured synthetic demonstration cases in the reconciled v1.0 package, the bundled frozen CFC Anchor execution track produces the preserved claim states, gate states, and closure decisions shown by the interface, and those cases are locally replayable through the frozen public API when the package verification succeeds.

The source/release provenance defect identified in RC1 was resolved by recovering the exact CASE_09 and CASE_10 bytes from the preserved RC1 release asset and verifying them against the preserved integrity anchors before restoring them to the reconciled source tree.

## What it is designed to illustrate

- unresolved evidence need not be converted into a definite positive or negative conclusion;
- direct contradiction can prevent closure;
- modeled redundancy can be explicitly accounted for without forcing a permanent block;
- decision scope can block closure even when a claim is verified;
- valid positive and valid negative evidence can both permit closure;
- the existence of a resolution record is not sufficient when the resolution is not validly bound or authorized for the active decision state;
- a `SUPPORTED` claim state is not equivalent to `VERIFIED` and does not by itself authorize closure.

## What it does not establish

The demonstrator alone does not establish general model-safety improvement, production readiness, external validation, universal correctness, ROI, causal efficacy, or applicability to every evidence/decision domain.

The synthetic model conclusions are fixed case inputs. The demonstrator evaluates whether closure is justified against those conclusions; it does not generate the model conclusions itself.
