from __future__ import annotations

import hashlib
import json
from typing import Any

from pro_beta.contracts import HAWMSnapshot


EVIDENCE_DRIFT_VERSION = "EVIDENCE_DRIFT_V0_1"
EVIDENCE_DRIFT_BOUNDARY = (
    "STRUCTURED_HAWM_CFC_STATE_ONLY_NO_FREE_TEXT_EVIDENCE_INFERENCE"
)

NO_DRIFT = "NO_DRIFT"
MATERIAL_DRIFT = "MATERIAL_DRIFT"
UNRESOLVED = "UNRESOLVED"

NO_ADDITIONAL_BLOCK = "NO_ADDITIONAL_BLOCK_FROM_DRIFT_ONLY"
BLOCK_CARRY_FORWARD = "BLOCK_CARRY_FORWARD_REEVALUATION_REQUIRED"


def _canonicalize(value: Any, *, path: tuple[str, ...] = ()) -> Any:
    """Return a deterministic JSON-compatible representation.

    The explicit cfc_structured.evidence collection is treated as a set-like
    support collection for drift purposes: ordering alone is not material.
    Other lists preserve order.
    """
    if isinstance(value, dict):
        return {
            str(key): _canonicalize(value[key], path=path + (str(key),))
            for key in sorted(value, key=str)
        }
    if isinstance(value, list):
        items = [_canonicalize(item, path=path + ("[]",)) for item in value]
        if path == ("cfc_structured", "evidence"):
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
    raise TypeError(f"unsupported structured value type: {type(value).__name__}")


def _structured_state(snapshot: HAWMSnapshot) -> tuple[Any | None, str | None]:
    if not isinstance(snapshot.state, dict):
        return None, "HAWM_STATE_NOT_OBJECT"
    structured = snapshot.state.get("cfc_structured")
    if structured is None:
        return None, "CFC_STRUCTURED_STATE_MISSING"
    if not isinstance(structured, dict):
        return None, "CFC_STRUCTURED_STATE_NOT_OBJECT"
    try:
        return _canonicalize(
            structured,
            path=("cfc_structured",),
        ), None
    except (TypeError, ValueError):
        return None, "CFC_STRUCTURED_STATE_NOT_CANONICALIZABLE"


def _fingerprint(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _changed_paths(left: Any, right: Any, path: str = "cfc_structured") -> list[str]:
    if type(left) is not type(right):
        return [path]

    if isinstance(left, dict):
        changes: list[str] = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}.{key}"
            if key not in left or key not in right:
                changes.append(child)
            else:
                changes.extend(_changed_paths(left[key], right[key], child))
        return changes

    if isinstance(left, list):
        return [] if left == right else [path]

    return [] if left == right else [path]


def _result(
    *,
    status: str,
    reason: str,
    baseline: HAWMSnapshot,
    current: HAWMSnapshot,
    baseline_fingerprint: str | None,
    current_fingerprint: str | None,
    changed_paths: list[str] | None = None,
) -> dict[str, Any]:
    blocked = status != NO_DRIFT
    return {
        "version": EVIDENCE_DRIFT_VERSION,
        "status": status,
        "reason": reason,
        "baseline_snapshot_id": baseline.snapshot_id,
        "current_snapshot_id": current.snapshot_id,
        "baseline_structured_fingerprint": baseline_fingerprint,
        "current_structured_fingerprint": current_fingerprint,
        "changed_paths": sorted(set(changed_paths or [])),
        "requires_re_evaluation": blocked,
        "propagation_effect": (
            BLOCK_CARRY_FORWARD if blocked else NO_ADDITIONAL_BLOCK
        ),
        "boundary": EVIDENCE_DRIFT_BOUNDARY,
        "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
    }



def unresolved_evidence_drift(
    reason: str,
    *,
    baseline_snapshot_id: str | None = None,
    current_snapshot_id: str | None = None,
) -> dict[str, Any]:
    """Build the same fail-closed result shape when comparison inputs are absent."""
    return {
        "version": EVIDENCE_DRIFT_VERSION,
        "status": UNRESOLVED,
        "reason": reason,
        "baseline_snapshot_id": baseline_snapshot_id,
        "current_snapshot_id": current_snapshot_id,
        "baseline_structured_fingerprint": None,
        "current_structured_fingerprint": None,
        "changed_paths": [],
        "requires_re_evaluation": True,
        "propagation_effect": BLOCK_CARRY_FORWARD,
        "boundary": EVIDENCE_DRIFT_BOUNDARY,
        "authorization_effect": "DOES_NOT_AUTHORIZE_CLOSURE",
    }

def assess_evidence_drift(
    baseline: HAWMSnapshot,
    current: HAWMSnapshot,
) -> dict[str, Any]:
    """Compare CFC-relevant structured HAWM state across two snapshots.

    This host-side layer detects whether a prior closure may be carried forward
    without an additional drift blocker. It never authorizes closure itself.
    """
    if baseline.conversation_id != current.conversation_id:
        return _result(
            status=UNRESOLVED,
            reason="CROSS_CONVERSATION_COMPARISON",
            baseline=baseline,
            current=current,
            baseline_fingerprint=None,
            current_fingerprint=None,
        )

    baseline_state, baseline_error = _structured_state(baseline)
    current_state, current_error = _structured_state(current)

    baseline_fingerprint = (
        _fingerprint(baseline_state) if baseline_error is None else None
    )
    current_fingerprint = (
        _fingerprint(current_state) if current_error is None else None
    )

    if baseline_error is not None or current_error is not None:
        reasons = []
        if baseline_error is not None:
            reasons.append(f"BASELINE_{baseline_error}")
        if current_error is not None:
            reasons.append(f"CURRENT_{current_error}")
        return _result(
            status=UNRESOLVED,
            reason="+".join(reasons),
            baseline=baseline,
            current=current,
            baseline_fingerprint=baseline_fingerprint,
            current_fingerprint=current_fingerprint,
        )

    if (
        baseline.snapshot_id == current.snapshot_id
        and baseline_fingerprint != current_fingerprint
    ):
        return _result(
            status=UNRESOLVED,
            reason="SNAPSHOT_ID_CONTENT_MISMATCH",
            baseline=baseline,
            current=current,
            baseline_fingerprint=baseline_fingerprint,
            current_fingerprint=current_fingerprint,
            changed_paths=_changed_paths(baseline_state, current_state),
        )

    changes = _changed_paths(baseline_state, current_state)
    if changes:
        return _result(
            status=MATERIAL_DRIFT,
            reason="STRUCTURED_EVIDENCE_STATE_CHANGED",
            baseline=baseline,
            current=current,
            baseline_fingerprint=baseline_fingerprint,
            current_fingerprint=current_fingerprint,
            changed_paths=changes,
        )

    return _result(
        status=NO_DRIFT,
        reason=(
            "SAME_SNAPSHOT"
            if baseline.snapshot_id == current.snapshot_id
            else "STRUCTURED_EVIDENCE_STATE_UNCHANGED"
        ),
        baseline=baseline,
        current=current,
        baseline_fingerprint=baseline_fingerprint,
        current_fingerprint=current_fingerprint,
    )
