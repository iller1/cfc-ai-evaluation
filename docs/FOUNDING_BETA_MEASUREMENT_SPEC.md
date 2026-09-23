# CFC + HAWM Founding Beta v2 — Measurement Spec

## Purpose

Founding Beta is an instrument for measuring CFC + HAWM behavior in real workflows.

The beta records **system behavior and human evaluation**, not customer business content.

## Persisted fields

The dedicated Founding Beta measurement record contains:

- `measurement_id`
- `workspace_id`
- `system_version`
- `workflow_type`
- `case_id`
- `cfc_result` — ALLOW / STOP / UNRESOLVED
- `reason_code`
- `hawm_state`
- `human_assessment` — AGREE / DISAGREE / UNSURE
- `final_action`
- `problem_type`
- `comment` — optional, short, anonymized
- `created_at`

## Explicitly absent

The measurement contract intentionally has no field for:

- customer document
- document text
- prompt
- full model response
- raw evidence content

The API rejects known customer-content field names.

## Problem classes

Supported first-round problem classes:

- NONE
- BUG
- USABILITY
- FALSE_STOP
- FALSE_ALLOW
- UPSTREAM_STATE_ISSUE

## Human comparison

The core comparison is:

`CFC/HAWM outcome -> human AGREE / DISAGREE / UNSURE -> final action`

This lets the beta measure where the system:
- stops correctly,
- allows correctly,
- stops too much,
- allows too much,
- communicates unclearly,
- receives a bad/incomplete upstream evidence state.

## Technical API

Workspace-scoped endpoints:

- `POST /api/workspaces/{workspace_id}/beta-measurements`
- `GET /api/workspaces/{workspace_id}/beta-measurements`

Ownership is enforced through the existing authenticated workspace boundary.

## Validation

The API/service layer fails closed on invalid:
- CFC result,
- human assessment,
- problem type,
- required fields,
- oversized fields/comments,
- explicit customer-content fields.

## Evidence

Latest validation on the Founding Beta branch:

- head: `eed1996fdde0e621d8a414f90c117cebbcef4234`
- GitHub Actions: `35898706059`
- PostgreSQL major: 18
- full Pro Beta contract/auth/persistence/PostgreSQL/frontend suite: SUCCESS

This is internal engineering evidence, not external validation.

## Ephemeral CFC path

The dedicated Founding Beta page does not persist customer source content.

Structured, non-content evidence state can be sent to:

- `POST /api/workspaces/{workspace_id}/beta-cfc-check`

The endpoint:
- enforces workspace ownership,
- rejects explicit customer-content field names,
- invokes frozen CFC Anchor through the structured mapping path,
- returns controller/presentation output,
- returns `persisted_customer_content: false`,
- does not create a message or HAWM free-text snapshot.

The dedicated frontend route is:

- `/founding-beta`

It intentionally omits legacy chat/model-send controls and exposes only structured technical state, CFC result, human assessment and minimal measurement.

Latest integrated validation:
- candidate head: `230a656e2535870887d1b633bffc5b4ef1693585`
- GitHub Actions run: `35899501928`
- PostgreSQL: 18
- result: SUCCESS
