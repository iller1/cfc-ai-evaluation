# CFC Demonstrator — working v0.1

Minimal local demonstrator over the frozen CFC Anchor execution track.

Pipeline:

`INPUT / EVIDENCE STATE -> MODEL CONCLUSION -> FROZEN CFC CHECK -> ALLOW / STOP + CLAIM STATE + REASON`

## Run

Windows: double-click `RUN_DEMO.bat` or run:

```text
python server.py
```

macOS/Linux:

```text
./run_demo.sh
```

Open `http://127.0.0.1:8765`.

The first start verifies the bundled frozen wheel SHA-256 and installs that exact wheel into the local `runtime/site` directory. No controller source is modified.

## Verify

```text
python verify_demo.py
```

The UI contains eight executable synthetic fixtures. `Run frozen controller` executes the selected fixture in a fresh Python process and compares the result with its preserved reference execution.

Operator Wrapper v1.23 remains byte-for-byte frozen and separate. The executable controller used by this demo is the frozen CFC Anchor `0.2.90rc1` public API.
