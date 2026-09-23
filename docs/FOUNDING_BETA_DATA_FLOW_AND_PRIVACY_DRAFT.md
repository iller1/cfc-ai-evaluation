# CFC + HAWM Founding Beta v2 — Data Flow & Privacy Draft

**Status:** working draft for operational and UK legal/privacy review.  
**Not legal advice and not a final Privacy Notice.**

## Core design

Founding Beta is designed around:

**USE THE DOCUMENT. DON'T COLLECT THE DOCUMENT.**

**NO CUSTOMER CONTENT BY DEFAULT.**

The dedicated Founding Beta path does not provide fields for customer documents, full prompts, full model replies or raw evidence content.

## Intended flow

1. Customer data/document remains under customer control.
2. If AI analysis is required, content is handled locally or sent directly to the customer's chosen model/provider according to the agreed workflow.
3. The customer/operator converts the relevant outcome into structured, non-content evidence state.
4. CFC evaluates whether closure is justified.
5. HAWM/presentation layer surfaces ALLOW / STOP / UNRESOLVED.
6. Human makes the final decision.
7. CFC + HAWM stores only the minimal Founding Beta measurement.

## Measurement data stored

- workspace identifier
- system version
- workflow type
- non-sensitive case identifier
- CFC result: ALLOW / STOP / UNRESOLVED
- reason code / gate failure
- HAWM state/presentation code
- human assessment: AGREE / DISAGREE / UNSURE
- final action code
- problem classification
- optional short anonymized comment
- timestamp

## Customer content not intended for storage

The dedicated Founding Beta measurement path has no field for:
- customer document,
- document body,
- full prompt,
- full model reply,
- raw evidence text.

Known customer-content field names are rejected at the API boundary.

## Authentication and ownership

- authentication is delegated to the configured external identity provider;
- measurement data is workspace-scoped;
- read/write/delete operations enforce workspace ownership.

## Deletion

Authenticated workspace owners can delete all Founding Beta measurement records for their workspace through the dedicated deletion path.

Current implementation:
- DELETE /api/workspaces/{workspace_id}/beta-measurements
- returns the number of deleted measurement records.

This does not claim deletion from third-party model providers; provider-side data handling follows the provider/customer configuration and must be documented separately.

## Retention — proposed operational default

**Proposed, not yet legally approved:** 30-day rolling retention for Founding Beta measurement records unless a shorter customer-specific period is agreed.

Rationale: long enough for replay/debugging/regression during a short beta cycle while remaining materially shorter than indefinite retention.

Automatic retention enforcement is not yet implemented. Until it is, retention is an operational blocker for paid launch.

## Infrastructure facts currently verified

- hosting platform: Railway
- frontend/API/Postgres configuration reports Railway region code: `sfo`
- production database major: PostgreSQL 18
- database uses a private Railway network endpoint and persistent volume

Customer-facing geographic wording, backup behavior, encryption disclosures and subprocessors must be confirmed from current provider documentation before final Privacy Notice.

## Third parties to document

At minimum:
- Railway
- authentication provider (currently Clerk)
- any model provider used by the customer/BYOK workflow

Exact controller/processor roles require legal review.

## Rights / requests

Before paid launch, final documentation must specify:
- privacy contact,
- access/correction/deletion request process,
- identity verification process,
- response times,
- backup deletion/expiry behavior,
- complaint/escalation route.

## Legal review gate

This draft must be reviewed by a UK lawyer familiar with SaaS, data protection and AI before it is presented as the final Privacy Notice or contractual data policy.
