# Benchmark V2 — Repeatability Summary

**Project:** CFC + HAWM  
**Repository:** `iller1/cfc-ai-evaluation`  
**Status:** Repeatability pilot summary  
**Date:** 2026-09-22

## Scope

This document summarizes the current **Benchmark V2 repeatability pilot** for cases B01–B08.

The pilot targets one narrow failure mode:

> **Premature closure** — a model reaches a definitive conclusion even though the available evidence state remains incomplete, conflicting, stale, unresolved, or otherwise insufficient to justify closure.

This summary does **not** claim model reliability, benchmark completeness, or external validation. It records the currently evaluated runs and their semantic labels.

Model replies in the benchmark are kept separate from CFC verification and are recorded as:

`MODEL_REPLY_UNCHECKED / NOT_CONNECTED_C2`

Semantic outcomes are manually evaluated rather than automatically scored.

---

## Current aggregate — B01 to B08

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

### Provider totals

- **Claude:** 46/46 evaluated responses labeled `CONSISTENT`
- **OpenAI:** 46/46 evaluated responses labeled `CONSISTENT`
- **Gemini:** 14/14 visible evaluated responses labeled `CONSISTENT`
- **Total evaluated responses:** 106
- **Observed `PREMATURE_CLOSURE` in this B01–B08 series:** 0

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

## B09 handling

**B09 is intentionally excluded from the aggregate above.**

The current B09 history contains provenance complications, including:

- historical/transitional V1-9 material,
- newer V2 material,
- at least one accidentally pasted duplicate,
- inconsistent Gemini presence across runs.

Because these records are not yet cleanly separated by benchmark version and persisted provenance, B09 should not be manually folded into a single aggregate number.

The correct next step is to reconstruct **B09 V2** from persisted benchmark history and count only records whose provenance is unambiguous.

This exclusion is deliberate and follows the same principle the benchmark is intended to test: unresolved provenance should not be silently converted into a definitive aggregate.

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
3. Reconstruct B09 V2 from persisted benchmark history.
4. Produce a machine-readable raw-results/provenance manifest.
5. Add independent/manual second-pass review of semantic labels.
6. Only after provenance cleanup, generate the final Benchmark V2 aggregate.

---

## External-review framing

The intended external-review question is not:

> “Does this prove the models are safe or reliable?”

It is:

> “Is this benchmark methodology fair, is the provenance sufficient, and can an adversarial reviewer produce a case that breaks the observed closure behaviour?”

That distinction should remain explicit in any external communication.
