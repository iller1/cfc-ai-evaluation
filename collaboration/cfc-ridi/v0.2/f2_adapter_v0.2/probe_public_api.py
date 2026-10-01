from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("f2_candidate_v02", HERE / "adapter.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules["f2_candidate_v02"] = mod
SPEC.loader.exec_module(mod)

repo_root = HERE.parents[3]
wheel = repo_root / "demonstrator/cfc_anchor-0.2.90rc1-py3-none-any.whl"
out = mod.public_interface_probe(wheel)

assert out["private_engine_accessed"] is False
assert out["anchor_wheel_artifact_verified"]["sha256"] == mod.ANCHOR_WHEEL_SHA256
assert out["f1_interface_sha256"] == mod.F1_INTERFACE_SHA256
print("PUBLIC_INTERFACE_PROBE_PASS")
