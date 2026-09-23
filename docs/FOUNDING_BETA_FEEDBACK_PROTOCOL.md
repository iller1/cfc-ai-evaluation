# CFC + HAWM Founding Beta — Feedback Protocol

## Purpose

Every external beta finding should be reproducible.

A useful report must preserve enough context to answer:

What happened, on which version, with which evidence state, and can we reproduce it?

## Required fields

- report_id
- company/workspace
- product_version
- timestamp
- workflow_name
- case_id
- input_state_reference
- evidence_state_reference
- observed_control_state
- expected_control_state
- user_action_taken
- severity
- reproducible: yes / no / unknown
- notes

## Classification

Each report receives exactly one primary classification:

- BUG
- USABILITY
- MISSING_FEATURE
- ASSUMPTION_ERROR
- BOUNDARY_FINDING

Optional secondary tags may be added, but the primary classification should remain stable for tracking.

## Closure-specific tags

Where relevant, also record:

- FALSE_STOP
- MISSED_STOP
- PREMATURE_CLOSURE
- AMBIGUOUS_OUTPUT
- PROVENANCE_GAP
- SCOPE_ERROR
- STALE_EVIDENCE
- PROVIDER_FAILURE

## Development loop

1. Reproduce the reported case on the exact reported version.
2. Preserve the original result.
3. Classify the finding.
4. Decide whether the change belongs outside the frozen baseline.
5. Implement the change only in an allowed layer/version.
6. Re-run the original case.
7. Run regression tests.
8. Record the new result and version.
9. Mark the finding RESOLVED, PARTIALLY_RESOLVED, NOT_REPRODUCED or ACCEPTED_BOUNDARY.

## Signal rule

A single customer report is a finding.

A recurring problem observed independently across multiple companies becomes a stronger product signal and should influence roadmap priority.

## Suggested intake channel

Choose one primary channel before external onboarding.

Examples:
- dedicated in-product form,
- private issue form,
- support email linked to a structured template.

Do not split first-round feedback across several untracked channels.
