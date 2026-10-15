# CFC · Isolated Consistency Gate — reproducible review (v0.1)

**Independent review welcome.** This is an internal, synthetic, non-authorizing experiment on the frozen CFC Anchor 0.2.90rc1 engine, not a NOAA ingestion or production demonstration.

## Get the exact artifacts

- **[Download original reproduction ZIP](./CFC_NATIVE_ISOLATED_CONSISTENCY_GATE_DEV_v0_1.zip)** — contains `reproduce_isolated.py`, `test_isolated.py`, `REFERENCE_RESULT.json`, English/Polish instructions, checksums and package receipt.
- **[Get frozen Anchor wheel](../../demonstrator/cfc_anchor-0.2.90rc1-py3-none-any.whl)** — this pre-existing binary is not modified by the experiment.
- [Interactive explanation](../../docs/cfc-demo/index.html) · [main project](../../README.md)

ZIP SHA-256: `a55d0d7fe67fbeb954142f3e8cf182e5059c361fe3fb9ad4470d64a00e9ffa36`

ZIP Git blob SHA-1: `e14d1515faac6f542e066b1048b3470840c93e16`

Frozen wheel SHA-256: `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`

Original `cfc_anchor/_engine.py` SHA-256: `77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`.

## Run on Windows PowerShell

Download the ZIP and wheel to your `Downloads` folder. If the wheel filename has an extra `(1)` suffix, rename the path variable accordingly (not the bytes). Then:

```powershell
$folder = "$env:USERPROFILE\Downloads\CFC_NATIVE_ISOLATED_CONSISTENCY_GATE_DEV_v0_1"
$wheel = "$env:USERPROFILE\Downloads\cfc_anchor-0.2.90rc1-py3-none-any.whl"

Get-FileHash -Algorithm SHA256 "$folder.zip"
Get-FileHash -Algorithm SHA256 "$wheel"
Expand-Archive -LiteralPath "$folder.zip" -DestinationPath $folder -Force
Set-Location $folder
py -3 .\reproduce_isolated.py --wheel "$wheel" --output .\WINDOWS_RESULT.json
$env:CFC_FROZEN_WHEEL = $wheel
py -3 -m unittest -v test_isolated.py
```

Expected status: `PASS_NATIVE_ONLY_GLOBAL_CONSISTENCY_GATE_FLIPS_SYNTHETIC_ONLY`, followed by `Ran 16 tests` and `OK`.

## What was observed

| Synthetic input | Claim | Global consistency | Other failed gates | Internal closure |
|---|---|---|---|---|
| safe / safe / safe | VERIFIED | true | none | true |
| safe / safe / unsafe | VERIFIED | false | none | false |

Only one **authored** record value changes: E3.value. Derived content-bound test identifiers are regenerated automatically. The native engine reports conflicts E1–E3 and E2–E3, with only `global_consistency_valid` failing.

The operator independently repeated the local execution on Windows on 2026-10-15: 16/16 PASS. This is **not** independent external attestation. Test role issuers and certificates are developer fixtures, not real trusted credentials. Positive internal `control_closure` is not permission to act in the real world.

## What a reviewer should challenge

Focus on support-set selection and the semantics of independence, the `r23_case` internal test helper, content-bound derived role records, completeness of the support universe, and whether generalization beyond synthetic fixtures is justified. The runner checks exact wheel and engine hashes and stops on mismatch.

**Unchanged boundaries:** Anchor FROZEN · F01 HOLD · G10/G13/G14 BLOCK · R273 NO_GO. NOAA-to-`Controller.evaluate` bridge NOT_ESTABLISHED.
