# Independent review protocol — public draft

**Status:** DRAFT / protocol review invited / independent execution not started  
**Basis:** Public adaptation of local 281AC protocol. **This Markdown file is not a byte-for-byte copy of the private 281AC TXT and must not be assigned its SHA-256.**  
**Scope:** A single synthetic frozen CFC Anchor `0.2.90rc1` replay, optionally followed by a separate review of the HAWM sequential stale-mapping HTTP case.

## Phase 1 — protocol review (possible now)

The reviewer can inspect the public [fixture](operator_capture_fixture_281J.json), [full recorded raw result](operator_capture_raw_output_281J.json) and [operator console transcript](operator_reported_console_281AA.txt) before any executable is shared.

Review questions:
- Does the fixture represent the stated bounded independence scenario?
- Do the recorded gates support `control_closure=false`?
- Are `stop_type=NONE` and `EPISTEMIC_STOP` distinguished from downstream authority?
- Are the proposed PASS / FAIL / INCONCLUSIVE criteria meaningful and sufficiently narrow?
- Which additional original records are necessary to evaluate the HTTP 409 stale-mapping claim?
- Which trust or custody claims cannot be established from operator-controlled data?

A reviewer can report **protocol feedback** at this stage, but **not an independent execution PASS**.

## Phase 2 — independent local replay (ON HOLD pending access and licensing)

### Materials needed

- Authorized, sanitized copy of the private 281AA reproducer, including frozen wheel/runtime files only if redistribution is permitted.
- 281AB file manifest with **23** entries.
- Expected manifest SHA-256 received through an appropriate trusted channel:
  `D26F95EA13723FB4DEB47C7DC05D3836A1093B8F4E3F52A372B90814C9DAD5EF`.
- 281AC private protocol TXT (optional for comparison), whose operator-reported SHA-256 is:
  `9C80C7176A3B2B979F3BC89C8564BFF33A924467859A2B5801796BCBAC7BCAAF`.
- Isolated local test environment and Python >=3.10.
- No live external effects and no downstream authorization.

### Proposed procedure

1. Record reviewer identity or pseudonym, local date/time, OS and Python version.
2. Verify the expected manifest digest using a trusted value, then verify all 23 file hashes; record missing/extra files.
3. In the reproducer folder run `python -B reproduce.py`.
4. Preserve exact command, stdout, stderr and process exit code.
5. Compare full parsed raw JSON output and fixture input to the supplied reference; document all differences.
6. Disclose environment differences, anomalies, and incomplete checks.

### Decision rules

**PASS:** Authorized and complete test setup; manifest and file integrity verified; frozen runtime verified; input exact match; full raw output exact match; process exit code 0; no unexplained deviations.

**FAIL:** With an otherwise verified and valid test setup, a reproducible mismatch or violation of a defined criterion occurs.

**INCONCLUSIVE:** Missing materials; integrity/provenance not established; execution environment unsuitable; or failure that cannot yet be attributed to the controller.

A hash mismatch is never PASS. A reported integrity problem alone is not proof of a controller regression.

### Reviewer return

Date, reviewer identifier, OS/Python version, manifest/hash results, full command and output, exit code, PASS/FAIL/INCONCLUSIVE with short reasoning, scope limits, and any recommended adversarial follow-up.

## Public information vs private material

Public: [report](README.md), [fixture](operator_capture_fixture_281J.json), [full recorded raw output](operator_capture_raw_output_281J.json), [281AA operator console text](operator_reported_console_281AA.txt), [evidence provenance](EVIDENCE_PROVENANCE.md), this protocol.

Private / not publicly supplied: executable controller wheel, complete HAWM export/ledger, complete 281T HTTP request/response transcript, 281AB 23-entry manifest file, and private 281AC TXT. Internal wheel metadata states `Proprietary research prototype - licensing not yet frozen`; no distribution permission is inferred.

**Not tested or established:** cross-process concurrency, full TOCTOU resistance, independent custody of sources, real-world source attestation, CP-15 integration, M6 authorization, downstream executor safety, or production readiness.
