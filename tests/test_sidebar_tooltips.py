"""Sidebar tooltip contract tests."""
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
SESSIONS_JS_PATH = REPO_ROOT / "static" / "sessions.js"


def _sessions_js() -> str:
    return SESSIONS_JS_PATH.read_text(encoding="utf-8")


def test_session_title_hover_shows_full_title_not_rename_hint():
    """The truncated sidebar title needs a real full-title tooltip.

    The old "Double-click to rename" title hid the only native hover affordance
    that can reveal a long chat title when badges/tags squeeze the row.
    """
    js = _sessions_js()
    assert "Double-click to rename" not in js
    assert "title.title=_sessionFullTitleTooltip(rawTitle,cleanTitle);" in js


def test_sidebar_status_badges_have_explanatory_tooltips():
    """Compact badges/icons must explain what they mean, not repeat the chip text."""
    js = _sessions_js()
    assert "function _sessionFullTitleTooltip" in js
    assert "function _sessionForkTooltip" in js
    assert "function _sessionLineageBadgeTooltip" in js
    assert "function _sessionChildBadgeTooltip" in js
    assert "function _sessionStateTooltip" in js
    assert "branchInd.title=_sessionForkTooltip(parentLabel);" in js
    assert "segmentCountEl.title=_sessionLineageBadgeTooltip(segmentLabel,canExpandLineageSegments);" in js
    assert "childCountEl.title=_sessionChildBadgeTooltip(childLabel);" in js
    assert "state.title=_sessionStateTooltip({isStreaming,hasUnread});" in js
