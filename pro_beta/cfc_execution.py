from __future__ import annotations

from typing import Any

ALLOWED_PREPARED_CASES = {
    "CASE_01_UNRESOLVED_POSITIVE",
    "CASE_03_ACTIVE_CONFLICT_NO_RESOLUTION",
    "CASE_07_VALID_POSITIVE_CLOSURE",
    "CASE_10_INCOMPLETE_REQUIRED_CHECKS",
}


def run_prepared_case(case_id: str) -> dict[str, Any]:
    """Execute one preserved demonstrator fixture through frozen CFC Anchor.

    This does not parse or evaluate the user's conversation text. It is a
    prepared synthetic fixture used to prove the separate CFC execution path.
    """
    if case_id not in ALLOWED_PREPARED_CASES:
        raise ValueError("CFC_PREPARED_CASE_NOT_ALLOWED")

    from demonstrator.server import run_case

    payload = run_case(case_id)
    result = payload["result"]
    return {
        "case_id": case_id,
        "controller_anchor": "0.2.90rc1",
        "controller_result": result,
        "presentation": payload["presentation"],
        "replay_matches_reference": payload.get("replay_matches_reference"),
        "boundary": "PREPARED_SYNTHETIC_FIXTURE_NOT_CONVERSATION_ANALYSIS",
    }


def run_structured_hawm_state(state: dict[str, Any]) -> dict[str, Any]:
    """Run only explicit structured HAWM CFC fields through the frozen anchor.

    Free-text HAWM fields such as goal, task, claims, evidence, constraints,
    unresolved, and next_action are deliberately ignored here. This adapter
    performs no natural-language inference.
    """
    structured = state.get("cfc_structured")
    if not isinstance(structured, dict):
        raise ValueError("HAWM_CFC_STRUCTURED_STATE_REQUIRED")

    if (
        structured.get("provenance_shape") == "SHARED_LINEAGE"
        and structured.get("independence_authority") == "VERIFIED"
    ):
        raise ValueError("HAWM_CFC_CONTRADICTORY_INDEPENDENCE_STATE")

    cfg = {
        "conclusion": structured.get("conclusion", "POSITIVE"),
        "required_independent_supports": structured.get(
            "required_independent_supports", 1
        ),
        "provenance_shape": structured.get("provenance_shape", "DISTINCT"),
        "independence_authority": structured.get(
            "independence_authority", "NONE"
        ),
        "scope": structured.get("scope", "EXPECTED"),
        "evidence": structured.get("evidence"),
    }

    from demonstrator.server import run_custom

    payload = run_custom(cfg)
    result = payload["result"]
    return {
        "case_id": "HAWM_STRUCTURED_CUSTOM",
        "controller_anchor": "0.2.90rc1",
        "controller_result": result,
        "presentation": payload["presentation"],
        "replay_matches_reference": None,
        "boundary": "STRUCTURED_HAWM_FIELDS_ONLY_NO_NATURAL_LANGUAGE_INFERENCE",
        "mapped_input": result.get("custom_input", cfg),
    }
