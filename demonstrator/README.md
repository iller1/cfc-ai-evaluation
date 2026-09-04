# CFC Demonstrator v1.0

Minimal local demonstrator over the frozen CFC Anchor execution track.

`INPUT / EVIDENCE STATE -> MODEL CONCLUSION -> FROZEN CFC CHECK -> ALLOW / STOP + CLAIM STATE + REASON`

## Status

This v1.0 package is the reconciled successor to the historical `cfc-demonstrator-v1.0-rc1` release candidate. The exact CASE_09 and CASE_10 bytes were recovered from the preserved RC1 release asset and verified against the preserved SHA-256 integrity anchors before inclusion in the reconciled source tree.

The frozen execution boundary is unchanged:

- CFC Anchor `0.2.90rc1` remains the deterministic executable controller;
- Operator Wrapper v1.23 remains byte-for-byte frozen, separate, and not bundled;
- the demonstrator remains an external presentation/replay layer and does not create, repair, reinterpret, or override controller decisions.

## Run

Requirements: Python 3.10 or newer. No third-party Python packages, pip install, or network access are required.

Windows: double-click `RUN_DEMO.bat` or run `python server.py`.

macOS/Linux: run `./run_demo.sh`.

Open `http://127.0.0.1:8765`.

The first start verifies the bundled frozen wheel SHA-256 and extracts that exact wheel into local `runtime/site` using Python standard-library `zipfile`.

## What is executable

- 10 preserved representative fixtures with live replay against the frozen controller;
- Reviewer mode: a live A/B experiment that changes only explicit independence-authority state;
- Build custom case: a bounded evidence-state builder mapped to the frozen public API.

The custom builder deliberately does not parse arbitrary natural language. Its fixed fictional claim is `DemoSubject / state / safe`; the user may change evidence polarity, temporal validity, required support count, provenance shape, explicit independence-authority state, and audit scope.

Distinct-looking provenance is not treated as proof of independence. The `VERIFIED` independence option installs an explicit synthetic host-authority attestation through the frozen public API.

## Verify

Run the complete release self-check:

```text
python verify_release.py
```

Individual checks remain available as `verify_demo.py`, `verify_custom.py`, and `verify_reviewer.py`.

## Reviewer mode

- A: two current positive supports, independence authority `NONE` -> frozen controller returns `SUPPORTED`, closure false;
- B: identical state except independence authority `VERIFIED` -> frozen controller returns `VERIFIED`, closure true;
- `verify_reviewer.py` confirms that only the declared input field changes and that both runs use the expected frozen engine identity.

## Claim boundary

See `CLAIM_BOUNDARY.md`. This demonstrator is a research-prototype demonstration artifact. It does not by itself establish general model-safety improvement, production readiness, external validation, universal correctness, ROI, or causal efficacy.
