# CFC Demonstrator v1.1 — 60-Second First-Impression Protocol

Status: FROZEN TEST PROTOCOL FOR UX CANDIDATE

## Purpose

Measure whether a person unfamiliar with CFC can understand the narrow value of the Demonstrator within 60 seconds, without prior explanation from the author.

This is a UX/comprehension test only. It is not a technical validation, methods review, independent replication, or product-readiness assessment.

## Participant eligibility

Participant should:
- not have previously used CFC;
- not have been briefed on the intended answer before the test;
- be able to read ordinary technical/product English;
- use the v1.1 UX candidate unchanged during the timed review.

## Procedure

1. Open the v1.1 landing page.
2. Start the 60-second timer immediately.
3. Participant may click through the highlighted 60-second review path.
4. No live explanation or hints from the author during the timed period.
5. Stop after 60 seconds even if the participant has not completed all five cases.
6. Immediately ask the four questions below and preserve the answers verbatim before interpretation.

## Questions

Q1. In one sentence, what problem do you think CFC is trying to solve?

Q2. What does `STOP` mean here?

Q3. Give one example of why CFC might stop a decision from being closed.

Q4. What does `ALLOW` mean here?

## Predefined scoring rubric

Each question scores 1 point only if the answer captures the following meaning without being prompted.

### Q1 — Core value

PASS if the answer says, in substance, that CFC checks whether the available evidence/current state justifies closing a model or AI-assisted conclusion.

FAIL if the answer instead describes CFC mainly as a factuality checker, hallucination detector, legal checker, generic safety system, or something unrelated to closure authority.

### Q2 — Meaning of STOP

PASS if the answer says, in substance, that the current evidence/state does not justify closure yet.

The participant does **not** need to use the words `UNRESOLVED`, `QUARANTINED`, or `SUPPORTED`.

FAIL if the participant interprets STOP as meaning the model conclusion has necessarily been proven false.

### Q3 — Reason for STOP

PASS if the participant identifies at least one mechanism actually shown in the 60-second path, such as:
- evidence not yet epistemically available/current for the audit point;
- direct contradiction/conflict;
- a resolution not bound to the exact decision context;
- insufficient required independent support.

FAIL if no valid shown reason is identified.

### Q4 — Meaning of ALLOW

PASS if the answer says, in substance, that the supplied evidence/state satisfies the closure requirements and the decision may be closed.

FAIL if ALLOW is interpreted as a guarantee that the underlying real-world proposition is universally true or permanently safe.

## Outcome classes

### CLEAR PASS

4/4 rubric points.

### PARTIAL PASS

3/4 rubric points, provided Q1 and Q2 both PASS.

### FAIL

Any of:
- fewer than 3/4 points;
- Q1 FAIL;
- Q2 FAIL.

## Secondary observations

Record separately and do not use to change the predefined score:
- how many of the five cases were viewed;
- where the participant hesitated;
- which terms were unclear;
- whether the participant noticed the distinction between `SUPPORTED` and `VERIFIED`;
- whether the participant wanted technical detail before understanding the basic purpose.

## Interpretation boundary

One participant is one UX observation only.

A PASS does not prove broad comprehensibility, commercial value, external validation, or production readiness.

The first three unfamiliar participants should be preserved, including slow, confused, or negative outcomes. Do not discard or replace an inconvenient result with a later retry.
