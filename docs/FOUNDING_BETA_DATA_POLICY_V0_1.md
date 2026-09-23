# CFC + HAWM Founding Beta — Round-1 Data Policy v0.1

**Status:** operational beta policy draft for internal approval.
**Not legal advice.**

## Purpose

This document defines the minimum data boundary for the first Founding Beta round.

The goal is to keep early customer workflows low-risk, reproducible and inspectable while legal/privacy work remains incomplete.

## Round-1 default rule

Until a reviewed privacy notice, retention policy and deletion process are finalized:

**Do not accept sensitive, special-category, regulated, secret, or unnecessary personal data.**

Prefer:
- synthetic data,
- public data,
- anonymized/pseudonymized low-risk examples,
- company-authorized non-sensitive operational data.

## Data that must not be submitted in round 1

- passwords or credentials,
- API keys,
- access tokens,
- payment-card data,
- medical/health records,
- biometric data,
- criminal-history data,
- highly sensitive employee records,
- legal privileged material,
- trade secrets unrelated to the bounded test,
- production secrets not required for reproduction,
- personal data not necessary for the workflow.

## Allowed minimum record

A Founding Beta case should contain only what is needed to reproduce the control decision:

- workspace / company identifier,
- workflow identifier,
- case identifier,
- product version,
- input/evidence-state references or summaries,
- model/provider metadata where relevant,
- control result,
- user feedback,
- timestamps.

## Provider boundary

If a workflow sends content to an external model provider, the participating company must know that the provider receives that content.

Before onboarding, document for each workflow:
- provider used,
- whether provider-side retention/training controls are relevant,
- whether the company is authorized to send that data to the provider.

## Storage boundary

Current product storage includes persisted application records used for replay, debugging, benchmark/provenance work, and beta support.

Exact production storage regions and infrastructure disclosures must be verified before external onboarding.

- Hosting/data location: TO VERIFY
- Backup behavior: TO VERIFY
- Encryption-at-rest disclosure: TO VERIFY
- Operator access boundary: TO DOCUMENT

## Retention

Round-1 retention period: TO DECIDE

The chosen period should be the shortest period that still permits replay, debugging, regression testing, and agreed support.

## Deletion

Before onboarding the first company, define:
- who can request deletion,
- how identity/ownership is verified,
- what records are deleted,
- whether backups age out separately,
- expected completion time,
- how deletion is confirmed.

Deletion procedure: TO IMPLEMENT / DOCUMENT

## Access

Access to customer beta records should be limited to the customer/workspace user(s) permitted by the beta account model and the minimum project operators required for support and debugging.

Operator-access logging/process: TO DOCUMENT

## Incident handling

Before paid onboarding, publish support and security/privacy incident contacts plus an expected acknowledgement process.

Incident contact: TO DECIDE

## Round-1 consent

Each company must explicitly acknowledge that:
- this is an experimental beta,
- human review remains required,
- independent validation remains open,
- only approved low-risk data/workflows may be submitted,
- logs may be retained for the agreed beta retention period,
- provider APIs may receive workflow content where applicable.

## Gate

No external company should be onboarded until all TO DECIDE, TO VERIFY, and TO IMPLEMENT items that materially affect that company's data are resolved.
