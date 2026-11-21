# Evidence Copilot — External Review Candidate (P74)

> **Status: DRAFT / CANDIDATE_NOT_PROMOTED.** The executable P74 ZIP is **not yet uploaded to this branch**. Do not treat this page as a runnable release or independent validation.

Evidence Copilot is a **local document-analysis demonstrator** associated with the CFC × HAWM research programme. It uses a local Ollama model to produce document-specific answers while explicitly marking them **unverified** and requiring **human review**. It is **not** the frozen CFC Anchor, does **not** execute the CFC controller or native HAWM, and does **not** authorize downstream actions.

## Intended audience

- **Independent technical reviewers:** examine the bounded trust/route design, reproduce the test, and report counterexamples or unsupported claims.
- **Research collaborators:** evaluate the difference between model completion, semantic correctness, source binding, and authority.
- **Potential pilot partners:** nominate **one concrete, low-risk document workflow** and define acceptance/rejection criteria before development. No production use or real sensitive documents at this stage.

## Operator-reported local evidence (21 November 2026)

| Step | Operator-reported observation | Boundary |
| --- | --- | --- |
| P70 | 9/9 regression cases equivalent between original and isolated importer | TXT, MD, CSV, DOCX, paste, four negative requests; PDF not tested |
| P72 | Local server on 127.0.0.1:8780 imported a synthetic document; Ollama `qwen3:1.7b` returned `finish_reason=stop`, `complete=True` | Semantic answer failed the ambiguity-handling expectation |
| P73 | Six HTTP route checks passed; HAWM, CFC and general-chat POST routes returned HTTP 403 | Limited route tests, **not** a full security audit |
| P74 | Nine-file ZIP built; ZIP content matched staged files | Locally generated, authenticity/independent custody unproven |
| P75 | Fresh extraction; 8/8 content hashes matched manifest | Same computer, offline integrity only |
| P76 | Freshly extracted copy served the UI, imported the synthetic document and returned another model response | Same computer, independent replication not done |

**Do not equate these operator-reported tests with an external audit.** `MODEL COMPLETE: YES` means response generation ended, **not** that the answer is sound. In the synthetic policy example, the model's answers differed in how they classified the A/B rule relationship. This is a test finding, not an automatic consistency-checking capability.

## P74 artifact identity (operator-reported)

- ZIP filename: `EVIDENCE_COPILOT_P74_REPLICATION_PACKAGE.zip`
- ZIP SHA-256: `05afb0e930b7a2fa3f96125873c94426ba42968c2e4d37d1e2fd18308116eb99`
- Manifest SHA-256: `7fda8b1739a6dc3fcb24ac132e97b3d39269a7d21b96357e452de51d663cbf7e`
- Contents: `portable_server.py`, `document_intake.py`, `document_ai_bridge.py`, `workspace.html`, `workspace.js`, `workspace.css`, `verify_package.py`, `README_REPLICATION.txt`, `P74_MANIFEST.json`

**Artifact publication pending.** The SHA-256 values above are useful for comparison once the actual archive is provided; they do not independently authenticate its origin.

## Reproduction protocol (once the ZIP is available)

1. Verify the downloaded ZIP against the recorded SHA-256, then extract it to a new folder.
2. Inspect the source code before running it. Requirements: Python 3, Ollama with local `qwen3:1.7b` (the weights are not included), web browser; `pypdf` is optional for PDF support.
3. Run `python -B verify_package.py` from the extracted folder.
4. Start Ollama and launch `python -B portable_server.py`; browse to `http://127.0.0.1:8780/`.
5. Import a **synthetic** document and ask about potential ambiguity in contradictory or exception-based rules.
6. Record import hash, model response, `MODEL COMPLETE`, `ANSWER UNVERIFIED`, `HUMAN REVIEW REQUIRED`, and `CFC NOT RUN`. Verify forbidden routes separately.
7. Report **PASS / FAIL / INCONCLUSIVE**, Python and Ollama versions, error output and reproduction steps. Do **not** silently edit the frozen baseline.

## Explicit boundaries

- CFC Anchor: **frozen / not executed** by this demonstrator.
- M6: **HOLD**; full E2E: **0/6**; CP-15: **NOT CONNECTED**.
- No independent replication, production authorization, professional security assessment, source authenticity proof, or verified semantic reliability.
- The server listens only on localhost; do **not** expose it to the public internet.
- Do not input confidential, personal, privileged or regulated documents into a demonstration without a separate security and data-handling review.

## Request for reviewers and prospective pilots

Please specify **which exact workflow** you would test, what a correct result looks like, what a false positive or false negative would cost, what evidence is required, and what should cause a STOP/INCONCLUSIVE decision.

A useful review identifies **one reproducible defect or one clearly bounded pilot use case**. It does not need to endorse the entire CFC × HAWM research programme.

---

**Review provenance:** prepared from operator-reported P70–P76 terminal/browser results. The actual P74 source/ZIP must be uploaded and checked before calling this a replication-ready public package.
