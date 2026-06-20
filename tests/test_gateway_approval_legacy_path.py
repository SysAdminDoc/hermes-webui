"""Tests for approval event handling on the gateway legacy /v1/chat/completions path (#4549).

The legacy path is the default when HERMES_WEBUI_GATEWAY_USE_RUNS_API is not set.
PR #4495 fixed the runs API path but left the legacy path without approval handling.
"""
from __future__ import annotations

from pathlib import Path

from api.gateway_chat import _gateway_runs_approval_event

REPO_ROOT = Path(__file__).parent.parent
GATEWAY_CHAT_SRC = (REPO_ROOT / "api" / "gateway_chat.py").read_text(encoding="utf-8")

_LEGACY_MARKER = 'url = f"{base_url}/v1/chat/completions"'
_NEXT_FUNC_RE = "\ndef "


def _extract_legacy_sse_loop():
    """Extract the legacy /v1/chat/completions SSE relay function body."""
    start = GATEWAY_CHAT_SRC.find(_LEGACY_MARKER)
    assert start >= 0, "Legacy chat/completions path not found in gateway_chat.py"
    end = GATEWAY_CHAT_SRC.find(_NEXT_FUNC_RE, start)
    if end < 0:
        end = len(GATEWAY_CHAT_SRC)
    return GATEWAY_CHAT_SRC[start:end]


def test_legacy_loop_checks_approval_request_event():
    """Legacy SSE loop must handle `approval.request` events."""
    loop = _extract_legacy_sse_loop()
    assert '"approval.request"' in loop, (
        "Legacy SSE loop must check for approval.request event name"
    )


def test_legacy_loop_checks_hermes_approval_request_event():
    """Legacy SSE loop must handle `hermes.approval.request` events."""
    loop = _extract_legacy_sse_loop()
    assert '"hermes.approval.request"' in loop, (
        "Legacy SSE loop must check for hermes.approval.request event name"
    )


def test_legacy_loop_derives_event_from_payload():
    """Legacy SSE loop must derive event type from JSON payload fields."""
    loop = _extract_legacy_sse_loop()
    assert 'payload.get("event")' in loop or "payload.get('event')" in loop, (
        "Legacy SSE loop must check payload JSON 'event' field"
    )


def test_legacy_loop_calls_put_gateway_event_approval():
    """Legacy SSE loop must relay approval via put_gateway_event('approval', ...)."""
    loop = _extract_legacy_sse_loop()
    assert 'put_gateway_event("approval"' in loop, (
        "Legacy SSE loop must call put_gateway_event with 'approval' event type"
    )


def test_legacy_loop_calls_submit_gateway_pending_mirror():
    """Legacy SSE loop must mirror approval to polling state."""
    loop = _extract_legacy_sse_loop()
    assert "submit_gateway_pending_mirror" in loop, (
        "Legacy SSE loop must call submit_gateway_pending_mirror for polling fallback"
    )


def test_legacy_loop_reuses_gateway_runs_approval_event():
    """Legacy SSE loop must reuse _gateway_runs_approval_event, not duplicate the mapping."""
    loop = _extract_legacy_sse_loop()
    assert "_gateway_runs_approval_event" in loop, (
        "Legacy SSE loop must call _gateway_runs_approval_event to map the payload"
    )


def test_legacy_loop_resets_sse_event_after_approval():
    """Legacy SSE loop must reset sse_event to 'message' after handling approval."""
    loop = _extract_legacy_sse_loop()
    approval_idx = loop.find('"hermes.approval.request"')
    assert approval_idx >= 0
    block_after = loop[approval_idx:approval_idx + 900]
    assert 'sse_event = "message"' in block_after, (
        "Must reset sse_event to 'message' after approval handling to prevent bleed"
    )


def test_approval_event_mapping_complete_payload():
    """_gateway_runs_approval_event correctly maps a full approval payload."""
    result = _gateway_runs_approval_event({
        "command": "rm -rf /tmp/x",
        "description": "Dangerous command approval",
        "pattern_key": "dangerous_command",
        "pattern_keys": ["dangerous_command"],
        "approval_id": "appr-leg-1",
        "choices": ["once", "session", "always", "deny"],
    })
    assert result is not None
    assert result["tool"] == "dangerous_command"
    assert result["command"] == "rm -rf /tmp/x"
    assert result["description"] == "Dangerous command approval"
    assert result["approval_id"] == "appr-leg-1"
    assert result["allow_permanent"] is True
    assert result["risk_level"] == "high"


def test_approval_event_mapping_rejects_empty():
    """Incomplete payload returns None."""
    assert _gateway_runs_approval_event({"risk_level": "high"}) is None
    assert _gateway_runs_approval_event({}) is None
