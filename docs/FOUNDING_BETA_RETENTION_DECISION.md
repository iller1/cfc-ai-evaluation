# CFC + HAWM Founding Beta v2 — Retention Decision Record

## Proposed operational retention

**30 days** for Founding Beta measurement records.

Status: **proposed and documented, not yet technically enforced and not yet legally approved.**

## Why 30 days

The beta measurement exists to support:
- replay;
- debugging;
- regression-case creation;
- short beta-cycle product learning.

Indefinite storage is not necessary for that purpose.

Thirty days is intended to provide enough time for a normal beta feedback/retest cycle while materially limiting accumulation.

## What the 30-day rule applies to

- Founding Beta measurement records;
- optional short anonymized measurement comments.

## What it does not automatically cover

- account/workspace identity records;
- third-party model-provider records;
- infrastructure backups;
- separately approved diagnostic exceptions;
- benchmark/internal engineering datasets not created from customer Founding Beta content.

These require separate policy/legal treatment.

## Current enforcement status

User/workspace deletion exists.

Automatic age-based deletion is **NOT YET IMPLEMENTED**.

Therefore:
- 30 days must not be advertised as a guaranteed automatic deletion period yet;
- paid launch remains blocked until enforcement/operations and provider backup behavior are resolved.

## Implementation options

Preferred:
- periodic scheduled deletion of measurements older than the approved retention period;
- auditable cleanup result;
- tests covering cutoff boundaries.

Fallback for an early controlled beta:
- documented manual cleanup schedule;
- operator checklist;
- deletion evidence.

The fallback should only be used if legal review accepts it and the very small beta size makes it operationally credible.

## Legal gate

UK counsel should confirm:
- whether 30 days is appropriate for the stated purpose;
- wording for deletion and backup expiry;
- whether any records must be kept longer for contractual/accounting/security reasons.
