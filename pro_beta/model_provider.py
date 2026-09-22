from __future__ import annotations

import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


MODE_LIMITS = {
    "YES_NO": 384,
    "MINIMUM": 768,
    "STANDARD": 2048,
    "EXPANDED": 4096,
}

MODE_INSTRUCTIONS = {
    "YES_NO": (
        "If the user asks a yes/no or proposition-status question, the first "
        "line must be exactly one of: YES, NO, NOT ENOUGH INFORMATION YET. "
        "Do not pretend certainty."
    ),
    "MINIMUM": "Answer briefly and directly.",
    "STANDARD": "Answer clearly and directly at a normal level of detail.",
    "EXPANDED": (
        "Answer in more detail, including relevant limitations and uncertainty."
    ),
}


class ProviderError(RuntimeError):
    pass


def gemini_call(
    *,
    api_key: str,
    model: str,
    text: str,
    mode: str,
    history: list[dict[str, Any]],
    hawm_state: dict[str, Any] | None,
) -> dict[str, Any]:
    key = api_key.strip()
    model_name = model.strip() or "gemini-3.8-flash"
    prompt = text.strip()
    selected_mode = mode.upper()
    if not key:
        raise ProviderError("GEMINI_API_KEY_REQUIRED")
    if not prompt:
        raise ProviderError("TEXT_REQUIRED")
    if selected_mode not in MODE_LIMITS:
        selected_mode = "STANDARD"

    system = (
        "You are the ordinary model reply path inside CFC + HAWM Pro Beta. "
        "Project terminology: CFC means Consistency / Closure Control for LLM "
        "Evaluation, not chlorofluorocarbons. HAWM means Human-AI Work Model. "
        "CFC checks whether current evidence and state justify a definite conclusion "
        "and preserves UNRESOLVED when closure is not justified. "
        "Your natural-language reply is MODEL_REPLY_UNCHECKED and CFC is "
        "NOT_CONNECTED_C2 for this reply. HAWM is working context, not verified "
        "evidence. Do not claim CFC authorization. Do not invent missing evidence. "
        "Reply in the same language as the user unless asked otherwise.\n\n"
        "Latest HAWM working state:\n"
        + json.dumps(hawm_state or {}, ensure_ascii=False)
        + "\n\n"
        + MODE_INSTRUCTIONS[selected_mode]
    )

    contents: list[dict[str, Any]] = []
    for row in history[-20:]:
        role = "model" if row.get("role") == "assistant" else "user"
        contents.append(
            {
                "role": role,
                "parts": [{"text": str(row.get("content") or "")}],
            }
        )
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    body = json.dumps(
        {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": MODE_LIMITS[selected_mode],
            },
        }
    ).encode("utf-8")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + quote(model_name)
        + ":generateContent?key="
        + quote(key)
    )
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    data = None
    for attempt, delay in enumerate((0, 1.5, 4.0)):
        if delay:
            time.sleep(delay)
        try:
            with urlopen(request, timeout=40) as response:
                data = json.loads(response.read().decode("utf-8"))
            break
        except HTTPError as exc:
            code = int(getattr(exc, "code", 0) or 0)
            if code in {500, 502, 503, 504} and attempt < 2:
                continue
            if code == 400:
                raise ProviderError("GEMINI_REQUEST_REJECTED") from exc
            if code in {401, 403}:
                raise ProviderError("GEMINI_API_KEY_REJECTED") from exc
            if code == 429:
                raise ProviderError("GEMINI_RATE_LIMIT") from exc
            raise ProviderError(f"GEMINI_HTTP_{code}") from exc
        except URLError as exc:
            if attempt < 2:
                continue
            raise ProviderError("GEMINI_UNREACHABLE") from exc

    if data is None:
        raise ProviderError("GEMINI_UNAVAILABLE")

    try:
        candidate = data["candidates"][0]
        output = candidate["content"]["parts"][0]["text"].strip()
        finish_reason = str(candidate.get("finishReason") or "")
    except Exception as exc:
        raise ProviderError("GEMINI_EMPTY_RESPONSE") from exc

    if not output:
        raise ProviderError("GEMINI_EMPTY_RESPONSE")

    return {
        "text": output,
        "finish_reason": finish_reason,
        "truncated": finish_reason == "MAX_TOKENS",
        "provider": "gemini",
        "model": model_name,
        "mode": selected_mode,
        "authority": "MODEL_REPLY_UNCHECKED",
        "cfc_status": "NOT_CONNECTED_C2",
    }



def claude_call(
    *,
    api_key: str,
    model: str,
    text: str,
    mode: str,
    history: list[dict[str, Any]],
    hawm_state: dict[str, Any] | None,
) -> dict[str, Any]:
    key = api_key.strip()
    model_name = model.strip() or "claude-sonnet-4-5"
    prompt = text.strip()
    selected_mode = mode.upper()
    if not key:
        raise ProviderError("CLAUDE_API_KEY_REQUIRED")
    if not prompt:
        raise ProviderError("TEXT_REQUIRED")
    if selected_mode not in MODE_LIMITS:
        selected_mode = "STANDARD"

    system = (
        "You are the ordinary model reply path inside CFC + HAWM Pro Beta. "
        "Project terminology: CFC means Consistency / Closure Control for LLM "
        "Evaluation, not chlorofluorocarbons. HAWM means Human-AI Work Model. "
        "CFC checks whether current evidence and state justify a definite conclusion "
        "and preserves UNRESOLVED when closure is not justified. "
        "Your natural-language reply is MODEL_REPLY_UNCHECKED and CFC is "
        "NOT_CONNECTED_C2 for this reply. HAWM is working context, not verified "
        "evidence. Do not claim CFC authorization. Do not invent missing evidence. "
        "Reply in the same language as the user unless asked otherwise.\n\n"
        "Latest HAWM working state:\n"
        + json.dumps(hawm_state or {}, ensure_ascii=False)
        + "\n\n"
        + MODE_INSTRUCTIONS[selected_mode]
    )

    messages: list[dict[str, Any]] = []
    for row in history[-20:]:
        role = "assistant" if row.get("role") == "assistant" else "user"
        messages.append(
            {
                "role": role,
                "content": str(row.get("content") or ""),
            }
        )
    messages.append({"role": "user", "content": prompt})

    body = json.dumps(
        {
            "model": model_name,
            "max_tokens": MODE_LIMITS[selected_mode],
            "system": system,
            "messages": messages,
        }
    ).encode("utf-8")

    request = Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    data = None
    for attempt, delay in enumerate((0, 1.5, 4.0)):
        if delay:
            time.sleep(delay)
        try:
            with urlopen(request, timeout=40) as response:
                data = json.loads(response.read().decode("utf-8"))
            break
        except HTTPError as exc:
            code = int(getattr(exc, "code", 0) or 0)
            if code in {500, 502, 503, 504} and attempt < 2:
                continue
            if code == 400:
                raise ProviderError("CLAUDE_REQUEST_REJECTED") from exc
            if code in {401, 403}:
                raise ProviderError("CLAUDE_API_KEY_REJECTED") from exc
            if code == 429:
                raise ProviderError("CLAUDE_RATE_LIMIT") from exc
            raise ProviderError(f"CLAUDE_HTTP_{code}") from exc
        except URLError as exc:
            if attempt < 2:
                continue
            raise ProviderError("CLAUDE_UNREACHABLE") from exc

    if data is None:
        raise ProviderError("CLAUDE_UNAVAILABLE")

    try:
        blocks = data.get("content") or []
        output = "\n".join(
            str(block.get("text") or "")
            for block in blocks
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip()
        finish_reason = str(data.get("stop_reason") or "")
    except Exception as exc:
        raise ProviderError("CLAUDE_EMPTY_RESPONSE") from exc

    if not output:
        raise ProviderError("CLAUDE_EMPTY_RESPONSE")

    return {
        "text": output,
        "finish_reason": finish_reason,
        "truncated": finish_reason == "max_tokens",
        "provider": "claude",
        "model": model_name,
        "mode": selected_mode,
        "authority": "MODEL_REPLY_UNCHECKED",
        "cfc_status": "NOT_CONNECTED_C2",
    }



def openai_call(
    *,
    api_key: str,
    model: str,
    text: str,
    mode: str,
    history: list[dict[str, Any]],
    hawm_state: dict[str, Any] | None,
) -> dict[str, Any]:
    key = api_key.strip()
    model_name = model.strip() or "gpt-5.6-terra"
    prompt = text.strip()
    selected_mode = mode.upper()
    if not key:
        raise ProviderError("OPENAI_API_KEY_REQUIRED")
    if not prompt:
        raise ProviderError("TEXT_REQUIRED")
    if selected_mode not in MODE_LIMITS:
        selected_mode = "STANDARD"

    system = (
        "You are the ordinary model reply path inside CFC + HAWM Pro Beta. "
        "Project terminology: CFC means Consistency / Closure Control for LLM "
        "Evaluation, not chlorofluorocarbons. HAWM means Human-AI Work Model. "
        "CFC checks whether current evidence and state justify a definite conclusion "
        "and preserves UNRESOLVED when closure is not justified. "
        "Your natural-language reply is MODEL_REPLY_UNCHECKED and CFC is "
        "NOT_CONNECTED_C2 for this reply. HAWM is working context, not verified "
        "evidence. Do not claim CFC authorization. Do not invent missing evidence. "
        "Reply in the same language as the user unless asked otherwise.\n\n"
        "Latest HAWM working state:\n"
        + json.dumps(hawm_state or {}, ensure_ascii=False)
        + "\n\n"
        + MODE_INSTRUCTIONS[selected_mode]
    )

    messages: list[dict[str, Any]] = []
    for row in history[-20:]:
        role = "assistant" if row.get("role") == "assistant" else "user"
        messages.append(
            {
                "role": role,
                "content": str(row.get("content") or ""),
            }
        )
    messages.append({"role": "user", "content": prompt})

    body = json.dumps(
        {
            "model": model_name,
            "instructions": system,
            "input": messages,
            "max_output_tokens": MODE_LIMITS[selected_mode],
        }
    ).encode("utf-8")

    request = Request(
        "https://api.openai.com/v1/responses",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + key,
        },
        method="POST",
    )

    data = None
    for attempt, delay in enumerate((0, 1.5, 4.0)):
        if delay:
            time.sleep(delay)
        try:
            with urlopen(request, timeout=40) as response:
                data = json.loads(response.read().decode("utf-8"))
            break
        except HTTPError as exc:
            code = int(getattr(exc, "code", 0) or 0)
            if code in {500, 502, 503, 504} and attempt < 2:
                continue
            if code == 400:
                raise ProviderError("OPENAI_REQUEST_REJECTED") from exc
            if code in {401, 403}:
                raise ProviderError("OPENAI_API_KEY_REJECTED") from exc
            if code == 429:
                raise ProviderError("OPENAI_RATE_LIMIT") from exc
            raise ProviderError(f"OPENAI_HTTP_{code}") from exc
        except URLError as exc:
            if attempt < 2:
                continue
            raise ProviderError("OPENAI_UNREACHABLE") from exc

    if data is None:
        raise ProviderError("OPENAI_UNAVAILABLE")

    try:
        output_parts: list[str] = []
        for item in data.get("output") or []:
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            for part in item.get("content") or []:
                if isinstance(part, dict) and part.get("type") == "output_text":
                    output_parts.append(str(part.get("text") or ""))
        output = "\n".join(output_parts).strip()
        status = str(data.get("status") or "")
        incomplete_reason = str(
            ((data.get("incomplete_details") or {}).get("reason")) or ""
        )
        finish_reason = incomplete_reason or status
    except Exception as exc:
        raise ProviderError("OPENAI_EMPTY_RESPONSE") from exc

    if not output:
        raise ProviderError("OPENAI_EMPTY_RESPONSE")

    return {
        "text": output,
        "finish_reason": finish_reason,
        "truncated": incomplete_reason == "max_output_tokens",
        "provider": "openai",
        "model": model_name,
        "mode": selected_mode,
        "authority": "MODEL_REPLY_UNCHECKED",
        "cfc_status": "NOT_CONNECTED_C2",
    }
