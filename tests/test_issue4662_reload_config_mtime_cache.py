"""Phase 2 (#4662): reload_config() must not re-run yaml.safe_load on the hot path
when config.yaml is unchanged. It now routes its parse through the mtime-keyed
_load_yaml_config_file cache (#4652). Behavior-preserving: the process-global
_cfg_cache is still pinned to the unscoped process-env expansion (#798 TLS), env
expansion still runs per call, and an mtime change still busts the cache.
"""
import os
import time

import yaml as _yaml


def test_reload_config_uses_mtime_cache(tmp_path, monkeypatch):
    import api.config as cfg

    config_path = tmp_path / "config.yaml"
    config_path.write_text("providers:\n  openai:\n    models: [gpt-5.5]\n", encoding="utf-8")
    monkeypatch.setattr(cfg, "_get_config_path", lambda: config_path)

    parse_calls = {"n": 0}
    real_safe_load = _yaml.safe_load

    def _counting_safe_load(s):
        parse_calls["n"] += 1
        return real_safe_load(s)

    monkeypatch.setattr(_yaml, "safe_load", _counting_safe_load)
    # Clear the shared file cache so the first reload is a genuine miss.
    with cfg._yaml_file_cache_lock:
        cfg._yaml_file_cache.clear()

    cfg.reload_config()
    first = parse_calls["n"]
    cfg.reload_config()          # same file, unchanged mtime -> must hit cache
    second = parse_calls["n"]

    assert first >= 1, "first reload should parse the file at least once"
    assert second == first, f"unchanged config.yaml was reparsed (parse went {first}->{second})"


def test_reload_config_busts_on_mtime_change(tmp_path, monkeypatch):
    import api.config as cfg

    config_path = tmp_path / "config.yaml"
    config_path.write_text("providers: {}\n", encoding="utf-8")
    monkeypatch.setattr(cfg, "_get_config_path", lambda: config_path)
    with cfg._yaml_file_cache_lock:
        cfg._yaml_file_cache.clear()

    cfg.reload_config()
    assert (cfg.get_config().get("providers") or {}) == {}

    # Edit + bump mtime; the next reload must pick up the change, not the cache.
    time.sleep(0.01)
    config_path.write_text("providers:\n  openai: {}\n", encoding="utf-8")
    os.utime(config_path, None)
    cfg.reload_config()
    assert "openai" in (cfg.get_config().get("providers") or {}), "mtime change not picked up"


def test_reload_config_expands_env_vars(tmp_path, monkeypatch):
    """The pinned process-env expansion must still run: a ${VAR} in config.yaml
    resolves against os.environ after reload_config (the #798 invariant)."""
    import api.config as cfg

    monkeypatch.setenv("HERMES_TEST_RELOAD_TOKEN", "expanded-value-xyz")
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "providers:\n  openai:\n    api_key: ${HERMES_TEST_RELOAD_TOKEN}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(cfg, "_get_config_path", lambda: config_path)
    with cfg._yaml_file_cache_lock:
        cfg._yaml_file_cache.clear()

    cfg.reload_config()
    key = ((cfg.get_config().get("providers") or {}).get("openai") or {}).get("api_key")
    assert key == "expanded-value-xyz", f"env var not expanded after reload: {key!r}"


def test_reload_config_empty_dict_config_does_not_spin(tmp_path, monkeypatch):
    """An empty ``{}`` config must still stamp _cfg_mtime, or get_config()'s
    `current_mtime != _cfg_mtime` stale check fires forever and re-enters
    reload_config() under _cfg_lock on every call. The cache-update is correctly
    skipped for {} (no-op), but the mtime stamp must not be. (Opus gate finding —
    a {} config is reachable on the profile-switch hot path via a freshly
    created/reset profile, and this also fixes the pre-existing empty/None-config
    spin on master.)
    """
    import api.config as cfg

    config_path = tmp_path / "config.yaml"
    config_path.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(cfg, "_get_config_path", lambda: config_path)
    with cfg._yaml_file_cache_lock:
        cfg._yaml_file_cache.clear()

    cfg.reload_config()
    # _cfg_mtime must equal the file's real mtime, not 0.0.
    assert cfg._cfg_mtime == config_path.stat().st_mtime, (
        f"_cfg_mtime not stamped for empty-dict config (got {cfg._cfg_mtime!r}); "
        "get_config() would spin reload_config() forever"
    )

    # And get_config() must NOT re-enter reload_config() on subsequent calls.
    reloads = {"n": 0}
    real_reload = cfg.reload_config

    def _counting_reload():
        reloads["n"] += 1
        return real_reload()

    monkeypatch.setattr(cfg, "reload_config", _counting_reload)
    cfg.get_config()
    cfg.get_config()
    cfg.get_config()
    assert reloads["n"] == 0, f"get_config() re-entered reload_config() {reloads['n']}x on a stable {{}} config (spin)"

