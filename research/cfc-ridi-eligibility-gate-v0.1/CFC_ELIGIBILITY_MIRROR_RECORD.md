# CFC ↔ RIDI Eligibility Gate v0.1 — CFC-side exact-byte mirror record

**Mirror date:** 2026-09-29  
**Mirror status:** PUBLIC / EXACT-BYTE COPY OF RIDI FROZEN RECORD AND ARTIFACTS  
**Mirror repository:** `iller1/cfc-ai-evaluation`  
**Mirror branch:** `freeze/cfc-ridi-eligibility-gate-v0.1`  
**Mirror directory:** `research/cfc-ridi-eligibility-gate-v0.1/`  
**Base branch:** `freeze/cfc-ridi-annexes-v0.1` (base commit `61368b2041e161a8475ea5318d93dfae1f2edbd9`)

## Authority and chronology

The authoritative bilateral eligibility-gate freeze was first recorded in `adeebnoor/ridi`, branch `freeze/cfc-ridi-eligibility-gate-v0.1`:

- RIDI bilateral freeze-record commit: `9225552ff0032bba2aeaa7d8a1f75fc8a46922a9`
- RIDI frozen SHA256 manifest commit: `1de01a08cc4c30e94d4e9b12a657327723a603c3`
- Source directory: `collaboration/cfc-ridi/substantive-v0.1/`
- Freeze date as recorded by RIDI: 2026-09-28.
- Parent Shared Case Protocol v0.1 SHA-256: `d6bc94e90be4ac01bd8ee60f32aa3045dd827f4f3e9e64a68b82191615138571`.

The CFC copy is subsequent provenance mirroring. It does not retroactively precede or replace the RIDI-side bilateral freeze.

## Four frozen artifact identities

| Relative file path in this mirror directory | SHA-256 of exact UTF-8 bytes | Git blob SHA (same in RIDI and CFC) |
|---|---|---|
| `ELIGIBILITY_CRITERIA_DRAFT.md` | `b766a0452af82343fe7ee33dbe8dfb7ccb0a1d557f6d0ccaf14676eefb827e8a` | `9392e8b4241bc5bf308c380607675d3a8641b214` |
| `candidate_registry_TEMPLATE.tsv` | `12992e3c8591d41dc2dc38de0ebe46e8c491d3a39e242d6021286e1815b5fd29` | `a27549f3b182b42be6e2cf828785cf0784b84450` |
| `eligible_pool_TEMPLATE.tsv` | `128a74efb1921e6c57a6cc02145b6e8facf1ff40c9dde36fd62b950cdc7d4f26` | `7db73a5d0534cda97bda1210816e4704f84c4222` |
| `tools/eligibility_check.py` | `96ca16e12e3f2fecb5a06998eb28476e250b2a0965f2b26713da298391958904` | `d3df8cb5bc1fa9e024e98b9d728e2c03077351cd` |

SHA-256 digests of the four source files were independently recomputed and matched the RIDI frozen manifest before mirroring. Exact Git blob identities are to be checked again on the CFC branch after committing this record.

The previously proposed checker SHA-256 `c5e7cc59ed1c80b932917469d06b0149835a46c020576422052d703f3227ab44` is **superseded** and is not frozen.

## Original provenance evidence copied without modification

- `ELIGIBILITY_GATE_FREEZE_RECORD.md`: exact-byte copy of the RIDI bilateral record; source Git blob `9eb33458cc58bb3c485ed685bf2d1201067bf44d`.
- `ELIGIBILITY_SHA256SUMS_FROZEN.txt`: exact-byte copy of the RIDI manifest; source Git blob `bdd0e256c0043318562caa5712a04f7d12dc80c5`. Its listed file paths are deliberately the original RIDI paths, **not** paths under this CFC mirror.
- `ELIGIBILITY_CRITERIA_DRAFT.md` retains its original internal heading/status verbatim. The later bilateral freeze record freezes that named file by exact bytes and SHA-256; altering the internal heading here would destroy the byte-identical mirror.

## Boundary and next permitted work

This branch mirrors provenance only. It does **not** modify the frozen CFC controller, frozen wrapper, earlier CFC↔RIDI protocol, M1/A1/I1 annexes, or substantive methodology.

At the RIDI eligibility-gate freeze, candidate registry rows = 0; eligible pool rows = 0; substantive selection seed = none; substantive execution = none. Creating this CFC mirror does not add any such records or run a substantive case.

Only after this mirror is public may real candidate registrations be constructed and audited under the frozen checker. A candidate registry is not an eligible pool. Pool freeze precedes seed commit–reveal, selection, independent raw outputs and interpretation.

Any byte-level change to the four frozen artifacts requires a new version/hash and renewed bilateral approval, not an in-place edit of this freeze.
