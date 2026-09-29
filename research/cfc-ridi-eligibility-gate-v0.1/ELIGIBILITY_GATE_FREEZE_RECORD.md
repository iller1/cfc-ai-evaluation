# CFC ↔ RIDI Eligibility Gate v0.1 — Bilateral Freeze Record

**Status:** BILATERALLY APPROVED / FROZEN  
**Freeze date:** 2026-09-28  
**Parent protocol SHA-256:** `d6bc94e90be4ac01bd8ee60f32aa3045dd827f4f3e9e64a68b82191615138571`

## Exact frozen artifacts

| Artifact | SHA-256 | Git blob SHA |
|---|---|---|
| `ELIGIBILITY_CRITERIA_DRAFT.md` | `b766a0452af82343fe7ee33dbe8dfb7ccb0a1d557f6d0ccaf14676eefb827e8a` | `9392e8b4241bc5bf308c380607675d3a8641b214` |
| `candidate_registry_TEMPLATE.tsv` | `12992e3c8591d41dc2dc38de0ebe46e8c491d3a39e242d6021286e1815b5fd29` | `a27549f3b182b42be6e2cf828785cf0784b84450` |
| `eligible_pool_TEMPLATE.tsv` | `128a74efb1921e6c57a6cc02145b6e8facf1ff40c9dde36fd62b950cdc7d4f26` | `7db73a5d0534cda97bda1210816e4704f84c4222` |
| `tools/eligibility_check.py` | `96ca16e12e3f2fecb5a06998eb28476e250b2a0965f2b26713da298391958904` | `d3df8cb5bc1fa9e024e98b9d728e2c03077351cd` |

The previously proposed checker SHA-256
`c5e7cc59ed1c80b932917469d06b0149835a46c020576422052d703f3227ab44`
is explicitly **superseded** and is not part of this freeze.

## Bilateral approval

**Krzysztof Sliwka** independently verified all four exact artifact hashes and the corrected strict-TSV checker behavior, confirmed the updated CI passed, and formally approved the exact four artifact versions above for bilateral eligibility-gate freeze with no further changes.

**Adeeb Noor** approves the same exact four artifact bytes and hashes for freeze.

## Frozen behavior

The frozen eligibility gate:

- distinguishes `UNKNOWN` original support requirement from `AUTHORITATIVE_1`;
- rejects `UNKNOWN` and `AUTHORITATIVE_GT1` for this bounded first experiment;
- binds source/specimen bytes, recorded offline endpoints and evaluation definition through immutable SHA-256 identities;
- detects repeated registration of the same A/B pair, including reversed ordering, through an order-independent pair fingerprint;
- does not treat sharing one arm/source record across otherwise distinct pairs as an automatic duplicate;
- applies a mechanical pre-selection eligibility procedure only;
- preserves ACCEPT/REJECT status and reason codes;
- does not execute CFC or RIDI, compare A/B downstream verdicts for equivalence, inspect hidden correctness, or rank cases by scientific interest;
- strictly rejects noncanonical TSV registry rows with extra fields, missing fields, embedded tab delimiters, blank rows or multiline/noncanonical shapes;
- computes each `registry_row_sha256` from the exact original UTF-8 registry-row bytes including the terminating LF.

## Verification

Strict-TSV correction CI:

https://github.com/adeebnoor/ridi/actions/runs/36356315694

Result: **PASS**

The correction includes negative regression tests for:
- extra fields;
- missing fields;
- embedded delimiters;
- exact source-row byte hashing.

## State at eligibility-gate freeze

At freeze:

- candidate registry rows: **0**
- eligible pool rows: **0**
- substantive case selected: **false**
- substantive selection seed created or revealed: **false**
- substantive pool frozen: **false**
- substantive CFC/RIDI run executed: **false**

The next permitted step is bilateral mirroring of this eligibility-gate freeze on the CFC side. Only after that mirror is recorded may real candidate registrations be constructed under these frozen rules.

Any byte-level modification to a frozen eligibility artifact requires a new version, new SHA-256, renewed bilateral approval and a new freeze record.
