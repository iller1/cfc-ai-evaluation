"""Host-side attestation lifecycle guard for CFC integration experiments.

This module is NOT part of frozen CFC Anchor 0.2.90rc1 and does not modify it.
Passing this guard means ELIGIBLE_FOR_ANCHOR, not ALLOW.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Mapping, MutableSet, Sequence

ELIGIBLE = "ELIGIBLE_FOR_ANCHOR"
STOP = "STOP"
UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class GuardResult:
    status: str
    reason: str
    attestation_ids: tuple[str, ...] = ()
    nonces_to_consume: tuple[str, ...] = ()


def _dt(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _required_text(record: Mapping[str, Any], key: str) -> str | None:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def validate_attestation(
    attestation: Mapping[str, Any],
    context: Mapping[str, Any],
    *,
    consumed_nonces: Iterable[str] = (),
    compromised_roots: Iterable[str] = (),
) -> GuardResult:
    """Validate one attestation for current host-side eligibility."""

    att_id = _required_text(attestation, "attestation_id")
    if att_id is None:
        return GuardResult(UNRESOLVED, "missing attestation_id")

    issued_at = _dt(attestation.get("issued_at"))
    valid_from = _dt(attestation.get("valid_from"))
    valid_to = _dt(attestation.get("valid_to"))
    decision_time = _dt(context.get("decision_time"))
    if None in (issued_at, valid_from, valid_to, decision_time):
        return GuardResult(UNRESOLVED, "missing or invalid timezone-aware temporal field", (att_id,))

    assert issued_at is not None and valid_from is not None and valid_to is not None and decision_time is not None

    if valid_from > valid_to:
        return GuardResult(STOP, "invalid validity interval", (att_id,))
    if decision_time < valid_from:
        return GuardResult(STOP, "attestation not yet valid at decision_time", (att_id,))
    if decision_time > valid_to:
        return GuardResult(STOP, "attestation expired before decision_time", (att_id,))

    ttl_seconds = attestation.get("ttl_seconds")
    if ttl_seconds is not None:
        if not isinstance(ttl_seconds, int) or ttl_seconds < 0:
            return GuardResult(UNRESOLVED, "invalid ttl_seconds", (att_id,))
        if decision_time > issued_at + timedelta(seconds=ttl_seconds):
            return GuardResult(STOP, "attestation TTL expired before decision_time", (att_id,))

    for field in ("scope_id", "purpose_id", "resource_id", "audience_id"):
        expected = _required_text(context, field)
        actual = _required_text(attestation, field)
        if expected is None:
            return GuardResult(UNRESOLVED, f"decision context missing {field}", (att_id,))
        if actual is None:
            return GuardResult(UNRESOLVED, f"attestation missing {field}", (att_id,))
        if actual != expected:
            return GuardResult(STOP, f"{field} mismatch", (att_id,))

    authenticity = _required_text(attestation, "authenticity_status")
    if authenticity is None or authenticity == "unknown":
        return GuardResult(UNRESOLVED, "attestation authenticity unresolved", (att_id,))
    if authenticity != "verified":
        return GuardResult(STOP, "attestation authenticity invalid", (att_id,))

    issuer_id = _required_text(attestation, "issuer_id")
    trusted_issuers = context.get("trusted_issuers")
    if issuer_id is None:
        return GuardResult(UNRESOLVED, "missing issuer_id", (att_id,))
    if not isinstance(trusted_issuers, (set, frozenset, list, tuple)):
        return GuardResult(UNRESOLVED, "trusted issuer set unavailable", (att_id,))
    if issuer_id not in set(trusted_issuers):
        return GuardResult(STOP, "issuer is outside configured trust set", (att_id,))

    revocation_status = _required_text(attestation, "revocation_status")
    if revocation_status is None or revocation_status == "unknown":
        return GuardResult(UNRESOLVED, "revocation status unresolved", (att_id,))
    if revocation_status == "revoked":
        return GuardResult(STOP, "attestation revoked", (att_id,))
    if revocation_status != "good":
        return GuardResult(UNRESOLVED, "unrecognized revocation status", (att_id,))

    revocation_checked_at = _dt(attestation.get("revocation_checked_at"))
    max_age = context.get("max_revocation_age_seconds")
    if revocation_checked_at is None:
        return GuardResult(UNRESOLVED, "missing revocation_checked_at", (att_id,))
    if revocation_checked_at > decision_time:
        return GuardResult(STOP, "revocation check is from the future relative to decision_time", (att_id,))
    if not isinstance(max_age, int) or max_age < 0:
        return GuardResult(UNRESOLVED, "invalid max_revocation_age_seconds", (att_id,))
    if decision_time - revocation_checked_at > timedelta(seconds=max_age):
        return GuardResult(UNRESOLVED, "revocation status too stale for current decision", (att_id,))

    root_id = _required_text(attestation, "root_id")
    if root_id is None:
        return GuardResult(UNRESOLVED, "root-of-trust binding unresolved", (att_id,))
    if root_id in set(compromised_roots):
        return GuardResult(STOP, "attestation depends on a known compromised root", (att_id,))

    failure_domain_id = _required_text(attestation, "failure_domain_id")
    if failure_domain_id is None:
        return GuardResult(UNRESOLVED, "source failure domain unresolved", (att_id,))

    decision_id = _required_text(context, "decision_id")
    bound_decision_id = _required_text(attestation, "decision_id")
    if decision_id is not None and bound_decision_id == decision_id:
        return GuardResult(ELIGIBLE, "decision-bound attestation is current and eligible", (att_id,))

    session_id = _required_text(context, "session_id")
    bound_session_id = _required_text(attestation, "session_id")
    nonce = _required_text(attestation, "nonce")
    if session_id is None:
        return GuardResult(UNRESOLVED, "decision_id binding absent and current session_id unavailable", (att_id,))
    if bound_session_id is None or bound_session_id != session_id:
        return GuardResult(STOP, "anti-replay session binding mismatch", (att_id,))
    if nonce is None:
        return GuardResult(UNRESOLVED, "anti-replay nonce unavailable", (att_id,))
    if nonce in set(consumed_nonces):
        return GuardResult(STOP, "replayed attestation nonce", (att_id,))

    return GuardResult(
        ELIGIBLE,
        "session-bound attestation is current and eligible; nonce must be consumed atomically",
        (att_id,),
        (nonce,),
    )


def validate_independence_set(
    attestations: Sequence[Mapping[str, Any]],
    context: Mapping[str, Any],
    *,
    consumed_nonces: Iterable[str] = (),
    compromised_roots: Iterable[str] = (),
    required_independent_supports: int = 2,
) -> GuardResult:
    """Validate a set without equating record count with independence."""

    if required_independent_supports < 1:
        return GuardResult(UNRESOLVED, "invalid required_independent_supports")
    if len(attestations) < required_independent_supports:
        return GuardResult(UNRESOLVED, "insufficient attestation count for required independence")

    roots: list[str] = []
    domains: list[str] = []
    ids: list[str] = []
    nonces: list[str] = []

    for attestation in attestations:
        result = validate_attestation(
            attestation,
            context,
            consumed_nonces=consumed_nonces,
            compromised_roots=compromised_roots,
        )
        if result.status != ELIGIBLE:
            return result

        att_id = _required_text(attestation, "attestation_id")
        root_id = _required_text(attestation, "root_id")
        domain_id = _required_text(attestation, "failure_domain_id")
        if att_id is None or root_id is None or domain_id is None:
            return GuardResult(UNRESOLVED, "identity/root/failure-domain resolution incomplete")
        ids.append(att_id)
        roots.append(root_id)
        domains.append(domain_id)
        nonces.extend(result.nonces_to_consume)

    if len(set(domains)) != len(domains):
        return GuardResult(STOP, "attestations share a source failure domain and are not independent", tuple(ids))
    if len(set(roots)) != len(roots):
        return GuardResult(STOP, "attestations share a root of trust and are not independent", tuple(ids))

    if len(set(domains)) < required_independent_supports or len(set(roots)) < required_independent_supports:
        return GuardResult(UNRESOLVED, "independence requirement not established", tuple(ids))

    return GuardResult(
        ELIGIBLE,
        "attestation set is current, bound, and independently rooted for host-side eligibility",
        tuple(ids),
        tuple(nonces),
    )


def commit_nonce_consumption(result: GuardResult, consumed_nonces: MutableSet[str]) -> None:
    """Commit anti-replay state only after the host commits the decision atomically."""

    if result.status != ELIGIBLE:
        raise ValueError("cannot consume nonces for a non-eligible result")
    for nonce in result.nonces_to_consume:
        if nonce in consumed_nonces:
            raise ValueError(f"nonce already consumed: {nonce}")
    consumed_nonces.update(result.nonces_to_consume)


def apply_revalidation_result(result: GuardResult, cached_eligible_attestations: MutableSet[str]) -> None:
    """Update host-side cached eligibility after revalidation.

    A negative or unresolved revalidation removes the affected attestation IDs.
    This cache is host integration state; it is not Anchor state.
    """

    if result.status == ELIGIBLE:
        cached_eligible_attestations.update(result.attestation_ids)
        return
    cached_eligible_attestations.difference_update(result.attestation_ids)
