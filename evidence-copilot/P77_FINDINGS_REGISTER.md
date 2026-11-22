# P77 — External review findings register and repair gates

**Baseline checkpoint:** P74 remains immutable: ZIP SHA-256 `05afb0e930b7a2fa3f96125873c94426ba42968c2e4d37d1e2fd18308116eb99`. PR #115 is the external-review checkpoint. **Do not overwrite the P74 ZIP or historical receipts.**

**Evidence classification:** Review A reported static source/manifest inspection; Reviews B and C explicitly could not access source; Review D reported independently downloading P74, exercising Python code and mocked-Ollama HTTP flows on Python 3.12.3, but not real Ollama/GUI/Windows. Runtime results in P70–P76 remain operator-reported. The claims below require independent reproduction when stated.

## Prioritized findings

| ID | Finding | Source of finding | State at P77 start | Planned gate |
|---|---|---|---|---|
| DOCX-01 | Byte-substring tracked-change check rejects legitimate `w:insideH` / `w:instrText`, misses alternative namespace prefixes | Review D, reported executed | Reproduced in isolated copy against P74 | Fix + regression tests |
| DOCX-02 | UTF-16 XML DTD/entity declarations evade ASCII-byte guard | Review D, reported executed | Reproduced against P74 | Encoding-agnostic DTD rejection tests |
| DOCX-03 | Hidden OOXML text passes as visible source | Review D, reported executed | Reproduced against P74 | Explicit refusal and tests |
| CTX-01 | Bridge has no explicit `num_ctx` and hardcodes `full_extracted_text_sent=True` | Review D, static and stub | Static code verified | Explicit context evidence / fail-closed |
| LIMIT-01 | Importer accepts 100k characters; bridge accepts 8k | Review D | Static code verified | Align user-visible workflow/limits |
| GROUND-01 | Fabricated quotation can return `complete=True`; no exact-quote verifier | Review D, stub | No local independent replay yet | Separate completion and quote support; add tests |
| GUI-01 | Residual unavailable HAWM/CFC controls in GUI | Reviews A/D | Static evidence | Disable/hide in demonstrator |
| GUI-02 | JS UTF-16 length differs from Python Unicode code-point count | Review D, static/Node | Static evidence | Unicode regression |
| HTTP-01 | Host header unchecked, local unauthenticated server, threads/timeouts | Review D | Static/stub evidence | Host check, timeout, bounded concurrency |
| PROV-01 | No pinned Ollama model digest/seed/version | Reviews A/D | Static evidence | Model provenance disclosure |
| REPRO-01 | ZIP has no shipped functional tests/fixtures | Reviews A/D | Verified from P74 archive | Bundle reproducible tests |
| PDF-01 | PDF parser untrusted-input fuzz/timeout absent | Reviews A/D | NOT TESTED | Separate evaluation |
| INJECT-01 | LLM document delimiter spoofing possible | Review D stub | Semantic effect NOT TESTED | Structured boundary + adversarial suite |

## Gate plan

- **P77-A — isolated DOCX parser repair**: change only `document_intake.py` in a *new candidate*, ship seven synthetic tests (including four adversarial DOCX cases), report baseline failures vs candidate successes; no model calls.
- **P77-B — model context and model-response evidence**: do not claim full-text coverage until actual evidence. Preserve previous schema/GUI consistency; test a stub before deployment.
- **P77-C — GUI semantic/Unicode/disabled-route alignment and functional HTTP harness.**
- **P77-D — external clean-room reproduction of fixed candidate, with independent logs and fixed model identity.**

**Status:** P77-A local isolated test reported by assistant-side execution. Full P77 candidate NOT PROMOTED. P74 original remains review evidence. No claim of pilot readiness.

**Unchanged project controls:** CFC FROZEN; M6 HOLD; E2E 0/6; CP-15 NOT CONNECTED.

## P77-B isolated candidate — 21 Nov 2026

- Candidate archive: `EVIDENCE_COPILOT_P77B_CONTEXT_CANDIDATE.zip`; SHA-256 `730eb51df75119bddaa32407e6967b74c1dfded16a6dee331f3bfe0aaa7d078a` (created locally, **not yet uploaded to GitHub**).
- Changes: explicit Ollama `num_ctx=8192`, `num_predict=512`; require `prompt_eval_count` and refuse near the configured budget; mark `model_context_coverage_verified=False` and document that the request sent all extracted text **without claiming** the model necessarily processed all of it; revise GUI wording accordingly.
- Results from isolated assistant-side runs: P77-A importer 7/7 PASS; P77-B mocked bridge 6/6 PASS; Node syntax PASS. No actual Ollama, no Chrome runtime, no independent-machine reproduction.
- `full_extracted_text_sent=True` in compatibility schema means the full extracted text was **submitted in the HTTP request**, not verified model context coverage or source grounding. This is a known provenance limitation.
- HOLD: model context fidelity needs real Ollama and adversarial long-document tests; grounding, the GUI Unicode bug, and missing endpoints remain open. No promotion or merging until explicit test evidence.

## P79 — literal-quote check candidate (21 Nov 2026)

- New isolated candidate ZIP: `EVIDENCE_COPILOT_P79_QUOTE_CHECK_CANDIDATE.zip`, SHA-256 `2dabb855a23efa3b2b0b37da2b6656eaad0f8e63c4537c3647ff4587a157a7a1`. The archive was constructed in the assistant environment but **has not been uploaded to GitHub**.
- Added a source-hash-bound literal quote check (`QUOTE_EXACT_MATCH`, `QUOTE_NOT_FOUND`, `QUOTE_CHECK_INCONCLUSIVE`) and displayed its result alongside `ANSWER UNVERIFIED`. It does not establish factual correctness, entailment or source authenticity.
- Assistant-local tests: P77-A 7/7, P77-B mocked bridge 6/6, P79 quote-unit 9/9, P79 HTTP mocked-model 3/3, JS syntax PASS; packaged 17 entries, offline hashes 16/16. **P79 real Qwen and Chrome NOT TESTED**; external replication NOT DONE.
- P78 real Qwen previous version P77-B reported working locally by operator; that result does not validate new P79 functionality.
- Next gate: user runs P79 tests on Windows and real Ollama against synthetic P31; preserve P74 as immutable checkpoint.

## Operator follow-up evidence — 22 Nov 2026 (P79–P81-R2-A)

This addendum supersedes **earlier pending-status statements for these specific gates only**. It does not revise historical logs.

| Gate | Operator-reported evidence | Narrow outcome |
|---|---|---|
| P79 Windows automated tests | P77-A importer 7/7, P77-B mocked context 6/6, P79 quote unit 9/9, HTTP mocked integration 3/3; offline hashes 16/16 | Local automated checks PASS 25/25; structural/byte checks only |
| P79 real Qwen3:1.7b + Chrome | Initially served stale `workspace.js` (local hash `6f3e6f525518f4a33813d7ac2ff350e9931b29dc7e7aa920ceef8d8adf95b0a9`; server hash `2520c2b830a058d2bb587dde17016cde3300e41d2a7c874b97ca1e735a759277`). After restart `P79_GUI_BYTE_MATCH: True`; real run reported `P79_QUOTE_STATE: QUOTE_EXACT_MATCH` and Chrome `QUOTE CHECK: QUOTE_EXACT_MATCH (1/1 exact) | SEMANTIC SUPPORT: NOT VERIFIED` | **LOCAL RUNTIME PASS for this one quote case**, not independent replication, not semantic entailment |
| P80 Windows synthetic boundary | Offline hashes 11/11; P80 unit tests 4/4, including correct quote paired with unsupported/irrelevant claim; packaged predecessor unchanged relative to manifest | **LOCAL SYNTHETIC PASS**; semantic correctness NOT PROVEN; no independent review |
| P81-R1 Windows matrix | 12 synthetic cases spanning SUPPORTED, CONTRADICTED, IRRELEVANT, FABRICATED_QUOTE, CONFLICT, UNRESOLVED; 7/7 matrix structural tests | **LOCAL STRUCTURE PASS**; labels are author-generated, not reviewed oracle |
| P81-R2-A Windows blind-review packaging | Offline hashes 6/6; blind coverage/form/label-hide/provenance tests 4/4 | **LOCAL PACKAGE PASS**; independent reviewer has not yet assessed cases |

**Current hard boundary:** `P81-R2-B EXTERNAL BLIND REVIEW PENDING`, `REFERENCE_FREEZE HOLD`. P81-07 and P81-09 especially need separate consideration of citation validity, claim support, and conflicting-rule evidence. No Qwen benchmark should be scored against P81 labels until reference review/adjudication is complete.

**Candidate distribution:** P80, P81 and P81-R2 packages were tested in isolated user Windows folders, but this GitHub change records **status only**. It does **not** claim these ZIP contents or raw receipts are included in the repo. Check hash/manifests on any separately submitted artifacts. P74 ZIP and historical evidence must remain immutable.

**Other unresolved controls:** long-document model context coverage, native CFC/HAWM integration, end-to-end execution prevention, model provenance, external clean-room replication. `CFC FROZEN | M6 HOLD | E2E 0/6 | CP-15 NOT CONNECTED`.
