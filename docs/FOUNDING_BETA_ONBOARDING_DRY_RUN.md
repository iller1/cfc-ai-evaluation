# CFC + HAWM Founding Beta — Onboarding Dry Run

## Purpose

Run this process internally before inviting the first company.

For the current dedicated Founding Beta v2 live path and exact expected synthetic checks, use `FOUNDING_BETA_NEW_COMPANY_WALKTHROUGH.md`.

The operator should behave as if they are unfamiliar with the project and should use only the materials intended for a beta participant.

## Test persona

Assume the participant:
- understands normal AI tools,
- has not worked on CFC,
- has one bounded workflow,
- wants to know whether an AI conclusion is sufficiently supported before action.

## Dry-run steps

### 1. Entry

- Open START HERE.
- Confirm the beta purpose is understandable in under 2 minutes.
- Confirm experimental status is visible.
- Confirm human-final-control requirement is visible.

Record time, unclear terms, and questions that arise.

### 2. Account / access

- Open the beta application.
- Sign in/onboard.
- Create or select a workspace.
- Create a conversation/case.

Record time-to-access, failed steps, and confusing labels.

### 3. Example workflow

Use FOUNDING_BETA_EXAMPLE_WORKFLOW.md.

- enter/capture the AI conclusion,
- preserve the relevant evidence state,
- save HAWM state if required,
- run the applicable CFC/control step,
- inspect the result.

Record time-to-first-complete-case and whether the user can explain the result in their own words.

### 4. Replay / observability

Without relying on memory:
- find the saved case,
- identify version/context,
- identify model/provider result if relevant,
- identify the control result,
- identify any provider failure separately,
- reproduce/replay where supported.

Record any information that cannot be reconstructed.

### 5. Feedback

Use the Founding Beta feedback issue form.

Submit a synthetic test finding containing version, workflow, case ID, expected behavior, observed behavior, minimal evidence-state summary, classification, and reproducibility.

Do not submit sensitive data.

### 6. Exit / support

Verify the participant can find limitations, feedback route, support/contact route once defined, data/privacy summary, and explanation of what to do when a case remains unresolved.

## Measurements

- TIME_TO_FIRST_ACCESS
- TIME_TO_FIRST_CASE
- TIME_TO_FIRST_CONTROL_RESULT
- TIME_TO_SUBMIT_FEEDBACK
- NUMBER_OF_OPERATOR_INTERVENTIONS
- NUMBER_OF_UNCLEAR_TERMS
- NUMBER_OF_BLOCKING_ERRORS

## Pass criteria for internal dry run

A dry run passes when:

- the test user can complete one example case;
- no frozen-baseline modification is needed;
- the result and provenance can be reconstructed;
- feedback can be submitted;
- limitations are visible;
- no sensitive data is required;
- no blocking product defect remains.

## External usability status

An internal dry run is not external usability validation.

It only establishes that the onboarding path is coherent enough to invite an external participant.
