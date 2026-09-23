# CFC + HAWM Founding Beta — Readiness Matrix

Status date: 2026-09-23

This document tracks readiness against the working Founding Beta plan.

## Positioning

CFC + HAWM Founding Beta is an experimental decision-control layer for testing whether AI conclusions are sufficiently supported before action.

This is not a claim of external validation, certification, or general production safety.

## Readiness matrix

| Area | Target | Current state | Status |
|---|---|---|---|
| Users | 3–5 genuinely engaged companies to start; target 10 | Not yet recruited | BLOCKED ON EXTERNAL USERS |
| Product | Stable beta version with repeatable onboarding | Pro Beta frontend/API/Postgres deployed; benchmark and provenance persistence operating | PARTIAL / TECHNICALLY READY |
| Documentation | START HERE + limitations + example workflow | Founding Beta docs added in this package | READY FOR INTERNAL REVIEW |
| Feedback | One structured feedback path; every report includes version and context | Protocol and template added; product-side intake still to be wired or chosen | PARTIAL |
| Observability | Key decisions logged and replayable | Persisted benchmark runs, provider results/failures, manual-label storage, audit/persistence layers available | SUBSTANTIALLY PRESENT |
| Commercial | Simple payment + beta terms + data/privacy policy | Draft terms/data document added; payment mechanism and legal review not complete | NOT READY FOR PAID START |
| Frozen baseline | No silent controller changes | Frozen baseline remains unchanged | READY |

## Current release boundary

Founding Beta may proceed only as a controlled beta.

The system must not be represented as:
- externally validated protection,
- a certification mechanism,
- a sole basis for high-risk decisions,
- proof that tested models are generally reliable.

Human review remains the final decision authority.

## Benchmark status

Benchmark V2 currently records 123 manually evaluated visible responses across B01–B09 with 0 observed premature-closure events in the current repeatability series.

This is a repeatability observation, not an external validation claim.

B09 was reconstructed from persisted production history and has a provenance manifest. A blind second-pass review pack exists, but an independent reviewer has not yet been obtained.

## Gate to first company

Before onboarding the first external company:

1. Freeze a named Founding Beta release version.
2. Run the full release/regression suite on that version.
3. Confirm production health and persistence.
4. Publish START HERE, limitations, example workflow, feedback path and data terms.
5. Choose the exact support/feedback channel.
6. Complete minimum privacy/data-retention decisions.
7. Confirm that the first workflow is low-risk and bounded.
8. Record company consent to beta limitations.

## Gate to paid Founding Beta

In addition to the first-company gate:

- payment mechanism,
- beta terms,
- privacy/data policy,
- retention/deletion process,
- support expectations,
- billing/tax handling,
- legal review appropriate to the operating jurisdiction.

Until these are complete, the product should be treated as an experimental private beta rather than a fully commercial service.
