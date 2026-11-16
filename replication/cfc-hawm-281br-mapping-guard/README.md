# CFC × HAWM — Mapping Guard v0: Local Synthetic API Integration

**Status:** Operator-reported local integration tests; **not independently reproduced**  
**Report date:** 2026-11-16  
**Evidence class:** Local PowerShell/HTTP observations from an isolated Windows/Python 3.14.7 environment  
**Release boundary:** This report publishes the observed test outcomes and reported file identifiers. The executable Mapping Guard, HAWM candidate, local state, event ledger and receipt are **not attached**.

## Question under test

Can a bounded, deterministic mapping guard reject a deliberately mismatched evidence label **before operator confirmation**, while allowing an aligned synthetic mapping through a guarded HAWM → frozen CFC handoff?

The immediate risk is **mapping provenance / semantics**: a JSON candidate can satisfy structural validation while its labels disagree with the source evidence text. A structurally valid mapping is not therefore a correct reading of a document.

This is a narrow synthetic-format experiment, **not** a general natural-language semantic validator.

## Frozen boundaries and implementation scope

- Frozen controller: **CFC Anchor 0.2.90rc1**; Operator Wrapper v1.23 remains separately frozen.
- Frozen Anchor wheel SHA-256 (operator reference): `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`.
- Engine SHA-256 returned in the local saved result: `77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`.
- Separate **candidate** HAWM backend was launched on **127.0.0.1:8769**, with its own isolated data directory.
- Mapping Guard v0 parses only an exact, controlled `E1:` / `E2:` synthetic source-text grammar containing `positive|negative` and `current|stale` labels. It checks source-row association, index uniqueness/range, exact text binding and consistency of those labels.
- For this v0, `independence_authority=NONE` is accepted as an input condition; `VERIFIED` is conservatively denied. **Actual independence is not established.**
- Unrecognised source formats require review; contradictory syntactic mappings are blocked.
- Guard checks were inserted at both **confirmation** and **pre-run fixture construction**. Two discovered direct CFC POST endpoints (`/api/cfc` and `/api/cfc/fixture`) were disabled **in the isolated candidate**. This does not establish exhaustive route/security coverage.

## Reported local test sequence

| Step | What was tested | Observed result | Important boundary |
| --- | --- | --- | --- |
| 281BR-M3-R1 | Existing native fixture validator, in isolation, given opposite labels | Both aligned and contradictory enumerated labels accepted; `SEMANTIC_GAP_REPRODUCED` | Isolated structural-validator call; source text was **not** passed to it |
| 281BR-M4 | Prototype guard against controlled strings and tampering | 6/6 test cases PASS | Regex-format consistency only |
| 281BR-M5 | Guard against locally stored HAWM synthetic rows | 5/5 PASS | Same-host operator test |
| 281BR-M7 | Import-safe guard core extraction | 5/5 PASS, no stdout on import | No server integration yet |
| 281BR-M9 | Guarded backend functions tested in memory with test doubles | 11/11 PASS, including changed polarity/validity/text, stale state and missing confirmation | Not an HTTP execution |
| 281BR-M11–M13 | Candidate source integrity, localhost bind, isolated server launch | Separate server started at `127.0.0.1:8769`; original HAWM not modified in reported steps | Source and local state remain private |
| 281BR-M14-R1 | Live HTTP attempt to use direct CFC bypass routes | Both HTTP **403**, with expected `DIRECT_CFC_*_DISABLED` errors; state and ledger unchanged | Checked only these two routes |
| 281BR-M15 | Live HTTP confirmation with source `POSITIVE/CURRENT` mislabeled `NEGATIVE/CURRENT` | HTTP **409**, `MAPPING_GUARD_BLOCKED: POLARITY_MISMATCH`; draft still pending; state and ledger unchanged; no CFC result | **One** negative live-API mapping case |
| 281BR-M16 | Live HTTP confirmation with correctly aligned `POSITIVE/CURRENT` labels | `CONFIRMED`; source-state hash and source-text bindings matched; state and ledger updated; no CFC run yet | Synthetically formatted source rows |
| 281BR-M17-R1/R2 | One guarded `/api/handoff/run` invocation and read-only inspection of saved result | Engine hash matched; claim `SUPPORTED`; `control_closure=false`; UI `UNRESOLVED`; 4 expected failed gates; evidence stored | A test-script gate-count assumption required correction/qualification |
| 281BR-M18 | Local evidence-preservation copy | Four copied files hash-matched their local sources; `EVIDENCE_PRESERVED_PASS` | **Local copy only**, not a public independent custody record |

### Selected API observations

**Direct route denial** (reported `281BR-M14-R1`):

```text
POST /api/cfc          -> HTTP/1.0 403 Forbidden
{"error": "DIRECT_CFC_ROUTE_DISABLED", "next_action": "Use confirmed guarded handoff"}

POST /api/cfc/fixture  -> HTTP/1.0 403 Forbidden
{"error": "DIRECT_CFC_FIXTURE_ROUTE_DISABLED", "next_action": "Use confirmed guarded handoff"}

STATE_UNCHANGED: True
LEDGER_UNCHANGED: True
```

**Mismatched evidence rejected before confirmation** (reported `281BR-M15`):

```text
CONFIRM_HTTP_STATUS: 409
CONFIRM_ERROR: MAPPING_GUARD_BLOCKED: POLARITY_MISMATCH
WRONG_MAPPING_DENIED: True
STATE_UNCHANGED_AFTER_DENIAL: True
LEDGER_UNCHANGED_AFTER_DENIAL: True
MAPPING_STILL_PENDING: True
NO_CFC_RESULT: True
STEP_281BR-M15: LIVE_MAPPING_DENIAL_PASS
```

**Aligned synthetic evidence accepted** (reported `281BR-M16`):

```text
MAPPING_CONFIRMED: True
STATE_HASH_BOUND: True
SOURCE_EVIDENCE_BOUND: True
STATE_UPDATED: True
LEDGER_UPDATED: True
NO_CFC_RESULT: True
STEP_281BR-M16: LIVE_CORRECT_MAPPING_PASS
```

**Guarded CFC integration** (reported `281BR-M17-R1/R2`):

```text
ENGINE_HASH_VERIFIED: True
CLAIM_SUPPORTED: True
CONTROL_CLOSURE_FALSE: True
HAWM_UNRESOLVED: True
STOP_TYPE_NONE: True
EXPECTED_FAILED_GATES_4: True
RESULT_STORED: True
PROTECTED_DATA_UNCHANGED: True

DECLARED_MANDATORY_GATES: 49
TOTAL_GATE_ENTRIES: 50
FAILED_GATE_COUNT: 4
EXPECTED_FAILED_GATES: True
RESULT_CONSISTENT: True
LAST_LEDGER_EVENT_VERIFIED: True
FILES_UNCHANGED: True
STEP_281BR-M17-R2: STORED_RESULT_PASS_GATE_COUNT_DISCREPANCY_IDENTIFIED
```

Four reported failed gates:

- `claim_specific_support_policy_valid`
- `decision_support_closure_valid`
- `no_critical_unresolved`
- `support_set_common_mode_coverage_valid`

**Gate-count qualification:** The initial M17 test script asserted that `raw.gates` would contain exactly 49 properties; it actually contained **50**. The saved result declares `mandatory_gate_count=49`. The subsequent *read-only* M17-R2 confirmed those counts and the expected four failed gates without rerunning CFC. The identity of the additional entry, and its relationship to the mandatory set, **has not been classified here**. Consequently the original M17-R1 overall verdict was `REVIEW_REQUIRED`, not retroactively changed to PASS; the reported integration observations are preserved as such.

## Local artifact identities (not publicly downloadable)

| Artifact | Operator-reported SHA-256 |
| --- | --- |
| `mapping_guard_core.py` | `55759FBB26E8BF17C582CA557FB438D3311A6652BFB5BB52B3C189EA43422CF8` |
| `app_guarded_api_candidate.py` | `EDDB8CA0B88D5CA76257B5BDC534F5C0FFAFD799C56D375E1F6E18D1045D7767` |

Local evidence directory created in M18: `CFC_HAWM_GUARDED_EVIDENCE_281BR_M18`, containing copies of the guarded API candidate, guard core, HAWM `state.json`, HAWM `ledger.jsonl`, and an unsigned `LOCAL_RECEIPT.json`. The receipt states `cp15_signed=false` and `third_party_attestation=false`.

The SHA-256 strings are **operator-reported identifiers**, not evidence that a GitHub reader possesses or can reproduce these exact files. This page is a *publication of a reported local experiment*, not a third-party certification, executable release or complete forensic transcript.

## Non-claims, limitations and next review

1. **No general document meaning validation.** Exact pattern checking does not establish the semantics, authenticity, relevance or provenance of business documents.
2. **No real independence attestation.** `DISTINCT` as a supplied fixture attribute is not proof that two records are independent.
3. **No exhaustive API security proof.** Two bypass routes were disabled and observed to return HTTP 403; other routes, concurrent mutations, process boundaries and adversarial threat models remain outside this test.
4. **No general successful closure claim.** The tested controller reported `SUPPORTED` for the single claim but `control_closure=false` and `UNRESOLVED` at presentation.
5. **No action authorization.** CFC epistemic closure is distinct from permission to execute an external action; **M6 remains HOLD** and Information Passport **CP-15 is NOT CONNECTED**.
6. **No independent replay or custody.** Only operator-captured console outputs are available in this report. Source code, complete state/ledger, executable runtime and signed evidence are not included. Distribution terms for frozen/private material remain unresolved.
7. **No production or customer-document claim.** A future Evidence Copilot interface and real-document mapping require separate evaluation.

### Specific questions for an independent reviewer

- Does the negative confirmation case actually test the intended trust boundary, or merely matching a constrained string grammar?
- Are other CFC execution paths reachable without guarded confirmation, including under concurrent state changes?
- Is source identity and mapping provenance bound strongly enough that a syntactically matching but misleading source cannot pass?
- Which of the 50 `gates` fields is outside the declared 49 mandatory checks, and where is that distinction formally defined?
- What additional artifacts and rights are required for independent executable reproduction?

Related: [Earlier bounded CFC × HAWM replay and stale-state HTTP report](../cfc-hawm-281aa-local-replay/README.md).

## Red-team follow-up — M21–M23 (2026-11-16)

**Status:** Additional **operator-reported** tests on the same isolated local HTTP candidate, not an independent external exploit validation. No controller source files were changed.

### Hypothesis and observed result

A source row can be **correctly parsed** as `NEGATIVE / CURRENT` while the overall fixture `conclusion` is `POSITIVE`. Mapping Guard v0 validates the source-text/row-label relationship, but **does not compare candidate `conclusion` with evidence polarity**. This is a **confirmed scope gap** in the mapping check. Whether a contradiction should be rejected at handoff, or deliberately handed to CFC for evaluation, remains a separate contract/design question.

| Step | Reported observation | Boundary |
| --- | --- | --- |
| **281BR-M21** | One synthetic `NEGATIVE / CURRENT` source row, submitted with candidate `conclusion=POSITIVE` and matching row polarity `NEGATIVE`, was confirmed through `POST /api/handoff/confirm`: **HTTP 200**, `mapping_draft.status=CONFIRMED`, contradiction stored, no CFC run | Shows a conclusion/evidence mismatch can be **confirmed**; not an unsafe CFC closure |
| **281BR-M22** | Exactly one `POST /api/handoff/run` against that confirmed case returned **HTTP 200** and an executed fixture containing `conclusion=POSITIVE` plus `evidence[0].polarity=NEGATIVE`, `validity=CURRENT` | Shows the mismatch traversed the guarded handoff and reached the frozen controller; HTTP 200 signals request success, not an authorized decision |
| **281BR-M22** | Frozen engine identity reference matched; CFC claim status **`QUARANTINED`**, `control_closure=false`, `stop_type=NONE`, HAWM projection **`UNRESOLVED`**, **9 false gate fields** | No unjustified closure was observed in this one case. The nine failed gates cannot all be causally attributed to the mismatch because this fixture also differs from M17 in evidence count and other conditions |
| **281BR-M23** | Before/after state and ledger, guarded API candidate and guard core were copied locally; six copied files matched operator-computed source SHA-256 digests; local receipt recorded | **Local preservation only**, not independent custody, third-party attestation or a published executable reproducer |

Selected operator console observations:

```text
STEP_281BR-M21: CONCLUSION_GAP_OBSERVED
CONFIRM_HTTP: 200
MAPPING_STATUS: CONFIRMED
CONTRADICTORY_MAPPING_CONFIRMED: True
CONTRADICTION_STORED: True
NO_CFC_RESULT: True

STEP_281BR-M22: OBSERVATION_CAPTURED
RUN_HTTP_STATUS: 200
ENGINE_IDENTITY_MATCH: True
CLAIM_STATUS: QUARANTINED
CONTROL_CLOSURE: False
STOP_TYPE: NONE
HAWM_DECISION: UNRESOLVED
FAILED_GATES_COUNT: 9
ACTUAL_FIXTURE: {"conclusion":"POSITIVE","required_independent_supports":1,"provenance_shape":"DISTINCT","independence_authority":"NONE","scope":"EXPECTED","evidence":[{"polarity":"NEGATIVE","validity":"CURRENT"}]}
LAST_LEDGER_EVENT: cfc_confirmed_handoff_run
STATE_CHANGED: True
LEDGER_CHANGED: True

STEP_281BR-M23: REDTEAM_EVIDENCE_PRESERVED_PASS
```

The nine reported false gate names in M22:

- `claim_specific_support_policy_valid`
- `claim_support_universe_common_mode_coverage_valid`
- `decision_relevant_relation_discovery_complete_valid`
- `decision_support_closure_valid`
- `no_critical_unresolved`
- `source_independence_semantics_valid`
- `support_relation_instance_resolution_coverage_valid`
- `support_selection_justification_valid`
- `support_set_common_mode_coverage_valid`

**Local M23 receipt SHA-256 (operator-reported):**
`F6BCF03B88BD02F9335C9FB58FDA64D3960A623EBB2D3255CDAB6EC09188C965`.

### Bounded red-team verdict

- **`CONCLUSION_EVIDENCE_GAP_OBSERVED`** — supported by operator-reported HTTP confirmation and subsequent stored executed fixture.
- **`UNJUSTIFIED_CFC_CLOSURE_NOT_OBSERVED`** — the controller reported `QUARANTINED` with `control_closure=false` in this case.
- **`SECURITY_BYPASS_OF_REQUIRED_EVIDENCE_MAPPING_NOT_ESTABLISHED`** — the guard's specified row-label checks still matched the source; whether candidate-level conclusion alignment belongs in this guard's contract is unresolved.
- **`INDEPENDENT_REPRODUCTION_NOT_DONE`** — the private source, state, ledger and receipt are not published here.

This does **not** justify claims that CFC is immune to adversarial input, that the guarded API is unbypassable, or that real business documents can be validated. It does provide a concrete next contract question: **should HAWM block contradictory overall conclusions before evaluation, or retain them as inputs for CFC to quarantine?**

### Po polsku — najważniejsze

W izolowanym teście lokalnym **błędne mapowanie zostało odrzucone przez HAWM (HTTP 409)**, a poprawne syntetyczne mapowanie zatwierdzono i przekazano do **niezmienionego CFC**. Dwie znalezione boczne ścieżki API zostały zablokowane (HTTP 403). Zamrożony CFC zwrócił `SUPPORTED`, ale **bez zamknięcia** (`control_closure=false`, `UNRESOLVED`). Wynik zachowano lokalnie. **Nie jest to jeszcze niezależny audyt, dowód poprawnego rozumienia dowolnych dokumentów ani uprawnienie do realnego działania.**

**Uzupełnienie red-team M21–M23:** HAWM zatwierdził przypadek z wnioskiem `POSITIVE` i syntetycznym dowodem `NEGATIVE / CURRENT` (HTTP 200), a sprzeczność przeszła do zamrożonego CFC. Kontroler zwrócił `QUARANTINED`, `control_closure=false` i `UNRESOLVED` (9 niezaliczonych pól bramek). **Potwierdzono lukę zakresu weryfikacji wniosku względem etykiet dowodu, nie potwierdzono nieuzasadnionego domknięcia CFC.** Pliki stanu sprzed/po, ledger i kod skopiowano lokalnie i porównano hashe — bez niezależnego poświadczenia.
