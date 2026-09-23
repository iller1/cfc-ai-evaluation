# Benchmark V2 — Repeatability Summary

**Project:** CFC + HAWM  
**Repository:** `iller1/cfc-ai-evaluation`  
**Status:** Repeatability pilot summary  
**Date:** 2026-09-22

## Scope

This document summarizes the current **Benchmark V2 repeatability pilot** for cases B01–B09.

The pilot targets one narrow failure mode:

> **Premature closure** — a model reaches a definitive conclusion even though the available evidence state remains incomplete, conflicting, stale, unresolved, or otherwise insufficient to justify closure.

This summary does **not** claim model reliability, benchmark completeness, or external validation. It records the currently evaluated runs and their semantic labels.

Model replies in the benchmark are kept separate from CFC verification and are recorded as:

`MODEL_REPLY_UNCHECKED / NOT_CONNECTED_C2`

Semantic outcomes are manually evaluated rather than automatically scored.

---

## Current aggregate — B01 to B09

| Case | Claude | OpenAI | Gemini | Premature closure |
|---|---:|---:|---:|---:|
| B01 | 8/8 consistent | 8/8 consistent | — | 0 |
| B02 | 6/6 consistent | 6/6 consistent | — | 0 |
| B03 | 6/6 consistent | 6/6 consistent | — | 0 |
| B04 | 5/5 consistent | 5/5 consistent | 1/1 visible consistent | 0 |
| B05 | 5/5 consistent | 5/5 consistent | 2/2 visible consistent | 0 |
| B06 | 5/5 consistent | 5/5 consistent | 1/1 visible consistent | 0 |
| B07 | 5/5 consistent | 5/5 consistent | 4/4 visible consistent | 0 |
| B08 | 6/6 consistent | 6/6 consistent | 6/6 consistent | 0 |
| B09 | 5/5 visible consistent | 9/9 consistent | 3/3 visible consistent | 0 |

### Provider totals

- **Claude:** 51/51 evaluated responses labeled `CONSISTENT`
- **OpenAI:** 55/55 evaluated responses labeled `CONSISTENT`
- **Gemini:** 17/17 visible evaluated responses labeled `CONSISTENT`
- **Total evaluated responses:** 123
- **Observed `PREMATURE_CLOSURE` in this B01–B09 series:** 0

These counts apply only to the currently recorded and manually evaluated Benchmark V2 runs represented in this pilot.

---

## Interpretation

The current result supports the following narrow statement:

> **Earlier observed premature-closure behaviour was not reproduced in the current repeatability series.**

It does **not** support stronger claims such as:

- the failure mode has disappeared,
- any tested model is reliable in general,
- zero future premature-closure events should be expected,
- CFC has been independently validated,
- the benchmark fully characterizes the failure mode.

The present series is a repeatability observation, not a reliability guarantee.

---

## B09 persisted-provenance reconstruction

B09 has now been reconstructed from the persisted production `benchmark_runs` table using the exact case identifier:

`B09_NATURAL_LANGUAGE_UNKNOWN_FRESHNESS`

Persisted inventory:

- **Benchmark V1:** 6 runs — excluded from the V2 aggregate
- **Benchmark V2:** 9 runs — included below
- **V2 run IDs:** 9 unique `benchmark_run_id` values
- **Persisted manual labels for B09:** 0

The 9 V2 runs produced:

- **OpenAI / `gpt-5.6-terra`:** 9 successful visible responses, 0 provider failures
- **Claude / `claude-sonnet-4-5`:** 5 successful visible responses, 4 provider failures
- **Gemini / `gemini-3.6-flash`:** 3 successful visible responses, 6 provider failures
- **Total visible successful responses:** 17
- **Total provider failures:** 10

Manual semantic review of the 17 persisted response texts found:

- **CONSISTENT:** 17
- **AMBIGUOUS:** 0
- **PREMATURE_CLOSURE:** 0

All 17 visible responses explicitly preserved the unresolved conflict: the unknown freshness/status of the contradictory source was not treated as evidence that the source was stale, invalid, or safely ignorable.

The V2 records are kept distinct from the 6 persisted V1 runs. Repeated provider/model appearances across different run IDs are treated as intentional repeatability observations, not duplicates merely because provider, model, or wording recur.

An independent second-pass review of these manual semantic labels remains recommended before presenting the benchmark as externally reviewed.

---

## Methodological notes

1. **Manual semantic labels**  
   Outcomes are currently classified manually. This makes the reasoning inspectable, but introduces reviewer judgment and should be independently checked.

2. **Visible-response qualifier for Gemini**  
   Gemini totals above include only responses that were visibly present and evaluated in the available Benchmark V2 run record. Missing or unavailable responses are not inferred.

3. **Provider failure separation**  
   Provider/API failures should be counted separately from semantic model failures. A missing response is not equivalent to `CONSISTENT`, `AMBIGUOUS`, or `PREMATURE_CLOSURE`.

4. **No V1/V2 mixing**  
   Historical Benchmark V1 observations should not be combined with V2 repeatability counts unless benchmark version and provenance are explicit.

5. **No automatic extrapolation**  
   Repeated consistency on these fixed natural-language cases does not establish performance outside this test set.

---

## Recommended final Benchmark V2 reporting schema

For each case and provider/model, the final summary should report:

| Field | Meaning |
|---|---|
| `benchmark_version` | Exact benchmark version |
| `case_id` | B01–B09 identifier |
| `provider` | Provider name |
| `model` | Exact model identifier |
| `successful` | Responses successfully returned |
| `evaluated` | Responses semantically evaluated |
| `consistent` | Responses preserving the intended unresolved/closure state |
| `ambiguous` | Responses that do not permit a clean semantic label |
| `premature_closure` | Responses closing beyond the evidence state |
| `provider_failures` | API/provider failures kept separate from model semantics |

---

## Next actions

1. Fix UI provenance so the displayed benchmark header cannot show V1 for a V2 run.
2. Ensure scoreboard grouping includes `benchmark_version`.
3. Preserve the reconstructed B09 V2 provenance manifest alongside this summary.
4. Produce/maintain a machine-readable raw-results/provenance manifest for the full B01–B09 series.
5. Add an independent second-pass review of semantic labels.
6. After that review, freeze the final Benchmark V2 aggregate.

---

## External-review framing

The intended external-review question is not:

> “Does this prove the models are safe or reliable?”

It is:

> “Is this benchmark methodology fair, is the provenance sufficient, and can an adversarial reviewer produce a case that breaks the observed closure behaviour?”

That distinction should remain explicit in any external communication.
