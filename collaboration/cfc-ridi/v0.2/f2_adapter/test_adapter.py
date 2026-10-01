from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("f2_adapter", HERE / "adapter.py")
assert SPEC and SPEC.loader
adapter = importlib.util.module_from_spec(SPEC)
import sys
sys.modules["f2_adapter"] = adapter
SPEC.loader.exec_module(adapter)


def h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def arm():
    q = "sweet leavened bread prepared for easter in romania"
    passages = []
    for i in range(1, 11):
        text = f"registered passage {i}"
        passages.append({
            "ordinal": i,
            "docid": f"doc{i}",
            "text": text,
            "text_sha256": h(text),
        })
    return {
        "schema_version": adapter.NEUTRAL_SCHEMA_VERSION,
        "case_id": "RAG-nq-test1035",
        "arm": "A",
        "dataset": "nq",
        "task": "qa",
        "draw": 0,
        "query": {
            "qid": "test1035",
            "source_qid": "test1035",
            "question": q,
            "question_sha256": h(q),
        },
        "source_binding": {
            "registered_context_line_sha256": "1" * 64,
            "source_contexts_corpus_sha256": adapter.SOURCE_CORPUS_SHA256,
            "source_registration": "txwdv",
            "prompt_sha256": "2" * 64,
        },
        "passages": passages,
        "recorded_endpoint": {
            "endpoint_record_sha256": "3" * 64,
            "raw": "Cozonac [1]",
            "canonical": "cozonac",
            "model": "Qwen/Qwen3-8B",
            "revision": "b968826d9c46dd6066d109eabc6255188de91218",
            "source_generations_sha256": "4" * 64,
            "source_result_archive": "RIDI_RAG_RESULTS__PRIMARY_H1_H2.zip",
        },
        "neutrality": {
            "adapter_unit": "ONE_ARM_ONLY",
            "candidate_claim_source": "recorded_endpoint.canonical",
            "endpoint_is_candidate_claim_only": True,
            "authority_asserted_by_schema": False,
            "semantic_support_asserted_by_schema": False,
            "ground_truth_withheld": True,
            "retrieval_grade_withheld": True,
            "prompt_text_withheld": True,
            "perturbation_condition_withheld": True,
            "counterpart_arm_withheld": True,
            "ridi_result_withheld": True,
            "correctness_withheld": True,
        },
    }


def assert_raises(exc, fn):
    try:
        fn()
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__}")


def test_prepare_is_deterministic_and_neutral():
    payload = arm()
    a = adapter.prepare_artifacts(payload)
    b = adapter.prepare_artifacts(json.loads(json.dumps(payload)))
    assert a == b
    manifest = a["mapping_manifest"]
    assert manifest["candidate_conclusion"] == "cozonac"
    assert manifest["authority_state"] == "NOT_ASSERTED_BY_NEUTRAL_SCHEMA"
    assert manifest["semantic_state"]["identity"] == "UNRESOLVED_UNTIL_EXTERNAL_STATE"
    rendered = json.dumps(manifest, sort_keys=True)
    assert "Cozonac [1]" not in rendered
    assert "registered passage 1" not in rendered
    assert '"gold"' not in rendered
    assert '"grade"' not in rendered
    assert '"condition"' not in rendered
    assert a["substantive_execution_authorized"] is False


def test_exact_ten_ordered_passages_required():
    payload = arm()
    payload["passages"][1]["ordinal"] = 1
    assert_raises(adapter.BindingError, lambda: adapter.validate_neutral_arm(payload))

    payload = arm()
    payload["passages"][0], payload["passages"][1] = (
        payload["passages"][1],
        payload["passages"][0],
    )
    assert_raises(adapter.BindingError, lambda: adapter.validate_neutral_arm(payload))


def test_hash_bindings_are_checked():
    payload = arm()
    payload["query"]["question"] += "?"
    assert_raises(adapter.BindingError, lambda: adapter.validate_neutral_arm(payload))

    payload = arm()
    payload["passages"][0]["text"] += " changed"
    assert_raises(adapter.BindingError, lambda: adapter.validate_neutral_arm(payload))

    payload = arm()
    payload["source_binding"]["source_contexts_corpus_sha256"] = "f" * 64
    assert_raises(adapter.BindingError, lambda: adapter.validate_neutral_arm(payload))


def test_neutrality_contract_is_exact():
    payload = arm()
    payload["neutrality"]["authority_asserted_by_schema"] = True
    assert_raises(
        adapter.NeutralSchemaError,
        lambda: adapter.validate_neutral_arm(payload),
    )

    payload = arm()
    payload["gold"] = "cozonac"
    assert_raises(
        adapter.NeutralSchemaError,
        lambda: adapter.validate_neutral_arm(payload),
    )


def test_authority_requirements_do_not_invent_state():
    prepared = adapter.prepare_neutral_arm(arm())
    req = adapter.authority_requirements(prepared)
    joined = json.dumps(req, sort_keys=True)
    assert "identity_state_and_authority" in joined
    assert "support_set_independence_state_and_authority_if_required" in joined
    assert "do_not_infer_independence_from_distinct_ids" in joined
    assert "cozonac" not in joined


def test_anchor_wheel_identity_is_enforced(tmp_dir=None):
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as d:
        p = Path(d) / "anchor.whl"
        p.write_bytes(b"not-the-frozen-wheel")
        assert_raises(
            adapter.ImplementationBoundaryError,
            lambda: adapter.verify_anchor_wheel_file(p),
        )


def test_execution_requires_external_resolved_state():
    payload = arm()
    prepared = adapter.prepare_neutral_arm(payload)
    assert_raises(
        adapter.AuthorityStateRequired,
        lambda: adapter._validate_resolved_state(prepared, {}),
    )


def test_source_has_no_private_anchor_reference():
    source = (HERE / "adapter.py").read_text(encoding="utf-8")
    assert "cfc_anchor._" not in source
    assert "importlib.import_module" not in source
    assert "sys.modules" not in source


def run():
    tests = [
        test_prepare_is_deterministic_and_neutral,
        test_exact_ten_ordered_passages_required,
        test_hash_bindings_are_checked,
        test_neutrality_contract_is_exact,
        test_authority_requirements_do_not_invent_state,
        test_anchor_wheel_identity_is_enforced,
        test_execution_requires_external_resolved_state,
        test_source_has_no_private_anchor_reference,
    ]
    for fn in tests:
        fn()
    print(f"PASS {len(tests)}/{len(tests)}")


if __name__ == "__main__":
    run()
