# CFC + HAWM Founding Beta v2 — New Company Walkthrough

**Status:** ready for external-style dry run.

## Goal

Run the complete Founding Beta path exactly as a first-time company would experience it, using synthetic or sanitized data only.

This walkthrough tests usability and operational readiness. It is not external validation of CFC or HAWM.

## Starting conditions

The tester should know only:
- this is an experimental Founding Beta;
- a human remains the final decision-maker;
- **NO CUSTOMER CONTENT BY DEFAULT**;
- the workflow is one bounded, low-risk case.

Do not explain internal implementation details unless the interface requires them.

## Walkthrough

### 1. Entry

Open the dedicated Founding Beta page.

Verify that the tester can identify:
- experimental status;
- human-final-control requirement;
- no-customer-content rule;
- basic flow from structured evidence state to CFC result and human assessment.

Record start time, unclear terms and first question asked.

### 2. Sign-in and workspace

- authenticate;
- create a new workspace with a non-sensitive name;
- select that workspace.

Record time to working workspace, authentication/workspace confusion and operator interventions.

### 3. First structured case

Use a synthetic case:
- Conclusion: POSITIVE
- Required supports: 1
- Scope: EXPECTED
- Provenance: DISTINCT
- Independence authority: NONE
- E1: POSITIVE / CURRENT
- E2: omitted

Run the Founding Beta CFC check.

Expected current presentation:
- Decision: ALLOW
- Claim state: VERIFIED
- reason equivalent to policy-satisfied support set;
- mapped input visible;
- customer content persisted: false.

This is a regression expectation for the current frozen anchor, not a general product guarantee.

### 4. Human measurement

Enter workflow type, a non-sensitive case ID, human assessment, final action, problem type and only an optional non-sensitive comment if genuinely needed.

Save measurement and verify:
- measurement appears in history;
- system version is visible;
- no document/prompt/model-response field exists;
- participant can understand what was stored.

### 5. Stop / unresolved case

Run a synthetic stale-evidence case:
- Conclusion: POSITIVE
- Required supports: 1
- Scope: EXPECTED
- Provenance: DISTINCT
- Independence authority: NONE
- E1: POSITIVE / STALE
- E2: omitted

Expected current presentation:
- Decision: STOP
- Claim state: UNRESOLVED
- reason equivalent to no referent-consistent epistemically available support;
- customer content persisted: false.

Ask the tester to explain in their own words why the case did not close.

### 6. History and deletion

- refresh Founding Beta measurement history;
- verify expected synthetic records;
- use a disposable workspace for deletion testing;
- delete that workspace's beta measurements;
- verify deleted count;
- verify `customer content deleted: 0`;
- refresh history and confirm no measurements remain in that disposable workspace.

Do not delete useful beta records from another workspace.

### 7. Retention explanation

The tester should be able to understand:
- source Founding Beta measurement rows have a maximum 14-day operational retention;
- an aggregate content-minimized report is created before automatic deletion;
- retained aggregate reporting excludes customer content, case IDs, comments, user/workspace identity and raw evidence;
- self-service deletion can happen earlier.

Do not make claims about infrastructure backup expiry that have not yet been project-specifically verified.

### 8. Support / limits

The tester should be able to find or be given:
- beta limitations;
- support/security contact;
- feedback route;
- what to do when a result is unresolved;
- statement that this is not certification, independent validation or sole high-risk authority.

## Metrics to record

- TIME_TO_FIRST_WORKSPACE
- TIME_TO_FIRST_CFC_RESULT
- TIME_TO_FIRST_SAVED_MEASUREMENT
- TIME_TO_FIND_HISTORY
- TIME_TO_DELETE_DISPOSABLE_MEASUREMENT
- OPERATOR_INTERVENTIONS
- UNCLEAR_TERMS
- BLOCKING_ERRORS
- NON_BLOCKING_FRICTION

## Pass criteria

Pass when:
- tester completes the flow without customer content;
- structured CFC result is understandable;
- human assessment remains distinct from controller result;
- measurement can be found and deleted;
- limitations are visible;
- no frozen artifact change is required;
- no blocking defect remains.

## Current known terminology boundary

The frozen Demonstrator presentation can show `Decision: STOP` with `Claim state: UNRESOLVED`.

The product documentation must not silently reinterpret that as a three-valued presentation decision. The claim state and presentation decision remain separate.
