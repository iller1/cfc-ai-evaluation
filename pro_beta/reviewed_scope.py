"""Server-side schema validation for a user-reviewed SYNTHETIC CFC demo.

Not an evidence authenticity service, independent-source authority, or real-case
CFC execution path. Never accepts model text/claims as source certification.
"""
from __future__ import annotations

import hashlib
from datetime import date
from typing import Any

REFERENCE_AS_OF = "2026-09-03"
WORKING_FIELDS = frozenset({
    "goal", "task", "claims", "evidence", "constraints", "unresolved", "next_action"
})
REVIEW_KEYS = frozenset({
    "claimLabel", "sourceMessageId", "universeConfirmed", "syntheticConfirmed",
    "moreSources", "required", "relation", "records"
})
RECORD_KEYS = frozenset({"id", "date", "disposition", "reason", "polarity", "validity"})
DISPOSITIONS = frozenset({"INCLUDE", "EXCLUDE", "OPEN_ISSUE"})
POLARITIES = frozenset({"POSITIVE", "NEGATIVE"})
VALIDITIES = frozenset({"CURRENT", "STALE"})


class ReviewValidationError(ValueError):
    """Stable error code, never echoes customer text."""


def reject(code: str) -> None:
    raise ReviewValidationError(code)


def _string(value: Any, limit: int, code: str) -> str:
    if not isinstance(value, str) or len(value) > limit or "\x00" in value:
        reject(code)
    return value.strip()


def _date(value: Any) -> str | None:
    text = _string(value, 10, "REVIEW_SOURCE_DATE_INVALID")
    if not text:
        return None
    try:
        parsed = date.fromisoformat(text)
        if parsed.isoformat() != text:
            reject("REVIEW_SOURCE_DATE_INVALID")
    except ValueError:
        reject("REVIEW_SOURCE_DATE_INVALID")
    return text


def validate_reviewed_demo_scope(
    review: Any,
    working_state: Any,
    *,
    context_message: Any = None,
) -> dict[str, Any]:
    """Only whitelisted, explicit human selections enter the demo configuration."""
    if not isinstance(review, dict) or set(review) != REVIEW_KEYS:
        reject("REVIEW_SCHEMA_REQUIRED")
    if not isinstance(working_state, dict) or not set(working_state).issubset(WORKING_FIELDS):
        reject("REVIEW_WORKING_STATE_INVALID")
    if review["moreSources"] is not False:
        reject("REVIEW_MORE_THAN_FOUR_SOURCES_UNSUPPORTED")
    if review["universeConfirmed"] is not True:
        reject("REVIEW_SOURCE_UNIVERSE_DECLARATION_REQUIRED")
    if review["syntheticConfirmed"] is not True:
        reject("REVIEW_SYNTHETIC_DEMO_CONSENT_REQUIRED")
    label = _string(review["claimLabel"], 160, "REVIEW_CLAIM_LABEL_INVALID")
    if not label:
        reject("REVIEW_CLAIM_LABEL_REQUIRED")
    message_id = _string(review["sourceMessageId"], 128, "REVIEW_CONTEXT_ID_INVALID")
    if message_id:
        if (
            context_message is None
            or getattr(context_message, "message_id", None) != message_id
            or getattr(context_message, "role", None) != "assistant"
            or not getattr(context_message, "provider", None)
            or getattr(context_message, "authority", None) != "MODEL_REPLY_UNCHECKED"
            or getattr(context_message, "cfc_status", None) != "NOT_CONNECTED_C2"
        ):
            reject("REVIEW_MODEL_CONTEXT_NOT_IN_OWNED_CONVERSATION")
    if type(review["required"]) not in (str, int) or str(review["required"]) not in ("1", "2"):
        reject("REVIEW_REQUIRED_SUPPORTS_INVALID")
    required = int(review["required"])
    relation = _string(review["relation"], 24, "REVIEW_RELATION_INVALID")
    if not isinstance(review["records"], list) or len(review["records"]) != 4:
        reject("REVIEW_FOUR_SLOTS_REQUIRED")

    records: list[dict[str, Any]] = []
    ids: set[str] = set()
    for item in review["records"]:
        if not isinstance(item, dict) or set(item) != RECORD_KEYS:
            reject("REVIEW_RECORD_SCHEMA_INVALID")
        source_id = _string(item["id"], 64, "REVIEW_SOURCE_ID_INVALID")
        disposition = _string(item["disposition"], 32, "REVIEW_STATUS_INVALID")
        reason = _string(item["reason"], 400, "REVIEW_REASON_INVALID")
        source_date = _date(item["date"])
        polarity = _string(item["polarity"], 16, "REVIEW_POLARITY_INVALID")
        validity = _string(item["validity"], 16, "REVIEW_VALIDITY_INVALID")
        if not source_id and not disposition and not reason and source_date is None:
            continue
        if not source_id or disposition not in DISPOSITIONS:
            reject("REVIEW_SOURCE_ID_AND_STATUS_REQUIRED")
        key = source_id.casefold()
        if key in ids:
            reject("REVIEW_DUPLICATE_SOURCE_ID")
        ids.add(key)
        if disposition != "INCLUDE" and not reason:
            reject("REVIEW_EXCLUSION_REASON_REQUIRED")
        if disposition == "INCLUDE" and (polarity not in POLARITIES or validity not in VALIDITIES):
            reject("REVIEW_INCLUDED_SOURCE_MAPPING_REQUIRED")
        records.append({
            "id": source_id,
            "disposition": disposition,
            "reason": reason,
            "source_date": source_date,
            "demo_polarity": polarity if disposition == "INCLUDE" else None,
            "demo_validity": validity if disposition == "INCLUDE" else None,
        })
    included = [r for r in records if r["disposition"] == "INCLUDE"]
    if not 1 <= len(included) <= 2:
        reject("REVIEW_DEMO_SUPPORT_LIMIT_ONE_OR_TWO")
    if len(included) == 2 and relation not in ("DISTINCT", "SHARED_LINEAGE"):
        reject("REVIEW_PAIR_RELATION_UNRESOLVED")
    shape = relation if len(included) == 2 else "DISTINCT"
    working: dict[str, str] = {}
    for key in WORKING_FIELDS:
        text = _string(working_state.get(key, ""), 2000, "REVIEW_WORKING_FIELD_INVALID")
        working[key] = text

    manifest = {
        "manifest_version": "HUMAN_REVIEWED_SYNTHETIC_DEMO_V1",
        "claim_label_for_human_reference_only": label,
        "model_reply_context_message_id": message_id or None,
        "model_reply_context_sha256": (
            hashlib.sha256(context_message.content.encode("utf-8")).hexdigest()
            if message_id else None
        ),
        "universe_declared_by_user_not_externally_verified": True,
        "source_records": records,
        "mapped_source_ids": [r["id"] for r in included],
        "excluded_source_ids": [r["id"] for r in records if r["disposition"] == "EXCLUDE"],
        "open_issue_source_ids": [r["id"] for r in records if r["disposition"] == "OPEN_ISSUE"],
        "synthetic_reference_as_of_date": REFERENCE_AS_OF,
        "source_dates_are_not_input_to_demonstrator": True,
        "analogous_settings": {
            "required_independent_supports": required,
            "provenance_shape": shape,
        },
        "synthetic_independence_authority": "NONE",
        "full_case_authorization": False,
        "boundary": "SOURCE_SCOPE_HUMAN_REVIEWED_ANALOGOUS_SYNTHETIC_CFC_ONLY",
        "server_validation": "SCHEMA_ONLY_USER_DECLARATION_NOT_EVIDENCE_VERIFICATION",
    }
    state = {
        **working,
        "review_manifest": manifest,
        "cfc_structured": {
            "conclusion": "POSITIVE",
            "required_independent_supports": required,
            "provenance_shape": shape,
            "independence_authority": "NONE",
            "scope": "EXPECTED",
            "evidence": [
                {"polarity": r["demo_polarity"], "validity": r["demo_validity"]}
                for r in included
            ],
        },
    }
    return {
        "state": state,
        "status": "USER_DECLARATION_SCHEMA_VALIDATED_NOT_SOURCE_VERIFIED",
        "real_case_status": "REAL_CASE_NOT_CHECKED",
    }
