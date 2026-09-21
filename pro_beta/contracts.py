from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


@dataclass(frozen=True)
class UserAccount:
    """Commercial account identity.

    Authentication is delegated to an external auth provider. Passwords and
    provider API keys do not belong in this record.
    """

    user_id: str
    external_auth_subject: str
    email: str | None = None
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class Workspace:
    workspace_id: str
    user_id: str
    name: str
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class Conversation:
    conversation_id: str
    workspace_id: str
    title: str
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class Message:
    message_id: str
    conversation_id: str
    role: str
    content: str
    authority: str
    cfc_status: str
    mode: str
    provider: str | None = None
    model: str | None = None
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class HAWMSnapshot:
    snapshot_id: str
    conversation_id: str
    state: dict[str, Any]
    last_verified_state: str
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class CFCRun:
    run_id: str
    conversation_id: str
    case_id: str
    controller_anchor: str
    controller_result: dict[str, Any]
    presentation: dict[str, Any]
    replay_matches_reference: bool | None = None
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class AuditReportRecord:
    report_id: str
    conversation_id: str
    cfc_run_id: str | None
    status: str
    artifact_path: str | None = None
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class BenchmarkRun:
    benchmark_run_id: str
    conversation_id: str
    benchmark_version: str
    case_id: str
    benchmark_type: str
    context_boundary: str
    expected_control_state: str
    invariant: str
    mode: str
    status: str
    results: list[dict[str, Any]]
    failed_providers: list[dict[str, Any]]
    authority: str = "MODEL_REPLY_UNCHECKED"
    cfc_status: str = "NOT_CONNECTED_C2"
    automatic_semantic_scoring: bool = False
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class UsageEvent:
    event_id: str
    user_id: str
    event_type: str
    units: int = 1
    created_at: str = field(default_factory=utc_now_iso)


def public_dict(record: Any) -> dict[str, Any]:
    """Return a JSON-safe record and fail if forbidden secret-shaped fields appear."""
    data = asdict(record)
    forbidden = {"api_key", "password", "password_hash", "secret", "token"}
    overlap = forbidden.intersection(data)
    if overlap:
        raise ValueError(f"forbidden persisted fields: {sorted(overlap)}")
    return data
