from __future__ import annotations

from dataclasses import asdict
from typing import Any

from pro_beta.contracts import CFCRun, Conversation, HAWMSnapshot


REPORT_VERSION = "HAWM_CFC_AUDIT_REPORT_V1"


def build_audit_document(
    *,
    conversation: Conversation,
    hawm_snapshot: HAWMSnapshot | None,
    cfc_run: CFCRun | None,
) -> dict[str, Any]:
    """Build an auditable export without reinterpreting HAWM or CFC output."""
    return {
        "report_version": REPORT_VERSION,
        "conversation": asdict(conversation),
        "boundaries": {
            "ordinary_model_reply": "MODEL_REPLY_UNCHECKED",
            "ordinary_model_cfc": "NOT_CONNECTED_C2",
            "hawm": "USER_WORKING_STATE_NOT_EVIDENCE_VERIFICATION",
            "cfc_bridge": (
                "STRUCTURED_HAWM_FIELDS_ONLY_NO_NATURAL_LANGUAGE_INFERENCE"
                if cfc_run is not None and cfc_run.case_id == "HAWM_STRUCTURED_CUSTOM"
                else "SEPARATE_CFC_RUN"
            ),
        },
        "hawm_snapshot": asdict(hawm_snapshot) if hawm_snapshot else None,
        "cfc_run": asdict(cfc_run) if cfc_run else None,
    }


def render_markdown(document: dict[str, Any]) -> str:
    conversation = document["conversation"]
    hawm = document.get("hawm_snapshot")
    cfc = document.get("cfc_run")
    boundaries = document["boundaries"]

    lines = [
        "# CFC + HAWM Audit Report",
        "",
        f"Report version: {document['report_version']}",
        f"Conversation: {conversation['title']}",
        f"Conversation ID: {conversation['conversation_id']}",
        "",
        "## Boundaries",
        "",
        f"- Ordinary model reply: {boundaries['ordinary_model_reply']}",
        f"- Ordinary model CFC status: {boundaries['ordinary_model_cfc']}",
        f"- HAWM state: {boundaries['hawm']}",
        f"- CFC bridge: {boundaries['cfc_bridge']}",
        "",
        "## Latest HAWM snapshot",
        "",
    ]

    if hawm is None:
        lines.append("No HAWM snapshot saved.")
    else:
        lines.extend(
            [
                f"Snapshot ID: {hawm['snapshot_id']}",
                f"Created: {hawm['created_at']}",
                f"State label: {hawm['last_verified_state']}",
                "",
                "~~~json",
                _json_pretty(hawm["state"]),
                "~~~",
            ]
        )

    lines.extend(["", "## Latest CFC run", ""])
    if cfc is None:
        lines.append("No CFC run saved.")
    else:
        presentation = cfc.get("presentation") or {}
        lines.extend(
            [
                f"Run ID: {cfc['run_id']}",
                f"Case: {cfc['case_id']}",
                f"Controller anchor: {cfc['controller_anchor']}",
                f"Created: {cfc['created_at']}",
                f"Claim state: {presentation.get('claim_state', 'NONE')}",
                f"Decision: {presentation.get('decision', 'UNKNOWN')}",
                f"Reason: {presentation.get('reason', '')}",
                f"Replay matches reference: {cfc.get('replay_matches_reference')}",
                "",
                "### Presentation",
                "",
                "~~~json",
                _json_pretty(presentation),
                "~~~",
                "",
                "### Raw frozen-controller result",
                "",
                "~~~json",
                _json_pretty(cfc.get("controller_result") or {}),
                "~~~",
            ]
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "This export records persisted state and CFC output. It does not turn free-text HAWM content or ordinary model replies into CFC-verified evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def _json_pretty(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
