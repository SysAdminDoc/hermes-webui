"""Static-source assertions for the #4662 profile-switch loading skeletons.

These don't execute JS — they assert the source wiring so the behaviour can't
silently regress:

  * switchToProfile() shows both skeletons up front (clears stale content),
    parallelizes the independent list+workspace refreshes, and restores real
    content on failure so a skeleton never strands.
  * renderSessionListFromCache() clears the skeleton-active flag on real render.
  * style.css defines the skeleton classes, the sheen + fade keyframes, the
    reduced-motion fallback, and dark-mode tokens.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
PANELS = (REPO_ROOT / "static" / "panels.js").read_text(encoding="utf-8")
SESSIONS = (REPO_ROOT / "static" / "sessions.js").read_text(encoding="utf-8")
WORKSPACE = (REPO_ROOT / "static" / "workspace.js").read_text(encoding="utf-8")
CSS = (REPO_ROOT / "static" / "style.css").read_text(encoding="utf-8")


def _switch_body() -> str:
    start = PANELS.index("async function switchToProfile(")
    # grab a generous slice (the function is long); next top-level function after it
    end = PANELS.index("function openProfileCreate(", start)
    return PANELS[start:end]


class TestSwitchWiring:
    def test_shows_session_skeleton_up_front(self):
        body = _switch_body()
        assert "showSessionListSkeleton()" in body
        # ...and before the awaited /api/profile/switch POST, so stale rows clear immediately
        assert body.index("showSessionListSkeleton()") < body.index("/api/profile/switch")

    def test_shows_workspace_skeleton_when_panel_open(self):
        body = _switch_body()
        assert "showWorkspaceTreeSkeleton()" in body
        assert "_workspaceVisibleAtStart" in body

    def test_parallelizes_list_and_workspace_refresh(self):
        body = _switch_body()
        # The non-sessionInProgress branch kicks off both fetches before awaiting.
        assert "const listLoad = renderSessionList();" in body
        assert "loadDir('.')" in body
        assert "await listLoad;" in body

    def test_restores_real_content_on_failure(self):
        body = _switch_body()
        catch = body[body.index("} catch (e) {"):]
        assert "renderSessionListFromCache()" in catch, "failed switch must restore real list"


class TestSessionsWiring:
    def test_skeleton_flag_cleared_on_real_render(self):
        # renderSessionListFromCache clears the skeleton-active flag when it
        # writes real rows (so a strand can't persist).
        idx = SESSIONS.index("function renderSessionListFromCache(")
        body = SESSIONS[idx: idx + 4000]
        assert "_sessionListSkeletonActive=false" in body.replace(" ", "")

    def test_builder_defines_groups_and_function(self):
        assert "const _SESSION_SKELETON_GROUPS" in SESSIONS
        assert "function showSessionListSkeleton(" in SESSIONS


class TestWorkspaceWiring:
    def test_builder_defined(self):
        assert "const _WS_SKELETON_ROWS" in WORKSPACE
        assert "function showWorkspaceTreeSkeleton(" in WORKSPACE


class TestSkeletonCss:
    def test_core_classes_present(self):
        for cls in (".skeleton-list", ".skeleton-row", ".skeleton-bar",
                    ".skeleton-group-label", ".skeleton-tree", ".skeleton-tree-row",
                    ".skeleton-glyph"):
            assert cls in CSS, f"missing skeleton CSS class {cls}"

    def test_sheen_and_fade_keyframes(self):
        assert "@keyframes skeletonSheen" in CSS
        assert "@keyframes skeletonFadeIn" in CSS
        assert "animation:skeletonSheen" in CSS.replace(" ", "")

    def test_reduced_motion_disables_animation(self):
        # There must be a prefers-reduced-motion block that turns the skeleton
        # sheen animation off (accessibility contract).
        compact = CSS.replace(" ", "")
        assert "prefers-reduced-motion" in compact
        # The reduced-motion rule names .skeleton-bar and sets animation:none.
        rm_blocks = [b for b in compact.split("@media(prefers-reduced-motion:reduce){")
                     if ".skeleton-bar" in b[:400]]
        assert rm_blocks, "no reduced-motion block scoping .skeleton-bar"
        assert "animation:none" in rm_blocks[0][:400], "reduced-motion must disable the sheen"

    def test_theme_tokens_defined_for_light_and_dark(self):
        compact = CSS.replace(" ", "")
        assert "--skeleton-base:" in compact
        assert "--skeleton-sheen:" in compact
        assert ":root.dark{--skeleton-base:" in compact
