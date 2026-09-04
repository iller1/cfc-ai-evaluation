# CFC Demonstrator — release candidate v1.0-rc1
- [CFC Demonstrator v1.0-rc1](https://github.com/iller1/cfc-ai-evaluation/releases/tag/cfc-demonstrator-v1.0-rc1)

Minimal local demonstrator over the frozen CFC Anchor execution track.

`INPUT / EVIDENCE STATE -> MODEL CONCLUSION -> FROZEN CFC CHECK -> ALLOW / STOP + CLAIM STATE + REASON`

## Run

Requirements: Python 3.10 or newer. No third-party Python packages, pip install, or network access are required.

Windows: double-click `RUN_DEMO.bat` or run `python server.py`.

macOS/Linux: run `./run_demo.sh`.

Open `http://127.0.0.1:8765`.

The first start verifies the bundled frozen wheel SHA-256 and extracts that exact wheel into local `runtime/site` using Python standard-library `zipfile`. No network access, pip installation, frozen controller source modification, or wheel-byte modification is required.

## What is executable

- 10 preserved representative fixtures with live replay against the frozen controller.
- `Reviewer mode`: a live A/B experiment that executes two otherwise identical states and changes only explicit independence-authority state.
- `Build custom case`: a bounded evidence-state builder that maps selected fields to the frozen public API and executes the result live.

The custom builder deliberately does **not** parse arbitrary natural language. Its fixed fictional claim is `DemoSubject / state / safe`; the user may change evidence polarity, temporal validity, required support count, provenance shape, explicit independence-authority state, and audit scope.

Important: distinct-looking provenance is not treated as proof of independence. A separate `VERIFIED` independence option installs an explicit synthetic host-authority attestation through the frozen public API.

## Verify

Run the complete release self-check:

```text
python verify_release.py
```

Individual checks remain available as `verify_demo.py`, `verify_custom.py`, and `verify_reviewer.py`.

Operator Wrapper v1.23 remains byte-for-byte frozen and separate. The executable controller used by this demo is the frozen CFC Anchor `0.2.90rc1` public API.

## Reviewer mode

- live one-variable Reviewer A/B experiment;
- A: two current positive supports, independence authority `NONE` -> frozen controller returns `SUPPORTED`, closure false;
- B: identical state except independence authority `VERIFIED` -> frozen controller returns `VERIFIED`, closure true;
- raw A/B outputs and direct loading of either state into Custom Case;
- `verify_reviewer.py` confirms that only the declared input field changes and that both runs use the expected frozen engine identity.
