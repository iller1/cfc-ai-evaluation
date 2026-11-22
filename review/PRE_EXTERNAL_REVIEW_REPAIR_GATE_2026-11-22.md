# CFC / Evidence Copilot — Pre-external-review repair gate

**Date:** 2026-11-22  
**Purpose:** fix reproducible defects before inviting outsiders to review the *latest* candidate; do not add features or broaden claims.  
**Status:** OPEN — NOT A RELEASE APPROVAL.

## Immutable boundaries

- CFC Anchor 0.2.90rc1 and Operator Wrapper v1.23 are frozen; historical baselines and P74 ZIP remain unchanged.
- M6 DESIGN HOLD; end-to-end execution tests 0/6; CP-15 NOT CONNECTED.
- Evidence Copilot is **not integrated** with frozen CFC/HAWM and does not authorize actions.
- Latest P79–P81 packages have been tested in isolated local environments, but **not all candidate ZIPs are checked into this repository**. A reviewer cannot reproduce an unpublished package from status notes alone.

## Defect triage (no unsupported claims of resolution)

| ID | Observed or reviewer-reported problem | Evidence so far | Required before marking fixed |
|---|---|---|---|
| R-01 Context | Ollama input submission does not prove all document tokens were processed; `prompt_eval_count` not established in real-run logs | P77-B mock checks 6/6; local real Qwen runs; context coverage still NOT VERIFIED | Deterministic long-input and near-limit tests; capture model version/config, token telemetry, refusal and honest GUI wording |
| R-02 Unicode | JavaScript UTF-16 length may disagree with Python Unicode code-point length at 8k/100k bounds | P74 external review reported discrepancy; latest candidate status not retested | Reproduce on non-BMP and boundary-sized text through actual GUI/HTTP; patch only if confirmed; regression tests |
| R-03 HTTP | Local service host/origin restrictions, timeouts, concurrency and limits require checking | P73 limited route tests, not full security assessment | Explicit localhost-only bind, Host checks, bounded request handling, negative tests and clear local-only non-claims |
| R-04 Document injection | Untrusted document instructions may influence model answers or impersonate system boundaries | External reviewer concern, not resolved by P79 | Predeclared adversarial synthetic fixtures; refuse or disclose unsupported assertions; no assertion of general injection immunity |
| R-05 Duplicate execution | External reviewer reports mock executor invoked twice when repeated operation supplied with an empty execution history | Report requires original reproducer/logs; **not confirmed defect of frozen CFC** | Pin exact module/version, attempt ID and state; reproduce; specify mandatory durable ledger/idempotency responsibility; do not modify frozen Anchor |
| R-06 Mapping | A synthetic contradiction passed a limited upstream mapping guard before frozen CFC marked closure false and output unresolved | Operator-reported M21–M23 reproduction | Recheck upstream candidate/evidence alignment using negative fixtures; do not claim CFC unjustified closure |
| R-07 DOCX | Tracked changes / DTD / hidden text defects in P74 | P77-A isolated candidate 7/7 tests; Windows operator PASS | Confirm patch is present in reviewable distributed candidate and rerun hostile DOCX regressions |
| R-08 Quotes | P74 fabricated quote could be treated as a complete response | P79 local Windows 25/25 and one real Qwen quote PASS; quote matching is **not** semantic truth | Distribute exact candidate and tests; independent clean extraction/replay; keep semantic status unverified |
| R-09 Oracle | P81 has 12 author-labelled synthetic semantic cases | P81-R1 7/7 structural tests; P81-R2-A 4/4 blind package tests | External blind evaluation and adjudication; reference freeze remains HOLD |

## Repair protocol

1. Establish source identity and exact candidate hash for each reproduced defect.
2. Write a failing **negative** regression test for confirmed defects; keep original logs and original package.
3. Patch **only the unfrozen candidate**, smallest possible change; no feature expansion.
4. Rerun focused positives, negatives, previous regressions and package-manifest verification.
5. Log `CONFIRMED_FIXED`, `NOT_REPRODUCED`, `OPEN_LIMITATION`, or `REVIEW_REQUIRED` with exact commands, environment and output. Never write PASS just because an issue was described.
6. Package the exact source + tests + fixture inputs + checksums + reproduction instructions; distinguish operator reports from independent replication.

## External-review gate

A professor may receive a **research introduction** now with this issue register. Do not send the latest Evidence Copilot as a clean executable review package until its archive is actually available and an unfamiliar operator can reproduce the published instructions. Do not advertise production safety, generalized semantic understanding, downstream execution prevention or commercial readiness.

**Decision:** KNOWN-DEFECT REPAIR IN PROGRESS | CFC FROZEN | M6 HOLD | P81 REFERENCE FREEZE HOLD.

## PRR1 isolated repair candidate — Unicode character limits

- Original P80-derived `workspace.js` SHA-256: `6f3e6f525518f4a33813d7ac2ff350e9931b29dc7e7aa920ceef8d8adf95b0a9`.
- Reproduced static discrepancy: JS `.length` counts UTF-16 code units; Python `len(str)` counts Unicode code points for non-BMP characters.
- **Minimal repair:** use code-point length for GUI paste 100,000-character limit and document excerpt 420-character limit/preview. This is not a comprehensive Unicode or browser security audit.
- Isolated candidate artifact: `EVIDENCE_COPILOT_PRR1_UNICODE_REPAIR_CANDIDATE.zip`; SHA-256 `d942eae3d8744ae6f569688fb7341552adc94786a2e8f3c63d5a12a47575e790`. **Not uploaded to GitHub.**
- Assistant-local verification: Node syntax PASS; code-point unit test 11 assertions PASS; inherited Python regressions 29/29 PASS (P77-A 7, P77-B 6, P79 quote 9 + HTTP mock 3, P80 4); new archive file hashes 23/23 PASS.
- **Next gate:** Windows operator clean extraction / full test commands and GUI HTTP non-BMP boundary test. The code fix is **CANDIDATE**, not independently validated; do not mark R-02 resolved before that test.
- Frozen P74, frozen CFC and M6 were not changed.

## PRR1 Windows operator test — 22 Nov 2026

- User-run Windows PowerShell 5.1 log: `verify_prr1.py` returned `PRR1_OFFLINE_HASHES: PASS_23`; `node --check workspace.js` exit 0; `node test_prr1_unicode.js` returned `PASS_11`.
- Inherited regression suite: P77-A 7/7, P77-B mocked context 6/6, P79 unit 9/9, P79 mocked HTTP 3/3, P80 synthetic boundary 4/4; `PRR1_WINDOWS_REGRESSION: PASS`.
- **Gate remains open:** actual Chrome paste-path Unicode boundary test not yet shown. This confirms local unit/regression checks, not independent external replication, browser correctness or all input safety.

## PRR1 real local HTTP/GUI follow-up — 22 Nov 2026

- Operator selected a generated UTF-8 TXT containing 50,001 U+1F600 code points in the Chrome file picker; the UI displayed an unverified attachment (source trust status, not parse error). Browser import byte identity was **not** independently captured.
- First direct PowerShell POST returned `P71_ORIGIN_REFUSED` because the required localhost Origin header was absent. The helper mistakenly printed a PASS after the failure; **this line is invalid and excluded from evidence**. The server's origin guard was behaving as designed.
- Corrected PowerShell HTTP POST supplied `Origin: http://127.0.0.1:8780` and returned `extracted_length=50001`, `source_sha256=21e406b4c606239aa7e87147d096fb666f187786a2ec17978cb2ba6ea3ee895d`, `cfc_evaluated_document=false`; `PRR1_UNICODE_REAL_HTTP: PASS`.
- **R-02 state: LOCAL REPAIR VERIFIED for tested Unicode file-import boundary.** This does not prove all Unicode behavior, comprehensive browser-flow reexecution or independent replication. No change to frozen CFC/P74.
- **Next repair area:** R-01 Ollama context coverage; exact candidate telemetry and long-document negative tests still needed, no new features.

## PRR2 Ollama context diagnostics prepared — 22 Nov 2026

- Inspected current extracted PRR1 `document_ai_bridge.py` and `document_intake.py`. Existing controls: 8,000-codepoint AI bridge limit, `num_ctx=8192`, `num_predict=512`, `prompt_eval_count` required, refusal at configured pressure threshold, `model_context_coverage_verified=False` even for completed answers.
- Separate diagnostic-only package: `PRR2_CONTEXT_DIAGNOSTIC_CANDIDATE.zip`, SHA-256 `0f4b2adaa0c77cd5f26083639421c31ff63c0151edcb3412663ae53395521862`. **Not yet in GitHub; not a repaired or promoted product version**.
- Probe: negative 8,001-character refusal before model execution; real Ollama short (1,200) and near-limit (7,900) synthetic docs with unique trailing marker. Collect prompt tokens, finish, quote marker presence. The marker is merely a narrow functional observation, **not proof of all-context fidelity**. Source module is unmodified. Static script compile and synthetic lengths 3/3 pass in assistant environment.
- **PENDING:** operator Windows/Ollama runtime diagnostic; no claim of context coverage, semantic correctness, independent replication, or R-01 resolution.

## PRR2-R1 Windows real-Ollama diagnostic — 22 Nov 2026

Operator reports `qwen3:1.7b` via unchanged PRR1 bridge: source 8001 code points refused pre-model; short 1200 and near-limit 7900 sources accepted, prompt_eval_count 376 and 1533, respectively; finish_reason `stop`, model_complete True for both. **Trailing unique marker absent from answer in both cases.** Both runs still `model_context_coverage_verified=False`; diagnostic correctly reported `REVIEW_REQUIRED` with successful script process exit (not promotion PASS).

**Evidence boundary:** absent marker in short and long cases cannot by itself diagnose Ollama context truncation. Diagnostic did not log model answer text. Next: capture bounded raw answer text and recheck marker check / prompt following in a separate diagnostic copy; leave product unchanged. R-01 remains OPEN / ROOT CAUSE NOT DETERMINED.

## PRR2-R2 short model answer — 22 Nov 2026

- Operator R2 answer inspection (1200-character fixture): provider `qwen3:1.7b`, `prompt_eval_count=377`, `finish_reason=stop`, `MODEL_COMPLETE=True`, answer exactly `UNRESOLVED` instead of trailing marker `PRR2_END_3704A0C98C37369A`. This is **not proof** of prompt truncation; model abstained despite a marker present in synthetic source.
- Separate **diagnostic-only** PRR2-R3 control probe created (not a product code change), ZIP `PRR2_R3_CONTROL_PROBE.zip` SHA-256 `8e3166d93fc74fb417e68b5f189f52c36ee81e780dcb8c71aafa398d4e50f809`; not uploaded to GitHub. Uses explicit key-value field at tail, positive/absent negative controls, 1200 / 7900-char fixtures. Assistant-local static syntax and 4 fixture shape checks PASS; **real Windows/Ollama execution pending**.
- R-01 continues OPEN; avoid labeling complete model generation as validated context coverage. No code modifications to frozen CFC or Evidence Copilot source.

## PRR2-R3 finding and R4 diagnostic correction — 22 Nov 2026

Operator Windows R3 results with `qwen3:1.7b`: short-present 1200 chars returned the expected key (`prompt_eval_count=508`); long-present 7900 returned expected key (`prompt_eval_count=2459`); both `finish_reason=stop` and `model_context_coverage_verified=False`. **These are narrow field-retrieval observations, not full context-coverage proof.**

R3 negative test falsely flagged `FABRICATED_KEY`: the **question itself contained the target key**, and model replied `Brak kodu [KEY] w dokumentie`, denying presence. Pure substring classification was invalid. This is a **diagnostic-harness error**, not confirmed model hallucination.

R4 diagnostic-only candidate `PRR2_R4_CORRECTED_NEGATIVE_PROBE.zip` SHA-256 `4326d44cbf11364b7bc81c471613e92dae829c280e7b9593a3252b4a43801902` now removes target key from the negative question, refuses key-leaking questions, and separates outcomes; assistant local Python compile + 4 fixture cases PASS; **R4 real Windows run pending**. No Evidence Copilot or frozen CFC source changed. R-01 context coverage remains OPEN.

## PRR2-R4 corrected negative control — Windows / real Ollama, 22 Nov 2026

Operator-run `prr2_r4_control_probe.py` with unchanged PRR1 bridge and local `qwen3:1.7b`:

| Case | Source length | Prompt eval count | Observed answer | Diagnostic outcome |
|---|---:|---:|---|---|
| short_present | 1200 | 508 | returned `KOD_TESTOWY_PRR2_R3_68C2` | `EXPECTED_KEY_RETURNED` |
| short_absent | 1200 | 516 | `Pole identyfikacyjne w dokumencie: BRAK W DOKUMENCIE` | `NO_KEY_FABRICATION_OBSERVED` |
| long_present | 7900 | 2459 | returned `KOD_TESTOWY_PRR2_R3_68C2` | `EXPECTED_KEY_RETURNED` |

All cases reported `finish_reason=stop`, `MODEL_COMPLETE=True`, `CONTEXT_COVERAGE_VERIFIED=False`; negative question `NEGATIVE_QUESTION_KEY_LEAK: NO`. Script completed without an error. The prior R3 `FABRICATED_KEY` was an **invalid diagnostic classification** caused by leaking the sought key in the question; it is not a confirmed hallucination.

**Outcome:** PRR2 diagnostic negative-control defect **CORRECTED AND OPERATOR-TESTED**; narrow end-of-document retrieval observed. **R-01 full context coverage remains OPEN/NOT PROVEN.** Do not patch product bridge based on this observation or claim generalized model context fidelity. Frozen CFC/P74 unchanged.

## PRR3 — isolated HTTP boundaries repair candidate (22 Nov 2026)

- Audited exact PRR1 `portable_server.py`: bound to `127.0.0.1:8780`, strict POST `Origin`, content-type and body-size checks, route allowlist. **Confirmed gaps:** no `Host` header validation (GET/POST) and no socket inactivity timeout; ambiguous duplicate `Content-Length` / `Transfer-Encoding` POST framing not rejected explicitly.
- Minimal, unfrozen repair candidate: `EVIDENCE_COPILOT_PRR3_HTTP_REPAIR_CANDIDATE.zip`, SHA-256 `ac4d76255e90ca3adac70e076c833027ad93603cb28e03e1563028f5fdefb6cb`; **not uploaded to GitHub**. Only `portable_server.py` modified. Adds single exact loopback `Host` check (actual bound port, including test ephemeral listener), rejects ambiguous POST framing, and configures a 15-second socket inactivity timeout.
- Assistant-local tests: new isolated HTTP positive/negative suite **10/10 PASS**; inherited P77-A 7/7, P77-B mock 6/6, P79 quotes 9/9 + HTTP mocks 3/3, P80 synthetic boundary 4/4 (**29/29 PASS**); archive file hashes **27/27 PASS**. No real Windows/Chrome execution for PRR3 and no independent audit.
- **Open controls:** `ThreadingHTTPServer` concurrency is not bounded; Ollama upstream may take 120 seconds and socket timeout is not an end-to-end execution budget. Additional CORS/Origin/security review and stress tests remain pending. Localhost-only, do not expose on LAN.
- **Next gate:** Windows operator verify archive + run `test_prr3_http.py`, inherited tests and real GUI startup. PRR3 remains `REPAIR_CANDIDATE_NOT_PROMOTED`; CFC/Wrapper/P74 unchanged.
