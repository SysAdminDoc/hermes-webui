"""Regression tests for the #4449 state-dir contract folded into #4454."""

from __future__ import annotations

import importlib
import os

import api.config as config


def test_config_state_dir_defaults_to_hermes_home_webui(tmp_path):
    hermes_home = tmp_path / ".hermes" / "profiles" / "isolated"
    hermes_home.mkdir(parents=True)

    old_home = os.environ.get("HERMES_HOME")
    old_state_dir = os.environ.get("HERMES_WEBUI_STATE_DIR")
    try:
        os.environ["HERMES_HOME"] = str(hermes_home)
        os.environ.pop("HERMES_WEBUI_STATE_DIR", None)

        reloaded = importlib.reload(config)

        assert reloaded.STATE_DIR == (hermes_home / "webui").resolve()
    finally:
        if old_home is None:
            os.environ.pop("HERMES_HOME", None)
        else:
            os.environ["HERMES_HOME"] = old_home
        if old_state_dir is None:
            os.environ.pop("HERMES_WEBUI_STATE_DIR", None)
        else:
            os.environ["HERMES_WEBUI_STATE_DIR"] = old_state_dir
        importlib.reload(config)


def test_config_state_dir_unchanged_for_normal_install_hermes_home_unset(tmp_path):
    """Backward-compat: with HERMES_HOME unset, STATE_DIR stays at the platform
    default `<~/.hermes>/webui` — a normal install's state must NOT relocate
    (the #4449/#4454 state-dir move only affects an explicitly-set HERMES_HOME)."""
    old_home = os.environ.get("HERMES_HOME")
    old_state_dir = os.environ.get("HERMES_WEBUI_STATE_DIR")
    try:
        os.environ.pop("HERMES_HOME", None)
        os.environ.pop("HERMES_WEBUI_STATE_DIR", None)

        reloaded = importlib.reload(config)

        # _platform_default_hermes_home() drives the default; STATE_DIR must be
        # that base + /webui, exactly as on master before the #4449 change.
        expected = (reloaded._platform_default_hermes_home() / "webui").resolve()
        assert reloaded.STATE_DIR == expected
    finally:
        if old_home is None:
            os.environ.pop("HERMES_HOME", None)
        else:
            os.environ["HERMES_HOME"] = old_home
        if old_state_dir is None:
            os.environ.pop("HERMES_WEBUI_STATE_DIR", None)
        else:
            os.environ["HERMES_WEBUI_STATE_DIR"] = old_state_dir
        importlib.reload(config)


def test_config_state_dir_explicit_override_takes_precedence(tmp_path):
    """HERMES_WEBUI_STATE_DIR always wins over the HERMES_HOME-derived default,
    so an operator who pinned a state dir keeps it even in isolated mode."""
    hermes_home = tmp_path / ".hermes" / "profiles" / "isolated"
    hermes_home.mkdir(parents=True)
    explicit = tmp_path / "custom-state"

    old_home = os.environ.get("HERMES_HOME")
    old_state_dir = os.environ.get("HERMES_WEBUI_STATE_DIR")
    try:
        os.environ["HERMES_HOME"] = str(hermes_home)
        os.environ["HERMES_WEBUI_STATE_DIR"] = str(explicit)

        reloaded = importlib.reload(config)

        assert reloaded.STATE_DIR == explicit.resolve()
    finally:
        if old_home is None:
            os.environ.pop("HERMES_HOME", None)
        else:
            os.environ["HERMES_HOME"] = old_home
        if old_state_dir is None:
            os.environ.pop("HERMES_WEBUI_STATE_DIR", None)
        else:
            os.environ["HERMES_WEBUI_STATE_DIR"] = old_state_dir
        importlib.reload(config)
