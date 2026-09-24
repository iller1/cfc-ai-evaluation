# CFC + HAWM Founding Beta v2 — Billing Decision Note

**Status:** recommendation prepared; owner decision and legal/tax confirmation remain open.

## Commercial assumption

Current Founding Beta price: **£10/month**.

Purpose: engagement filter, not final product valuation.

## Option A — Stripe Payment Link

Advantages:
- low implementation effort;
- hosted checkout;
- card handling stays with Stripe rather than the application;
- easy to stop or replace later;
- no need to build billing UI into Founding Beta.

Still to confirm: contracting entity/name on receipts, VAT treatment, cancellation/refund wording, recurring subscription vs one-off payment and whether Stripe must be added to privacy/subprocessor disclosures.

## Option B — manual invoice / bank transfer

Advantages:
- simplest for a very small number of companies;
- no billing integration;
- easy to handle 3–5 participants individually.

Disadvantages:
- more manual administration;
- invoice/VAT details still need to be correct;
- less convenient recurring collection.

## Option C — custom billing inside the product

Not recommended for Founding Beta. It adds code, security/compliance surface and support work without improving the core measurement goal.

## Working recommendation

Prefer **Stripe Payment Link if legal/accounting setup is ready; otherwise manual invoice for the first few companies.**

Do not build custom billing.

## Gate before taking money

Before paid activation confirm:
- legal review/terms adequate for the paid beta;
- contracting entity;
- VAT/invoicing position;
- cancellation/refund wording;
- support expectation;
- privacy/subprocessor disclosures relevant to the chosen payment route.

Until those are resolved, the £10/month figure remains a commercial plan rather than authorization to charge participants.
