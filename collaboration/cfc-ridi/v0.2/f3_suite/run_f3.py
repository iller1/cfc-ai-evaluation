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



def require_positive_control(
    label: str,
    payload: dict[str, Any],
    resolved: dict[str, Any],
) -> dict[str, Any]:
    out = execute(payload, resolved)
    if out.get("control_closure") is not True:
        raw = out.get("raw") if isinstance(out.get("raw"), dict) else {}
        diag = {
            "claim_support_policy_violations": raw.get("claim_support_policy_violations"),
            "matching_support_universes": raw.get("matching_support_universes"),
            "critical_unresolved": raw.get("critical_unresolved"),
            "global_consistency_violations": raw.get("global_consistency_violations"),
            "constraint_relation_coverage_violations": raw.get("constraint_relation_coverage_violations"),
            "constraint_coverage_violations": raw.get("constraint_coverage_violations"),
            "gates": raw.get("gates"),
        }
        raise RuntimeError(
            f"{label}: positive control did not close; "
            f"control_closure={out.get('control_closure')!r}, "
            f"stop_type={out.get('stop_type')!r}, "
            f"claim_states={out.get('claim_states')!r}, "
            f"diagnostics={diag!r}"
        )
    return {
        "control_closure": True,
        "stop_type": out.get("stop_type"),
        "claim_states": out.get("claim_states"),
    }


def run_control_mutation_probe(test_id: str) -> dict[str, Any]:
    probe = HERE / "probe_f3.py"

    def one(mode: str) -> dict[str, Any]:
        proc = subprocess.run(
            [sys.executable, str(probe), test_id, mode],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
        if not proc.stdout.strip():
            raise RuntimeError(
                f"{test_id}/{mode}: probe emitted no JSON; "
                f"returncode={proc.returncode}; stderr={proc.stderr!r}"
            )
        try:
            return json.loads(proc.stdout)
        except Exception as exc:
            raise RuntimeError(
                f"{test_id}/{mode}: invalid probe JSON: {proc.stdout!r}; "
                f"stderr={proc.stderr!r}"
            ) from exc

    control = one("control")
    mutation = one("mutation")

    if control.get("execution") != "RESULT":
        return result_fail({
            "finding": "reference control was not executable",
            "control": control,
            "mutation": mutation,
        })

    if mutation.get("execution") == "EXPLICIT_REJECTION":
        return result_pass({
            "attribution": "EXPLICIT_REJECTION",
            "control": control,
            "mutation": mutation,
        })

    if mutation.get("execution") != "RESULT":
        return result_fail({
            "finding": "mutation probe produced unknown state",
            "control": control,
            "mutation": mutation,
        })

    if mutation.get("summary") == control.get("summary"):
        return result_fail({
            "finding": "mutation was silently ignored; diagnostic result identical to control",
            "control": control,
            "mutation": mutation,
        })

    return result_pass({
        "attribution": "MUTATION_CHANGED_DIAGNOSTIC_STATE",
        "control": control,
        "mutation": mutation,
    })

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
    return run_control_mutation_probe("F3-T05")
def t06() -> dict[str, Any]:
    return run_control_mutation_probe("F3-T06")
def t07() -> dict[str, Any]:
    return run_control_mutation_probe("F3-T07")
def t08() -> dict[str, Any]:
    return run_control_mutation_probe("F3-T08")
def t09() -> dict[str, Any]:
    payload = make_neutral_arm(case_id="F3-T09")
    resolved = build_resolved_state(payload, tag="t09")
    resolved["passages"][0], resolved["passages"][1] = (
        resolved["passages"][1],
        resolved["passages"][0],
    )
    rejected, detail = explicit_rejection(
        lambda: adapter._validate_resolved_state(adapter.prepare_neutral_arm(payload), resolved)
    )
    return result_pass(detail) if rejected else result_fail(detail)



def t10() -> dict[str, Any]:
    return run_control_mutation_probe("F3-T10")
def t11() -> dict[str, Any]:
    return run_control_mutation_probe("F3-T11")
def t12() -> dict[str, Any]:
    return run_control_mutation_probe("F3-T12")
def t13() -> dict[str, Any]:
    payload = make_neutral_arm(case_id="F3-T13")
    base = build_resolved_state(payload, tag="t13")
    mutations = {
        "missing_identity": lambda x: x.pop("identity"),
        "missing_topology": lambda x: x.pop("failure_domain_topology"),
        "missing_snapshot": lambda x: x.pop("snapshot"),
        "missing_passage_semantics": lambda x: x["passages"][0].pop("source_semantics"),
        "missing_passage_provenance": lambda x: x["passages"][0].pop("provenance"),
        "missing_evidence_authority": lambda x: x["passages"][0].pop("evidence_authority"),
        "missing_epistemic_role": lambda x: x["passages"][0].pop("epistemic_role"),
    }
    failures = []
    details = {}
    prepared = adapter.prepare_neutral_arm(payload)
    for name, mutate in mutations.items():
        r = copy.deepcopy(base)
        mutate(r)
        rejected, detail = explicit_rejection(lambda r=r: adapter._validate_resolved_state(prepared, r))
        details[name] = detail
        if not rejected:
            failures.append(name)
    return result_fail({"not_rejected": failures, "details": details}) if failures else result_pass(details)


def t14() -> dict[str, Any]:
    variants = [
        make_neutral_arm(
            case_id="F3-T14-NQ-A",
            arm="A",
            dataset="nq",
            task="qa",
            passage_namespace="t14a",
        ),
        make_neutral_arm(
            case_id="F3-T14-FEVER-B",
            arm="B",
            dataset="fever",
            task="verdict",
            passage_namespace="t14b",
        ),
    ]
    observations = []
    for payload in variants:
        # Mutation class 1: withheld-state injection.
        p = copy.deepcopy(payload)
        p["gold"] = "forbidden"
        reject_extra, extra_detail = explicit_rejection(
            lambda p=p: adapter.validate_neutral_arm(p)
        )

        # Mutation class 2: passage-state rebinding. Use a minimal resolved-state
        # validation object so case-agnostic checking does not depend on global
        # fixture registries inside the frozen controller.
        prepared = adapter.prepare_neutral_arm(payload)
        passage_rows = []
        for ordinal, docid, text_sha in prepared.passage_bindings:
            passage_rows.append(
                {
                    "neutral_binding": {
                        "ordinal": ordinal,
                        "docid": docid,
                        "text_sha256": text_sha,
                    },
                    "source_semantics": {},
                    "evidence_draft_kwargs": {},
                    "provenance": {},
                    "evidence_authority": {},
                    "epistemic_role": {},
                }
            )
        passage_rows[0], passage_rows[1] = passage_rows[1], passage_rows[0]
        minimal_resolved = {
            "decision_as_of": "2026-09-03",
            "controller_scope": None,
            "claim_identity_map": {"c1": "id:fixture"},
            "requirements": {"c1": {"required_independent_supports": 1}},
            "host_trust_registrations": [
                {
                    "authority_class": "FIXTURE",
                    "authority_id": "FIXTURE",
                    "verifier": object(),
                }
            ],
            "identity": {},
            "failure_domain_topology": {},
            "passages": passage_rows,
            "snapshot": {},
        }
        reject_rebind, rebind_detail = explicit_rejection(
            lambda prepared=prepared, resolved=minimal_resolved:
                adapter._validate_resolved_state(prepared, resolved)
        )

        observations.append(
            {
                "case_id": payload["case_id"],
                "arm": payload["arm"],
                "dataset": payload["dataset"],
                "task": payload["task"],
                "withheld_injection_rejected": reject_extra,
                "withheld_detail": extra_detail,
                "rebinding_rejected": reject_rebind,
                "rebinding_detail": rebind_detail,
            }
        )

    if not all(
        x["withheld_injection_rejected"] and x["rebinding_rejected"]
        for x in observations
    ):
        return result_fail(observations)
    return result_pass(observations)

def t15() -> dict[str, Any]:
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_strings = [
        "cfc_anchor._",
        "monkeypatch",
        "__dict__",
        "sys.modules",
        "importlib.import_module",
    ]
    found_strings = [s for s in forbidden_strings if s in source]
    if found_strings:
        return result_fail({"forbidden_source_markers": found_strings})

    import_names = set()
    controller_calls = set()
    private_attrs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "cfc_anchor":
            import_names.update(alias.name for alias in node.names)
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            private_attrs.append(node.attr)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in adapter._F1_CONTROLLER_METHODS:
                controller_calls.add(node.func.attr)

    allowed_imports = set(adapter._F1_PUBLIC_IMPORTS)
    if import_names and not import_names.issubset(allowed_imports):
        return result_fail({
            "unapproved_imports": sorted(import_names - allowed_imports),
            "imports": sorted(import_names),
        })

    # Adapter dynamically imports the public package root, so direct from-imports may be empty.
    probe = adapter.public_interface_probe(WHEEL_PATH)
    if probe.get("private_engine_accessed") is not False:
        return result_fail({"probe": probe})
    if private_attrs:
        # Private methods defined/called on this adapter module itself are allowed; Controller-private
        # access would show up as c.<_name> in source. Check that form separately.
        private_controller = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and node.attr.startswith("_")
                and isinstance(node.value, ast.Name)
                and node.value.id == "c"
            ):
                private_controller.append(node.attr)
        if private_controller:
            return result_fail({"private_controller_attributes": sorted(set(private_controller))})

    if not controller_calls.issubset(set(adapter._F1_CONTROLLER_METHODS)):
        return result_fail({
            "unapproved_controller_calls": sorted(controller_calls - set(adapter._F1_CONTROLLER_METHODS))
        })

    return result_pass({
        "public_probe": {
            "private_engine_accessed": probe["private_engine_accessed"],
            "anchor_wheel_sha256": probe["anchor_wheel_artifact_verified"]["sha256"],
        },
        "controller_calls_observed_in_source": sorted(controller_calls),
        "accepted_method_surface_size": len(adapter._F1_CONTROLLER_METHODS),
    })


TESTS: list[tuple[str, str, Callable[[], dict[str, Any]]]] = [
    ("F3-T01", "Exact F2 baseline identity", t01),
    ("F3-T02", "Deterministic one-arm preparation", t02),
    ("F3-T03", "Hidden neutral-field promotion", t03),
    ("F3-T04", "Counterpart/withheld-state injection", t04),
    ("F3-T05", "Cross-case / cross-arm resolved-state substitution", t05),
    ("F3-T06", "Claim-identity substitution", t06),
    ("F3-T07", "Scope broadening", t07),
    ("F3-T08", "Decision-as-of / freshness substitution", t08),
    ("F3-T09", "Passage-state rebinding", t09),
    ("F3-T10", "Dependency / independence preservation", t10),
    ("F3-T11", "Required-support mismatch", t11),
    ("F3-T12", "Host-trust / verifier mismatch", t12),
    ("F3-T13", "Missing/malformed resolved semantic state", t13),
    ("F3-T14", "Case-agnostic behavior", t14),
    ("F3-T15", "Public-interface confinement", t15),
]


def _single_test(test_id: str) -> dict[str, Any]:
    matches = [(tid, title, fn) for tid, title, fn in TESTS if tid == test_id]
    if len(matches) != 1:
        return {
            "test_id": test_id,
            "title": "UNKNOWN",
            "status": "HARNESS_ERROR",
            "detail": {"error": "unknown test id"},
        }
    tid, title, fn = matches[0]
    try:
        outcome = fn()
        return {"test_id": tid, "title": title, **outcome}
    except Exception as exc:
        return {
            "test_id": tid,
            "title": title,
            "status": "HARNESS_ERROR",
            "detail": {
                "suite_exception": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            },
        }


def run_one(test_id: str) -> dict[str, Any]:
    for tid, title, fn in TESTS:
        if tid != test_id:
            continue
        try:
            outcome = fn()
        except Exception as exc:
            outcome = result_fail({
                "suite_exception": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            })
        return {"test_id": tid, "title": title, **outcome}
    raise ValueError(f"unknown test id: {test_id}")


def run_all() -> dict[str, Any]:
    results = []
    for test_id, title, _fn in TESTS:
        proc = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--single",
                test_id,
            ],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
        try:
            outcome = json.loads(proc.stdout)
        except Exception:
            outcome = {
                "test_id": test_id,
                "title": title,
                "status": "FAIL",
                "detail": {
                    "harness_parse_error": True,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                },
            }
        results.append(outcome)
        print(f"{test_id}: {outcome['status']}")
        if outcome["status"] == "FAIL":
            print(json.dumps(outcome["detail"], indent=2, sort_keys=True, default=str))

    passed = sum(x["status"] == "PASS" for x in results)
    failed = len(results) - passed
    overall = PASS_STATUS if failed == 0 else FAIL_STATUS
    return {
        "suite": "CFC-RIDI-v0.2-F3-R1",
        "criteria_sha256": CRITERIA_SHA256,
        "f2_adapter_commit": F2_COMMIT,
        "f2_adapter_sha256": EXPECTED_F2["adapter.py"]["sha256"],
        "execution_isolation": "FRESH_PROCESS_PER_TEST",
        "tests_total": len(results),
        "tests_passed": passed,
        "tests_failed": failed,
        "overall_status": overall,
        "results": results,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--single", choices=[x[0] for x in TESTS])
    ap.add_argument(
        "--output",
        type=Path,
        default=HERE / "F3_RESULTS.json",
    )
    args = ap.parse_args()

    if args.single:
        one = run_one(args.single)
        print(json.dumps(one, sort_keys=True, default=str))
        raise SystemExit(0 if one["status"] == "PASS" else 1)

    report = run_all()
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    print("OVERALL:", report["overall_status"])
    print("RESULT_FILE:", args.output)
    raise SystemExit(0 if report["tests_failed"] == 0 else 1)


if __name__ == "__main__":
    main()
