from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any, Callable

from fixtures import (
    ADAPTER_PATH,
    HERE,
    REPO_ROOT,
    WHEEL_PATH,
    adapter,
    build_resolved_state,
    execute,
    make_neutral_arm,
)

EXPECTED_F2 = {
    "adapter.py": {
        "path": REPO_ROOT / "collaboration/cfc-ridi/v0.2/f2_adapter/adapter.py",
        "bytes": 28972,
        "sha256": "4b975fda6242c9a7e33d0d692705ef6fe82683dbf2bddefc0345c2e5504b480a",
    },
    "test_adapter.py": {
        "path": REPO_ROOT / "collaboration/cfc-ridi/v0.2/f2_adapter/test_adapter.py",
        "bytes": 6586,
        "sha256": "4f70526185dbb69e4073c0baf89a6f924e8e1e220ba0317c339708bf5b152f34",
    },
    "README.md": {
        "path": REPO_ROOT / "collaboration/cfc-ridi/v0.2/f2_adapter/README.md",
        "bytes": 3479,
        "sha256": "3bf666564b2c1a7f85526a3e223e7385e30a61c73e8d5f67ca0b17d954d7638a",
    },
    "ADAPTER_MANIFEST.json": {
        "path": REPO_ROOT / "collaboration/cfc-ridi/v0.2/f2_adapter/ADAPTER_MANIFEST.json",
        "bytes": 1348,
        "sha256": "32b8c36ebb434fa620cdae970ed12bbb389a1ae62d20be6005e78b7c0db89591",
    },
}

CRITERIA_SHA256 = "f9640dbaec55a2b381a159825fe27a9e87502b75b20bbfbcf4382ca44cd887a2"
F2_COMMIT = "4167783eb48e1a1677107cb1359ad9b2f890017f"
PASS_STATUS = "F3_REPRESENTATION_ONLY_ADVERSARIAL_SUITE_PASS"
FAIL_STATUS = "F3_NO_GO_REPRESENTATION_INVALID"


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def result_pass(detail: Any) -> dict[str, Any]:
    return {"status": "PASS", "detail": detail}


def result_fail(detail: Any) -> dict[str, Any]:
    return {"status": "FAIL", "detail": detail}


def explicit_rejection(fn: Callable[[], Any]) -> tuple[bool, str]:
    try:
        fn()
    except Exception as exc:
        return True, f"{type(exc).__name__}: {exc}"
    return False, "mutation was accepted"


def nonclosure_or_rejection(fn: Callable[[], Any]) -> tuple[bool, dict[str, Any]]:
    try:
        out = fn()
    except Exception as exc:
        return True, {
            "mode": "EXPLICIT_REJECTION",
            "exception": f"{type(exc).__name__}: {exc}",
        }
    closed = out.get("control_closure")
    if closed is False:
        return True, {
            "mode": "EXPLICIT_NON_CLOSURE",
            "control_closure": closed,
            "stop_type": out.get("stop_type"),
            "claim_states": out.get("claim_states"),
            "raw_keys": sorted(out.get("raw", {}).keys()) if isinstance(out.get("raw"), dict) else None,
        }
    return False, {
        "mode": "SILENT_OR_NORMAL_CLOSURE",
        "control_closure": closed,
        "stop_type": out.get("stop_type"),
        "claim_states": out.get("claim_states"),
    }


def require_positive_control(label: str, payload: dict[str, Any], resolved: dict[str, Any]) -> dict[str, Any]:
    out = execute(payload, resolved)
    if out.get("control_closure") is not True:
        raise RuntimeError(
            f"{label}: positive control did not close; "
            f"control_closure={out.get('control_closure')!r}, "
            f"stop_type={out.get('stop_type')!r}, "
            f"claim_states={out.get('claim_states')!r}"
        )
    return {
        "control_closure": True,
        "stop_type": out.get("stop_type"),
        "claim_states": out.get("claim_states"),
    }


def t01() -> dict[str, Any]:
    observed = {}
    for name, spec in EXPECTED_F2.items():
        p = spec["path"]
        observed[name] = {
            "bytes": p.stat().st_size,
            "sha256": sha_file(p),
        }
        if observed[name]["bytes"] != spec["bytes"] or observed[name]["sha256"] != spec["sha256"]:
            return result_fail({"component": name, "expected": spec, "observed": observed[name]})
    if sha_file(WHEEL_PATH) != adapter.ANCHOR_WHEEL_SHA256:
        return result_fail({
            "component": "anchor_wheel",
            "expected_sha256": adapter.ANCHOR_WHEEL_SHA256,
            "observed_sha256": sha_file(WHEEL_PATH),
        })
    return result_pass({
        "f2_commit": F2_COMMIT,
        "components": observed,
        "anchor_wheel_sha256": sha_file(WHEEL_PATH),
    })


def t02() -> dict[str, Any]:
    payload = make_neutral_arm()
    outputs = [adapter.prepare_artifacts(copy.deepcopy(payload)) for _ in range(5)]
    hashes = [adapter.canonical_json_sha256(x) for x in outputs]
    if len(set(hashes)) != 1 or any(x != outputs[0] for x in outputs[1:]):
        return result_fail({"artifact_hashes": hashes})
    return result_pass({"runs": 5, "artifact_sha256": hashes[0]})


def t03() -> dict[str, Any]:
    base = make_neutral_arm()
    variant = copy.deepcopy(base)
    variant["draw"] = 77
    variant["source_binding"]["source_registration"] = "changed-bookkeeping-registration"
    variant["source_binding"]["prompt_sha256"] = hashlib.sha256(b"changed-prompt-binding").hexdigest()
    variant["recorded_endpoint"]["model"] = "ChangedFixtureModel"
    variant["recorded_endpoint"]["revision"] = "changed-revision"
    variant["recorded_endpoint"]["source_generations_sha256"] = hashlib.sha256(b"changed-generation-binding").hexdigest()

    a = adapter.prepare_artifacts(base)
    b = adapter.prepare_artifacts(variant)

    sem_a = a["mapping_manifest"]["semantic_state"]
    sem_b = b["mapping_manifest"]["semantic_state"]
    authority_a = a["mapping_manifest"]["authority_state"]
    authority_b = b["mapping_manifest"]["authority_state"]
    req_a = a["authority_requirements"]["required_external_state"]
    req_b = b["authority_requirements"]["required_external_state"]

    if sem_a != sem_b or authority_a != authority_b or req_a != req_b:
        return result_fail({
            "base_semantic_state": sem_a,
            "variant_semantic_state": sem_b,
            "base_authority_state": authority_a,
            "variant_authority_state": authority_b,
            "base_required_external_state": req_a,
            "variant_required_external_state": req_b,
        })
    return result_pass({
        "semantic_state_unchanged": True,
        "authority_state": authority_a,
        "required_external_state_unchanged": True,
    })


def t04() -> dict[str, Any]:
    fields = [
        ("counterpart_arm", {"arm": "B"}),
        ("gold", "hidden-gold"),
        ("retrieval_grade", 3),
        ("correctness", True),
        ("condition", "reference"),
        ("ridi_result", "PASS"),
    ]
    failures = []
    for field, value in fields:
        payload = make_neutral_arm()
        payload[field] = value
        rejected, detail = explicit_rejection(lambda p=payload: adapter.validate_neutral_arm(p))
        if not rejected:
            failures.append({"field": field, "detail": detail})
    return result_fail(failures) if failures else result_pass({"rejected_fields": [x[0] for x in fields]})


def t05() -> dict[str, Any]:
    # Same passage bindings, but a different case and arm.
    arm_a = make_neutral_arm(case_id="F3-T05-A", arm="A", passage_namespace="t05-shared")
    arm_b = make_neutral_arm(case_id="F3-T05-B", arm="B", passage_namespace="t05-shared")
    foreign = build_resolved_state(
        arm_b,
        tag="t05-foreign",
        required_independent_supports=1,
        install_independence=True,
    )
    control = require_positive_control("F3-T05", arm_b, foreign)

    ok, detail = nonclosure_or_rejection(lambda: execute(arm_a, foreign))
    if ok:
        return result_pass({"positive_control": control, "mutation": detail})
    return result_fail({
        "finding": "foreign resolved-state package was accepted for a different case/arm",
        "positive_control": control,
        "mutation": detail,
    })
def t06() -> dict[str, Any]:
    payload = make_neutral_arm(case_id="F3-T06")
    resolved = build_resolved_state(
        payload,
        tag="t06",
        required_independent_supports=1,
        install_independence=True,
    )
    control = require_positive_control("F3-T06", payload, resolved)
    mutated = copy.deepcopy(resolved)
    mutated["claim_identity_map"] = {"c1": "id:foreign-subject:v9"}
    ok, detail = nonclosure_or_rejection(lambda: execute(payload, mutated))
    return result_pass({"positive_control": control, "mutation": detail}) if ok else result_fail({"positive_control": control, "mutation": detail})
def t07() -> dict[str, Any]:
    payload = make_neutral_arm(case_id="F3-T07")
    resolved = build_resolved_state(
        payload,
        tag="t07",
        required_independent_supports=1,
        install_independence=True,
        controller_scope=None,
        snapshot_scope="scope:f3:narrow",
    )
    control = require_positive_control("F3-T07", payload, resolved)
    mutated = copy.deepcopy(resolved)
    mutated["controller_scope"] = "scope:f3:requested-broad"
    ok, detail = nonclosure_or_rejection(lambda: execute(payload, mutated))
    return result_pass({"positive_control": control, "mutation": detail}) if ok else result_fail({"positive_control": control, "mutation": detail})
def t08() -> dict[str, Any]:
    payload = make_neutral_arm(case_id="F3-T08")
    resolved = build_resolved_state(
        payload,
        tag="t08",
        required_independent_supports=1,
        install_independence=True,
    )
    control = require_positive_control("F3-T08", payload, resolved)
    mutated = copy.deepcopy(resolved)
    mutated["decision_as_of"] = "2027-01-15"
    ok, detail = nonclosure_or_rejection(lambda: execute(payload, mutated))
    return result_pass({"positive_control": control, "mutation": detail}) if ok else result_fail({"positive_control": control, "mutation": detail})
def t10() -> dict[str, Any]:
    payload = make_neutral_arm(case_id="F3-T10")
    control_state = build_resolved_state(
        payload,
        tag="t10-control",
        shared_lineage=False,
        required_independent_supports=2,
        install_independence=True,
    )
    control = require_positive_control("F3-T10", payload, control_state)

    mutated = build_resolved_state(
        payload,
        tag="t10-mutated",
        shared_lineage=True,
        required_independent_supports=2,
        install_independence=False,
    )
    ok, detail = nonclosure_or_rejection(lambda: execute(payload, mutated))
    return result_pass({"positive_control": control, "mutation": detail}) if ok else result_fail({"positive_control": control, "mutation": detail})
def t11() -> dict[str, Any]:
    payload = make_neutral_arm(case_id="F3-T11")
    resolved = build_resolved_state(
        payload,
        tag="t11",
        shared_lineage=False,
        required_independent_supports=2,
        install_independence=True,
    )
    control = require_positive_control("F3-T11", payload, resolved)
    mutated = copy.deepcopy(resolved)
    mutated["requirements"] = {"c1": {"required_independent_supports": 11}}
    ok, detail = nonclosure_or_rejection(lambda: execute(payload, mutated))
    return result_pass({"positive_control": control, "mutation": detail}) if ok else result_fail({"positive_control": control, "mutation": detail})
def t12() -> dict[str, Any]:
    payload = make_neutral_arm(case_id="F3-T12")
    resolved = build_resolved_state(
        payload,
        tag="t12",
        required_independent_supports=1,
        install_independence=True,
    )
    control = require_positive_control("F3-T12", payload, resolved)
    mutated = copy.deepcopy(resolved)
    for row in mutated["host_trust_registrations"]:
        if row["authority_class"] == "IDENTITY":
            row["authority_id"] = "F3_WRONG_IDENTITY_AUTHORITY"
            break
    ok, detail = nonclosure_or_rejection(lambda: execute(payload, mutated))
    return result_pass({"positive_control": control, "mutation": detail}) if ok else result_fail({"positive_control": control, "mutation": detail})

