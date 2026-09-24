# CFC + HAWM Founding Beta v2 — Retention Decision Record

## Operational retention decision

**14 days** for Founding Beta measurement records.

Owner decision date: **2026-09-24**.

The intent is:

`measurement -> short operational window -> aggregate retention report -> source measurement deletion`

The report is created before deletion in the same database transaction. If report creation or deletion fails, the transaction is rolled back rather than leaving a partial archive/delete state.

## Why 14 days

The beta measurement exists to support:
- short-cycle replay and debugging;
- regression-case creation;
- usability and false-stop / false-allow detection;
- product learning during a controlled beta.

Indefinite storage of individual measurement rows is not required for those purposes.

Fourteen days provides a bounded operational window while materially reducing accumulation.

## What is deleted after 14 days

The automatic rule applies to:
- Founding Beta measurement records;
- optional short measurement comments stored inside those records.

The age check is based on the measurement `created_at` timestamp.

## What is retained "on the shelf"

Before expired source rows are deleted, the system creates a **content-minimized aggregate retention report**.

The retained report may contain:
- source record count;
- first / last source timestamp;
- counts by system version;
- counts by workflow type;
- counts by CFC result;
- counts by human assessment;
- counts by final action;
- counts by problem type.

The retained report intentionally does **not** contain:
- user or workspace identity;
- measurement IDs;
- case IDs;
- comments;
- reason-code text;
- HAWM state text;
- customer documents, prompts, model replies or raw evidence.

This report exists for longitudinal product/research learning, not for reconstructing individual customer cases.

## Enforcement design

The production API process starts an internal retention worker.

Default settings:
- retention period: **14 days**;
- check interval: **1 hour**;
- no extra Railway service is required.

A PostgreSQL transaction-scoped advisory lock prevents concurrent workers from producing duplicate reports for the same expired source rows.

The archive report insertion and deletion of the exact selected rows occur in one transaction.

## Self-service deletion remains separate

Workspace owners may still delete their Founding Beta measurements earlier through the existing authenticated deletion path.

Automatic 14-day retention is a maximum source-measurement lifetime, not a minimum waiting period.

## What this policy does not automatically cover

- account/workspace identity records;
- third-party model-provider records;
- Railway/PostgreSQL infrastructure backups;
- separately approved diagnostic exceptions;
- benchmark/internal engineering datasets not created from Founding Beta measurements.

These require separate provider/legal treatment.

## Legal gate

The 14-day operational decision is an owner/product decision and does not replace legal review.

UK counsel should still confirm:
- customer-facing retention/deletion wording;
- provider backup expiry wording;
- whether any contractual/accounting/security records require different treatment;
- whether the aggregate retention report should have its own long-stop retention period.
