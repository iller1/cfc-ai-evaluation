# CFC in 30 seconds

Additive browser-only presentation of the existing reviewer A/B experiment.
The frozen v1.0 demonstrator and its historical manifest are not changed.

Open this directory through any static HTTP host, or use the original local
server and visit `http://127.0.0.1:8765/quick/`. Use `?lang=pl` for Polish.

The initial view displays recorded A (STOP); one button shows recorded B
(ALLOW), and another click restores A. The page exposes the complete inputs
and raw results and clearly labels the interaction as recorded execution.
It does not run a controller or a language model in the browser.

Regenerate `recorded-ab.json` by running `python demonstrator/export_quick_demo.py`
from the repository root. This uses the existing `server.run_custom` boundary,
which checks the frozen wheel and executed engine identities. The exporter
checks that only `independence_authority` changes and verifies both outcomes.
The timestamp and source commit identify export provenance, not a new benchmark.

The full local demo retains all ten cases, live replay and the custom builder.
Its executable is CFC Anchor 0.2.90rc1, not Operator Wrapper v1.23.
