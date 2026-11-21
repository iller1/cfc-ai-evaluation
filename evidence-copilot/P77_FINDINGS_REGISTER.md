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
