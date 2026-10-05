from __future__ import annotations

import hashlib
import json
from typing import Any

from pro_beta.contracts import HAWMSnapshot


STATE_MONITOR_VERSION = "STATE_MONITOR_V0_1"
STATE_MONITOR_BOUNDARY = (
    "EXPLICIT_HAWM_WORKING_STATE_TRANSITIONS_ONLY_NO_FREE_TEXT_SEMANTIC_INFERENCE"
)

NO_MONITOR_ALERT = "NO_MONITOR_ALERT"
STATE_TRANSITION_ALERT = "STATE_TRANSITION_ALERT"
UNRESOLVED = "UNRESOLVED"

NO_ADDITIONAL_BLOCK = "NO_ADDITIONAL_BLOCK_FROM_STATE_MONITOR_ONLY"
BLOCK_STATE_CARRY_FORWARD = "BLOCK_STATE_CARRY_FORWARD_REVIEW_REQUIRED"


def _canonicalize(value: Any, *, path: tuple[str, ...] = ()) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _canonicalize(value[key], path=path + (str(key),))
            for key in sorted(value, key=str)
        }
    if isinstance(value, list):
        items = [_canonicalize(item, path=path + ("[]",)) for item in value]
        if path == ("state", "cfc_structured", "evidence"):
            return sorted(
                items,
                key=lambda item: json.dumps(
                    item,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ),
            )
        return items
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"unsupported state value type: {type(value).__name__}")


def _state_fingerprint(snapshot: HAWMSnapshot) -> tuple[str | None, str | None]:
    if not isinstance(snapshot.state, dict):
        return None, "HAWM_STATE_NOT_OBJECT"
    try:
        canonical = _canonicalize(snapshot.state, path=("state",))
    except (TypeError, ValueError):
        return None, "HAWM_STATE_NOT_CANONICALIZABLE"
    payload = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest(), None


def _unresolved_present(snapshot: HAWMSnapshot) -> tuple[bool | None, str | None]:
    if not isinstance(snapshot.state, dict):
        return None, "HAWM_STATE_NOT_OBJECT"
    value = snapshot.state.get("unresolved")
    if value is None:
        return False, None
    if not isinstance(value, str):
        return None, "UNRESOLVED_FIELD_NOT_STRING"
    return bool(value.strip()), None


def _result(
    *,
    status: str,
    reason: str,
    previous: HAWMSnapshot,
    current: HAWMSnapshot,
    previous_unresolved_present: bool | None,
    current_unresolved_present: bool | None,
    current_snapshot_evaluated: bool | None,
) -> dict[str, Any]:
    blocked = status != NO_MONITOR_ALERT
    return {
        "version": STATE_MONITOR_VERSION,
        "status": status,
        "reason": reason,
        "previous_snapshot_id": previous.snapshot_id,
        "current_snapshot_id": current.snapshot_id,
        "previous_unresolved_present": previous_unresolved_present,
        "current_unresolved_present": current_unresolved_present,
        "current_snapshot_evaluated": current_snapshot_evaluated,
        "requires_review": blocked,
        "propagation_effect": (
            BLOCK_STATE_CARRY_FORWARD if blocked else NO_ADDITIONAL_BLOCK
        ),
        "boundary": STATE_MONITOR_BOUNDARY,
        "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
    }


def assess_state_transition(
    previous: HAWMSnapshot,
    current: HAWMSnapshot,
    *,
    current_snapshot_evaluated: bool,
) -> dict[str, Any]:
    """Assess one explicit HAWM working-state transition.

    v0.1 watches one narrow workflow invariant: an explicit non-empty
    unresolved working-state field must not disappear and silently inherit
    prior authority unless the current snapshot has itself been evaluated via
    an exact persisted CFC run binding.

    The boolean is an orchestration input. Production integration must derive it
    from persisted snapshot-to-run linkage, never from user input or heuristic
    existence of some run.
    """
    if not isinstance(current_snapshot_evaluated, bool):
        return _result(
            status=UNRESOLVED,
            reason="CURRENT_SNAPSHOT_EVALUATION_FLAG_INVALID",
            previous=previous,
            current=current,
            previous_unresolved_present=None,
            current_unresolved_present=None,
            current_snapshot_evaluated=None,
        )

    if previous.conversation_id != current.conversation_id:
        return _result(
            status=UNRESOLVED,
            reason="CROSS_CONVERSATION_TRANSITION",
            previous=previous,
            current=current,
            previous_unresolved_present=None,
            current_unresolved_present=None,
            current_snapshot_evaluated=current_snapshot_evaluated,
        )

    previous_fingerprint, previous_state_error = _state_fingerprint(previous)
    current_fingerprint, current_state_error = _state_fingerprint(current)
    if previous_state_error is not None or current_state_error is not None:
        reasons = []
        if previous_state_error is not None:
            reasons.append(f"PREVIOUS_{previous_state_error}")
        if current_state_error is not None:
            reasons.append(f"CURRENT_{current_state_error}")
        return _result(
            status=UNRESOLVED,
            reason="+".join(reasons),
            previous=previous,
            current=current,
            previous_unresolved_present=None,
            current_unresolved_present=None,
            current_snapshot_evaluated=current_snapshot_evaluated,
        )

    if (
        previous.snapshot_id == current.snapshot_id
        and previous_fingerprint != current_fingerprint
    ):
        return _result(
            status=UNRESOLVED,
            reason="SNAPSHOT_ID_CONTENT_MISMATCH",
            previous=previous,
            current=current,
            previous_unresolved_present=None,
            current_unresolved_present=None,
            current_snapshot_evaluated=current_snapshot_evaluated,
        )

    previous_unresolved, previous_unresolved_error = _unresolved_present(previous)
    current_unresolved, current_unresolved_error = _unresolved_present(current)
    if previous_unresolved_error is not None or current_unresolved_error is not None:
        reasons = []
        if previous_unresolved_error is not None:
            reasons.append(f"PREVIOUS_{previous_unresolved_error}")
        if current_unresolved_error is not None:
            reasons.append(f"CURRENT_{current_unresolved_error}")
        return _result(
            status=UNRESOLVED,
            reason="+".join(reasons),
            previous=previous,
            current=current,
            previous_unresolved_present=previous_unresolved,
            current_unresolved_present=current_unresolved,
            current_snapshot_evaluated=current_snapshot_evaluated,
        )

    if previous_unresolved and not current_unresolved:
        if not current_snapshot_evaluated:
            return _result(
                status=STATE_TRANSITION_ALERT,
                reason="UNRESOLVED_CLEARED_WITHOUT_CURRENT_SNAPSHOT_EVALUATION",
                previous=previous,
                current=current,
                previous_unresolved_present=True,
                current_unresolved_present=False,
                current_snapshot_evaluated=False,
            )
        return _result(
            status=NO_MONITOR_ALERT,
            reason="UNRESOLVED_CLEARED_AFTER_CURRENT_SNAPSHOT_EVALUATION",
            previous=previous,
            current=current,
            previous_unresolved_present=True,
            current_unresolved_present=False,
            current_snapshot_evaluated=True,
        )

    if not previous_unresolved and current_unresolved:
        reason = "UNRESOLVED_ADDED"
    elif previous_unresolved and current_unresolved:
        reason = "UNRESOLVED_STILL_PRESENT"
    else:
        reason = "NO_UNRESOLVED_CLEARANCE"

    return _result(
        status=NO_MONITOR_ALERT,
        reason=reason,
        previous=previous,
        current=current,
        previous_unresolved_present=previous_unresolved,
        current_unresolved_present=current_unresolved,
        current_snapshot_evaluated=current_snapshot_evaluated,
    )
