# CFC + HAWM Founding Beta v2 — UK Legal Review Pack

## Purpose

This file is the handoff checklist for a UK lawyer familiar with SaaS, data protection and AI.

The goal is not to ask counsel to discover the product from scratch. The technical/product boundary should already be explicit.

## Product summary

Founding Beta is a small-company experimental beta whose primary purpose is measuring CFC + HAWM behavior in real workflows.

Human remains the final decision-maker.

The project intentionally separates:
- customer content,
- structured evidence state,
- frozen CFC control result,
- HAWM presentation,
- human assessment/final action,
- minimal product measurement.

## Core architecture to review

- USE THE DOCUMENT. DON'T COLLECT THE DOCUMENT.
- NO CUSTOMER CONTENT BY DEFAULT.
- dedicated Founding Beta page has no document/prompt/full-model-response field;
- structured CFC check is ephemeral;
- stored measurement contains only technical codes/metadata + optional short anonymized comment;
- workspace ownership applies to stored measurements;
- authenticated workspace purge exists;
- external model/provider handling may occur separately under BYOK/customer workflow.

## Documents for counsel

- FOUNDING_BETA_AGREEMENT_WORKING_DRAFT.md
- FOUNDING_BETA_DATA_FLOW_AND_PRIVACY_DRAFT.md
- FOUNDING_BETA_DATA_POLICY_V0_1.md
- FOUNDING_BETA_SECURITY_INCIDENT_SUPPORT_DRAFT.md
- FOUNDING_BETA_WORKFLOW_POLICY.md
- FOUNDING_BETA_LIMITATIONS.md
- FOUNDING_BETA_MEASUREMENT_SPEC.md
- FOUNDING_BETA_COMPANY_INTAKE.md

## Questions requiring legal answers

1. What is the correct contracting entity?
2. B2B-only beta or any consumer exposure?
3. Appropriate governing law/jurisdiction wording?
4. UK GDPR roles for project, customer, Railway, Clerk and model providers?
5. Is a DPA required for intended workflows?
6. What lawful-basis/privacy wording is appropriate for account/measurement data?
7. Are international-transfer terms/mechanisms required?
8. What must be disclosed about infrastructure regions/subprocessors?
9. What retention period is defensible for the measurement purpose?
10. Required response/process for access/deletion requests?
11. Required breach/incident notification commitments?
12. Appropriate limitation-of-liability/warranty language for experimental AI-control beta?
13. IP/confidentiality treatment for workflow feedback and derived regression cases?
14. VAT/invoicing obligations for £10/month UK/international B2B beta participants?
15. Cancellation/refund terms?
16. Any AI-specific disclosure or regulatory wording required for this scope?

## Technical evidence

Current branch: `founding-beta-v0.1`

Validated engineering components include:
- content-free Founding Beta measurement contract;
- Postgres 18 persistence and ownership;
- dedicated no-customer-content beta page;
- ephemeral structured CFC check using frozen Anchor;
- authenticated measurement deletion;
- regression tests.

Engineering validation is internal evidence only and must not be described as independent legal/security validation.

## Counsel completion gate

Paid onboarding stays blocked until:
- counsel-reviewed Beta Agreement,
- final Privacy Notice/data-flow,
- approved retention/deletion wording,
- approved liability/payment/cancellation terms,
- confirmed subprocessors/data-location wording,
- real support/security contacts.
