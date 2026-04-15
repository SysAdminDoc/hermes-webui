import pathlib
import re


REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
BOOT_JS = (REPO_ROOT / "static" / "boot.js").read_text(encoding="utf-8")
UI_JS = (REPO_ROOT / "static" / "ui.js").read_text(encoding="utf-8")
SESSIONS_JS = (REPO_ROOT / "static" / "sessions.js").read_text(encoding="utf-8")


def test_boot_chat_enter_send_respects_ime_composition():
    assert re.search(
        r"if\(e\.key==='Enter'\)\{\s*if\(e\.isComposing\)\{return;\}",
        BOOT_JS,
    ), "Chat composer Enter handler must ignore IME composition Enter in static/boot.js"
    assert re.search(
        r"if\(e\.key==='Enter'&&!e\.shiftKey\)\{\s*if\(e\.isComposing\)\{return;\}",
        BOOT_JS,
    ), "Command dropdown Enter handler must ignore IME composition Enter in static/boot.js"


def test_ui_enter_submit_paths_respect_ime_composition():
    assert re.search(
        r"document\.addEventListener\('keydown',e=>\{[\s\S]*?if\(e\.key==='Enter'\)\{\s*if\(e\.isComposing\) return;",
        UI_JS,
    ), \
        "App dialog Enter handler must ignore IME composition Enter in static/ui.js"
    assert "if(e.key==='Enter' && !e.shiftKey) { if(e.isComposing) return; e.preventDefault();" in UI_JS, \
        "Message edit Enter-to-save handler must ignore IME composition Enter in static/ui.js"
    assert re.search(
        r"inp\.onkeydown=\(e2\)=>\{\s*if\(e2\.key==='Enter'\)\{\s*if\(e2\.isComposing\)\{return;\}",
        UI_JS,
    ), \
        "Workspace rename Enter handler must ignore IME composition Enter in static/ui.js"


def test_sessions_enter_submit_paths_respect_ime_composition():
    matches = re.findall(
        r"if\(e2?\.key==='Enter'\)\{\s*if\(e2?\.isComposing\)\{return;\}",
        SESSIONS_JS,
    )
    assert len(matches) >= 3, \
        "Session and project rename/create Enter handlers must ignore IME composition Enter in static/sessions.js"
