# CFC + HAWM Founding Beta — Release Checklist

This checklist converts the working Founding Beta plan into an operational gate.

## A. Product freeze

- [x] Name the beta release candidate: `Founding Beta RC1`.
- [x] Record exact candidate commit: `230a656e2535870887d1b633bffc5b4ef1693585`.
- [x] Record exact Integration Layer version: `v0.4 RC`.
- [x] Record frozen identities: Operator Wrapper `v1.23`; CFC Anchor `0.2.90rc1`; Demonstrator `v1.0`.
- [x] Confirm no frozen artifact changed in the Founding Beta measurement implementation.
- [x] Run Pro Beta contract/auth/persistence/PostgreSQL/frontend suite — GitHub Actions run `35871943953`: SUCCESS.
- [x] Re-run same suite on Postgres 18 (matching production major) — GitHub Actions run `35873169764`: SUCCESS.
- [x] Content-free Founding Beta measurement path + tests — GitHub Actions run `35898706059`: SUCCESS.
- [x] Dedicated no-customer-content `/founding-beta` page + ephemeral structured CFC path — GitHub Actions run `35899501928`: SUCCESS.
- [x] Confirm current Railway production health — all five services latest deployment status SUCCESS on 2026-09-23; dedicated Founding Beta v2 frontend/API path is deployed live.
- [x] Confirm measurement database persistence/ownership through Postgres 18 integration tests; end-to-end live beta replay remains part of onboarding dry-run.

## B. Onboarding

- [x] START HERE exists.
- [x] Limitations document exists.
- [x] Example workflow exists.
- [x] Feedback protocol exists.
- [x] Select one real feedback channel — structured GitHub Founding Beta issue form (non-sensitive reports only).
- [x] Run onboarding once as if we were a new company on the dedicated `/founding-beta` path — live synthetic dry run completed 2026-09-23 with STOP/SUPPORTED, ALLOW/VERIFIED, and STOP/UNRESOLVED outcomes recorded.
- [ ] Measure time-to-first-use — a fresh external-style live walkthrough was completed 2026-09-25 through check, save, refresh/history, and deletion; exact step timings were not captured, so timing metrics remain open.
- [x] Record onboarding friction — required non-sensitive `case_id` was not clearly signposted; UI validation/labeling was fixed and redeployed. Read-only mapped-input diagnostics were also added during the dry run.

## C. Observability

- [x] Confirm version is stored with each Founding Beta measurement (`system_version`).
- [x] Confirm Founding Beta measurement path does not require customer content; only non-content state/reason codes are persisted.
- [x] Confirm control result is persisted as `ALLOW / STOP / UNRESOLVED` plus `reason_code`.
- [x] Confirm existing benchmark provider failures remain separate from semantic outcomes; Founding Beta measurement schema records product outcome/problem class separately.
- [x] Confirm live measurement persistence across refresh after redeploy — verified 2026-09-25 with the same measurement remaining visible after `Refresh history`. Long-horizon automatic 14-day expiry remains covered separately by retention tests/worker evidence rather than this short walkthrough.
- [ ] Confirm an operator can replay one historical beta case end-to-end.

## D. Safety boundary

- [x] Experimental status is explicit.
- [x] External validation remains an open claim.
- [x] Human final control is explicit.
- [x] High-risk sole-use is prohibited.
- [x] Frozen baseline rule is explicit.
- [x] Choose allowed workflow classes for first companies — see `FOUNDING_BETA_WORKFLOW_POLICY.md`.
- [x] Choose prohibited workflow classes for first companies — see `FOUNDING_BETA_WORKFLOW_POLICY.md`.

## E. Data/privacy

- [x] Architecture rule: **NO CUSTOMER CONTENT BY DEFAULT**; dedicated measurement API has no document/prompt/model-response fields.

- [x] Working data/terms draft exists.
- [x] Retention duration set to 14 days for Founding Beta measurement records; automatic aggregate-report-then-delete enforcement is live in production (API commit `06ccbef5d1027627af7a2f687e66d6bf28a9782a`, Railway deployment `08ba2c70-12c9-4e0a-96f4-cac234124e80`, CI run `#259`: SUCCESS). Customer-facing legal wording and provider backup behavior remain subject to external verification/legal review.
- [x] Define deletion process — authenticated workspace purge + operator-assisted SOP in `FOUNDING_BETA_DELETION_SOP.md`; live deletion dry run on 2026-09-24 deleted exactly 1 synthetic measurement, reported `customer content deleted: 0`, and left the workspace history empty after refresh.
- [x] Define access roles — participant/workspace user, project operator, infrastructure/subprocessors in `FOUNDING_BETA_ACCESS_ROLES.md`; named operators and production-access procedure remain open.
- [ ] Confirm hosting/data locations relevant to customer disclosure. Railway currently reports region code `sfo` for frontend/API/Postgres; customer-facing geography still TO VERIFY.
- [x] Decide whether personal data is permitted in round 1 — default policy: no unnecessary personal/sensitive data; synthetic/public/authorized low-risk data preferred.
- [ ] Produce final privacy notice before paid onboarding.

## F. Commercial

- [x] Confirm Founding Beta price: £10/month as an engagement filter, not target valuation.
- [ ] Choose billing mechanism — decision note prepared in `FOUNDING_BETA_BILLING_DECISION.md`; owner/legal/accounting confirmation remains.
- [ ] Confirm contracting entity/jurisdiction.
- [ ] Confirm tax/VAT handling.
- [ ] Finalize Founding Beta Terms / Beta Agreement and obtain UK SaaS/data-protection/AI legal review before paid launch.
- [x] Define support contact and expectations — `krzysztofsliwka@yahoo.co.uk`; reasonable-efforts beta support, no SLA.

## G. First-user gate

- [ ] At least 3–5 genuinely engaged companies identified for initial start (up to 10 in first group) — recruitment package/runbook ready.
- [ ] Each company has one bounded workflow.
- [ ] Each company accepts beta limitations.
- [ ] Each company has a named human reviewer.
- [ ] No first-round workflow depends on CFC + HAWM as sole high-risk authority.

## H. Round-1 success evidence

Track:
- actual usage, not expressions of interest;
- reproducible defects and boundary findings;
- recurring needs across independent companies;
- retention into the next round;
- case studies including what failed and what changed.

## Independent review status

Independent human review is desirable evidence but is not treated as a launch blocker for a clearly labeled experimental Founding Beta.

Its absence must remain explicit and must not be converted into a claim of validation.
