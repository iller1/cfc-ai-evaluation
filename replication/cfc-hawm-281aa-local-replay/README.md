# CFC × HAWM — Bounded Local Replay and Stale-State HTTP Rejection

**Status:** Local, operator-reported technical evidence; **not independently reproduced**  
**Report date:** 2026-11-15  
**Scope:** One synthetic HAWM → frozen CFC Anchor scenario, with a sequential stale-state HTTP rejection test  
**Release status:** Public report, bounded operator-captured synthetic input/output, console text and protocol-review draft; **private executable materials not distributed**

## The question

Can a HAWM operator-confirmed mapping be replayed through the unchanged CFC Anchor, and will HAWM reject the mapping after its source state changes?

This report documents a bounded experiment, **not** general AI correctness, an independent security assessment, or production readiness. The observations below come from local PowerShell/HTTP outputs supplied by the operator; an external reviewer has **not** yet reproduced them.

## Pinned controller boundary

- Frozen CFC Anchor: `0.2.90rc1`; Operator Wrapper `v1.23` remains separately frozen.
- Wheel SHA-256: `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`
- Frozen engine SHA-256: `77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`
- Public API reference SHA-256: `d057ec835d11e8d8ed2086eb02e83ca52c210b8d627bad4ba5087aaa555ea333`

These hashes are *identity/integrity references*, not external custody attestations.

## Observed local results

| Step | Test | Operator-reported observation | Evidence boundary |
| --- | --- | --- | --- |
| 281K | Replay the same confirmed fixture against frozen Anchor | Input matched; complete raw output matched exactly | Same host, not independent |
| 281L | Synthetic paired A/B with only `independence_authority` changed from `NONE` to `VERIFIED` | A: `control_closure=false`, `stop_type=NONE`; B: `control_closure=true`, `stop_type=EPISTEMIC_STOP` | Parameter substitution; no real-world independence verification |
| 281O | Change confirmed HAWM state in memory | `STALE_MAPPING_DRAFT` rejection | In-memory test only |
| 281T | Confirm a mapping, modify HAWM state, then call `/api/handoff/run` over isolated local HTTP | HTTP `409`, `STALE_MAPPING_DRAFT`; no new CFC run ledger entry or `last_fixture_result` recorded | Sequential request test; no concurrent or cross-process proof |
| 281U | Inspect native HAWM POST handler | `do_POST` wraps `_do_POST_guarded()` in `threading.RLock()` | Code-level single-process serialization, not a concurrency stress test |
| 281AA | Build private reproducer from hash-checked frozen files and replay saved fixture | `FROZEN_CFC_INTEGRITY: PASS`; `INPUT_MATCH: True`; `RAW_OUTPUT_EXACT_MATCH: True`; `CONTROL_CLOSURE: False`; `STOP_TYPE: NONE`; `REPRODUCER: PASS` | Private same-host replay; not an external reproduction |

The bounded replay initially exercised a synthetic claim (`DemoSubject is safe.`) with two current positive records and **no attested source independence**. The initial controller result had `control_closure=false`; four mandatory gate checks were false. The `EPISTEMIC_STOP` code in the paired positive case denotes *controller closure readiness* under this frozen controller's semantics, **not permission to execute any downstream action**.

The current bridge's presentation label `ALLOW` for `control_closure=true` must not be interpreted as real-world authorization. That terminology remains a presentation-layer limitation; the frozen controller was not changed.

## Public inspectable artifacts — operator-supplied, not independently verified

The following are now published for **inspection of recorded data**. These improve transparency but **do not** independently verify execution or permit reproduction without the frozen runtime.

- [Bounded synthetic fixture (JSON)](operator_capture_fixture_281J.json)
- [Complete recorded raw frozen-CFC controller output (JSON)](operator_capture_raw_output_281J.json)
- [Operator-reported 281AA console transcript](operator_reported_console_281AA.txt)
- [Provenance, extraction checks and limitations](EVIDENCE_PROVENANCE.md)
- [Public review-protocol draft](PUBLIC_REVIEW_PROTOCOL.md) — a Markdown adaptation, **not byte-identical** to private 281AC TXT

The JSON artifacts were extracted from the **operator-provided** synthetic native trace and are not signed by an independent custodian. The input equals the recorded `custom_input`; the complete raw result is available for inspection. The original private trace is not attached. A complete HTTP request/response recording for 281T is **not yet published**, so HTTP 409 remains operator-reported.

## Private reproducibility artifacts (not attached)

- **281AA** — private standalone local reproducer, including a `reproduce.py` entry point.
- **281AB** — SHA-256 manifest listing **23** reproducer files. Manifest SHA-256: `D26F95EA13723FB4DEB47C7DC05D3836A1093B8F4E3F52A372B90814C9DAD5EF`.
- **281AC** — independent-review protocol draft. Document SHA-256: `9C80C7176A3B2B979F3BC89C8564BFF33A924467859A2B5801796BCBAC7BCAAF`.

**Important:** The manifest and protocol digests are reported from the operator's local environment. Their digests alone do not allow a reader to reproduce this test or prove independent custody. The executable package, manifest file, full native export, local HAWM state and private ledger **are not published here**.

The wheel's internal metadata states: `License: Proprietary research prototype - licensing not yet frozen`. Distribution/permission terms must be resolved **before sharing those executable materials**. The public report is not a substitute for a licensed reproducibility package.

## Proposed independent-review protocol (DRAFT — not yet executed)

1. Agree on authorized access to a sanitized, frozen reproducer and establish a trusted channel for the expected manifest digest.
2. Record reviewer identity/pseudonym, OS, Python version (Python >=3.10), date, and environment differences.
3. Verify the manifest SHA-256, and independently verify **every one of the 23 included file hashes** against the manifest.
4. From the reproducer directory run `python -B reproduce.py`.
5. Preserve complete stdout/stderr, process exit code and any deviations; provide a short independent review note.

**PASS:** Verified manifest and files, runtime checks passed, fixture input matched, full raw output matched exactly, exit code `0`, with no unexplained deviations.

**FAIL:** A correctly verified and valid setup yields a reproducible mismatch or fails a specified acceptance criterion.

**INCONCLUSIVE:** Materials, integrity, provenance, environment or execution cannot be established adequately to attribute the outcome. A hash mismatch is **never** PASS; an integrity failure alone does not prove a controller regression.

### Current exclusions

- No independent external reproduction or third-party certification yet.
- No arbitrary document-to-evidence mapping, general correctness claim or production safety certification.
- No real-world source-independence attestation.
- No CP-15 Information Passport connection.
- No M6 authorization, executor approval, or real-world actions: **HOLD**.
- No cross-process concurrency or exhaustive TOCTOU assurance.

## Call for reviewers

We welcome a narrowly scoped **protocol review first**, with possible independent reproduction **after distribution conditions are agreed**. A useful review challenges the acceptance criteria, trust boundary, identity claims, and the strength of the reported observations—not merely whether the local program printed PASS.

### Polski — krótkie podsumowanie

To publiczny opis **lokalnego testu syntetycznego** CFC × HAWM. Odtworzono identyczny wynik zamrożonego kontrolera i uzyskano odmowę HTTP 409 po zmianie zatwierdzonego stanu. Powstał prywatny reproduktor oraz manifest 23 plików. **Nie było jeszcze niezależnej reprodukcji; nie publikujemy prywatnych plików ani zamrożonego pakietu z nieustalonymi warunkami licencji.** Poszukujemy recenzenta, który najpierw zakwestionuje protokół i granice dowodu.
