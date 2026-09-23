# CFC + HAWM Founding Beta — Workflow Policy

## Objective

The first Founding Beta round should test a narrow reliability question in bounded, reviewable workflows:

> Does the available evidence and current system state justify a definitive conclusion before action?

The first round is not intended to cover every AI workflow.

## Allowed first-round workflow characteristics

A workflow is suitable when all of the following are true:

- low or moderate consequence if the beta system is wrong;
- a human retains final authority;
- evidence/input state can be captured and replayed;
- the expected decision boundary is understandable;
- sensitive data is not required;
- the workflow can be paused when the system returns unresolved;
- the company can provide feedback with enough context to reproduce issues.

## Suitable examples

- internal research validation before a low-risk business action;
- policy/document consistency checks where a human approves the result;
- product/specification evidence checks;
- vendor or technical due-diligence support using non-sensitive data;
- QA/evaluation workflows for AI-generated conclusions;
- historical-case replay using sanitized inputs.

## Prohibited first-round workflows

Do not use Founding Beta as the sole or primary authority for:

- medical diagnosis or treatment;
- emergency or physical-safety control;
- legal adjudication or legal advice relied upon without qualified review;
- hiring/firing or other high-impact employment decisions;
- credit, insurance, lending or financial eligibility decisions;
- execution of trades or material financial transfers;
- law-enforcement or surveillance decisions;
- access-control decisions where an error could create serious harm;
- autonomous actions that cannot be stopped by a human;
- workflows requiring sensitive personal data in round 1.

## Conditional workflows

A workflow may be accepted only after additional review if:

- the consequence is material but reversible;
- the evidence set contains confidential company data;
- provider data-routing is non-trivial;
- regulatory obligations may apply;
- the workflow requires integration with production systems.

## Per-company intake questions

Before accepting a workflow, record:

1. What decision/action follows the AI conclusion?
2. What is the worst plausible consequence of a wrong result?
3. Can a human stop or override the action?
4. Can the input/evidence state be replayed?
5. What data categories are involved?
6. Which external model providers receive content?
7. Is the company authorized to submit that data?
8. What would count as a false stop?
9. What would count as a missed stop?
10. Who is the named human reviewer?

## Acceptance rule

If any answer is unclear, the workflow remains **NOT YET ACCEPTED** until clarified.

Unknown risk must not be silently converted into acceptable risk.
