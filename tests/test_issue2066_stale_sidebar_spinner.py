"""Regression checks for #2066 stale sidebar spinner state."""

from pathlib import Path


SESSIONS_JS = (Path(__file__).resolve().parent.parent / "static" / "sessions.js").read_text()


def _function_block(name: str, next_name: str) -> str:
    start = SESSIONS_JS.find(f"function {name}")
    assert start != -1, f"{name} not found in sessions.js"
    end = SESSIONS_JS.find(f"function {next_name}", start)
    assert end != -1, f"{next_name} not found after {name}"
    return SESSIONS_JS[start:end]


def test_local_streaming_only_uses_active_session_busy_state():
    block = _function_block("_isSessionLocallyStreaming", "_isSessionEffectivelyStreaming")

    assert "const isActive = S.session && s.session_id === S.session.session_id;" in block
    assert "return isActive && Boolean(S.busy);" in block
    assert "INFLIGHT[s.session_id]" not in block
    assert "INFLIGHT && INFLIGHT[s.session_id]" not in block


def test_cache_render_purges_stale_non_streaming_inflight_entries():
    purge_block = _function_block("_purgeStaleInflightEntries", "_rememberRenderedStreamingState")
    render_block = _function_block("renderSessionListFromCache", "_showProjectPicker")

    assert "const s = _allSessionsById.get(sid);" in purge_block
    assert "if (s && !s.is_streaming)" in purge_block
    assert "delete INFLIGHT[sid];" in purge_block
    assert "clearInflightState(sid);" in purge_block
    assert "_purgeStaleInflightEntries();" in render_block
