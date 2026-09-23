# CFC + HAWM Founding Beta — Release Checklist

This checklist converts the working Founding Beta plan into an operational gate.

## A. Product freeze

- [ ] Name the beta release version.
- [x] Record exact candidate commit: `ee97145277de61a81be981058a1ad520ef108441`.
- [ ] Record exact Integration Layer version.
- [ ] Record frozen Anchor/controller identities.
- [ ] Confirm no frozen artifact changed.
- [x] Run Pro Beta contract/auth/persistence/PostgreSQL/frontend suite — GitHub Actions run `35871943953`: SUCCESS.
- [x] Re-run same suite on Postgres 18 (matching production major) — GitHub Actions run `35873169764`: SUCCESS.
- [ ] Confirm production health.
- [ ] Confirm database persistence and replay.

## B. Onboarding

- [x] START HERE exists.
- [x] Limitations document exists.
- [x] Example workflow exists.
- [x] Feedback protocol exists.
- [x] Select one real feedback channel — structured GitHub Founding Beta issue form (non-sensitive reports only).
- [ ] Run onboarding once as if we were a new company.
- [ ] Measure time-to-first-use.
- [ ] Record onboarding friction.

## C. Observability

- [ ] Confirm version is stored with each relevant external beta case.
- [ ] Confirm input/evidence state can be reconstructed.
- [ ] Confirm control result can be reconstructed.
- [ ] Confirm provider failures are distinct from semantic outcomes.
- [ ] Confirm audit/log retention works after redeploy.
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

- [x] Working data/terms draft exists.
- [ ] Choose retention duration.
- [ ] Define deletion process.
- [ ] Define access roles.
- [ ] Confirm hosting/data locations relevant to customer disclosure. Railway currently reports region code `sfo` for frontend/API/Postgres; customer-facing geography still TO VERIFY.
- [x] Decide whether personal data is permitted in round 1 — default policy: no unnecessary personal/sensitive data; synthetic/public/authorized low-risk data preferred.
- [ ] Produce final privacy notice before paid onboarding.

## F. Commercial

- [ ] Confirm Founding Beta price.
- [ ] Choose billing mechanism.
- [ ] Confirm contracting entity/jurisdiction.
- [ ] Confirm tax/VAT handling.
- [ ] Finalize beta terms.
- [ ] Define support contact and expectations.

## G. First-user gate

- [ ] At least 3 genuinely engaged companies identified.
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
