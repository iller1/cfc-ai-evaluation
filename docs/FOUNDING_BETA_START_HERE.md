# CFC + HAWM Founding Beta — START HERE

## What this beta is

CFC + HAWM Founding Beta is an experimental decision-control layer for testing whether AI conclusions are sufficiently supported before action.

The purpose of the beta is to expose real workflow problems, false stops, missed stops, usability problems and missing product features.

It is not intended to prove that CFC + HAWM is already complete.

## What you should use it for

Start with one small, bounded workflow where an AI system produces a conclusion or recommendation and a human needs to decide whether the available evidence is sufficient to act.

Good beta workflows have:
- a clear input state,
- identifiable evidence,
- a meaningful but non-catastrophic decision point,
- a human who can review the outcome,
- enough context to replay the case later.

## What you should not use it for

Do not use Founding Beta as the sole decision basis for:
- medical diagnosis or treatment,
- legal decisions,
- safety-critical control,
- employment termination or similarly high-impact decisions,
- financial execution where an incorrect decision could cause material harm,
- any workflow where human review cannot be retained.

## Basic workflow

1. Capture the AI conclusion and the evidence state that supports it.
2. Run the case through the current CFC + HAWM beta workflow.
3. Record the resulting control state and any unresolved conditions.
4. Human reviews the output before action.
5. If the result is wrong, unclear, overly conservative or insufficiently conservative, submit structured feedback.
6. The case is classified as bug, usability issue, missing feature, assumption error, or boundary finding.
7. After a change, the same case is re-tested together with regression tests.

## What to include in feedback

Always include:
- product version,
- workflow/case identifier,
- what you expected,
- what actually happened,
- relevant input/evidence state,
- whether the issue blocked work,
- whether the system stopped when it should not have or failed to stop when it should have.

## Current validation status

The system is under active evaluation.

Current benchmark observations and provenance records are available in the repository, but external independent validation remains open.

## Frozen baseline rule

If a beta release uses a frozen CFC Anchor/controller baseline, beta iteration must happen around that baseline unless a separately versioned future controller line is explicitly opened.

No silent modification of the frozen baseline is permitted.
