# CFC + HAWM Founding Beta v2 — Access Roles

## Principle

Access should be limited to the minimum required for beta operation, support and debugging.

## Role 1 — Participant workspace user

May:
- authenticate through the configured identity provider;
- access only owned workspaces;
- submit structured non-content state;
- run the dedicated Founding Beta CFC path;
- create/list/delete Founding Beta measurements for owned workspaces.

Must not:
- access another participant's workspace;
- use Founding Beta as sole authority for prohibited workflows;
- submit prohibited customer content through measurement/feedback fields.

## Role 2 — Project operator

Purpose:
- beta support;
- incident handling;
- debugging;
- release verification.

Operator access should be used only when needed and should avoid retrieving customer business content.

Before paid launch, define:
- named operators;
- how production access is granted/revoked;
- whether Railway/Postgres access is shared or individual;
- how operator access is logged/reviewed.

Current named operator list: **TO DECIDE**. Decision-ready operating procedure: `FOUNDING_BETA_OPERATOR_EMERGENCY_PROCEDURE.md`.

## Role 3 — Infrastructure / subprocessors

Systems currently relevant include:
- Railway;
- Clerk/authentication provider;
- customer-selected model providers where a BYOK workflow is used.

Their exact legal role and access boundary must be confirmed in the Privacy Notice / legal review.

## Ownership controls

The application enforces workspace ownership for Founding Beta measurement operations.

Cross-workspace access must fail closed.

## Secrets

Provider API keys and other secrets must not be persisted in the Founding Beta measurement contract.

Secrets must not be placed in feedback comments.

## Privileged access gate

Before paid launch:
- identify real project operators;
- use individual accounts where supported;
- enable available MFA/2FA;
- document emergency access — procedure prepared in `FOUNDING_BETA_OPERATOR_EMERGENCY_PROCEDURE.md`; named operator/backup confirmation remains open;
- document revocation/offboarding;
- record who is authorized to access production database/service configuration.

## Review

Access roles should be reviewed:
- before first paid company;
- after adding an operator;
- after an incident;
- when infrastructure/authentication changes.
