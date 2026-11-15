# Evidence provenance and limits — operator capture

This directory contains **operator-supplied evidence from a single synthetic HAWM → CFC scenario**. Public files are available for inspection of *recorded data*, not independent re-execution.

## Source and derived artifacts

- Source: operator-provided `CFC_HAWM_NATIVE_REVIEW_TRACE_NOT_CP15 (1).json` (53,777 bytes).
- Source file SHA-256 as locally checked against the operator's earlier reference: `3d3af04e098ea1fd8ec468405f88cc3fbd4070dec959dff5741d1793c6441931`.
- `operator_capture_fixture_281J.json` is extracted from `original_hawm_export.state.mapping_draft.last_run_fixture`.
- `operator_capture_raw_output_281J.json` is extracted from `raw_original_cfc_result`.
- The source's frozen controller output also appears in `original_hawm_export.state.last_fixture_result.raw`; these two raw objects matched in the source.
- The extracted fixture matches the raw result's `custom_input` as a parsed JSON object.
- `operator_reported_console_281AA.txt` reproduces text pasted by the operator after running the private standalone local reproducer. It is **not** an independently captured terminal session.

The two JSON files preserve the full raw controller result and bounded fixture as *JSON values*; they are not byte-for-byte copies of sections of the original trace. The complete trace is not distributed (it includes local HAWM state and event ledger). Their publication does not independently authenticate the operator's source trace, the controller wheel, the execution environment, or the event chain.

## What can a reader inspect?

Readers can examine:
1. Synthetic fixture with `independence_authority=NONE` and two `CURRENT` positive evidence rows.
2. The full recorded raw result, including `control_closure=false`, `stop_type=NONE`, gate values and support-policy violations.
3. The operator-reported local 281AA check showing `RAW_OUTPUT_EXACT_MATCH: True`.

Readers **cannot** independently derive a new controller output from the supplied JSON alone, and cannot verify the HTTP 409 test from an HTTP transcript in this publication. The 281T claim remains operator-reported pending a safely reviewed full HTTP request/response trace.

## Explicit limits

- Not an external reproduction; no independent attestation or custody proof.
- Synthetic input; no live LLM inference.
- No verified source independence or real-world authorization.
- No permission to take downstream actions; M6 HOLD.
- Frozen executable controller not distributed because sharing terms are unresolved.
- CP-15 NOT_CONNECTED; production assurance NOT_CLAIMED.

For reviewer criteria, see [public draft review protocol](PUBLIC_REVIEW_PROTOCOL.md).
