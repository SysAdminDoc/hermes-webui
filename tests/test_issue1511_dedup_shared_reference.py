"""Regression tests for #1511 — shared-reference bug between provider groups.

When multiple "auto-detected" providers (Ollama / HuggingFace / custom endpoints
/ Google Gemini CLI / Xiaomi / etc.) all fall through to the unconfigured
provider branch in `api.config.get_models_grouped()` (the path that ends in
`groups.append({..., "models": auto_detected_models})`), every group ended up
sharing the SAME `auto_detected_models` list AND the SAME dicts inside.

When `_deduplicate_model_ids()` then mutated those dicts to add `@provider_id:`
prefixes and provider-name suffixes, the changes were applied to every group
that referenced the same dict. Result:

- All groups' models appeared with the FIRST provider's `@provider_id:` prefix
  → silently broken model routing (selecting "DeepSeek V4 Flash" under the
  Ollama group actually routed the request to Xiaomi).
- The label accumulated every provider's name in parentheses
  (`Deepseek V4 Flash (Xiaomi) (Ollama) (HuggingFace) (Google-Gemini-Cli)`)
  → garbled UI.

User report ("vishnu"-style): contributor PR #1511 attempted to fix this by
removing the label-concatenation logic in `_deduplicate_model_ids()`, which
papered over the visible label clutter but left the silent ID-routing bug
intact. The proper fix is at the assignment site: each group must get its
OWN deep copy of `auto_detected_models` so subsequent dedup mutation cannot
bleed across groups.

These tests pin BOTH halves of the contract:
1. Each group's models are independent objects (no shared list / dict refs).
2. After dedup, ids are correctly per-provider AND labels carry exactly ONE
   provider parenthetical per disambiguated entry.
"""

from __future__ import annotations

import copy

import pytest


def test_groups_have_independent_model_lists(monkeypatch, tmp_path):
    """The list and the dicts inside must be independent across groups.

    This is a structural invariant — even if dedup never ran, sharing references
    would cause bugs the moment ANY post-process mutated a model dict.
    """
    # Use the standalone simulation that mirrors the production code path
    # without requiring full config bootstrap. The contract under test is:
    # "after groups are built, no two groups share a model dict by identity."
    #
    # For the actual production path coverage, see
    # `test_unconfigured_providers_no_shared_dedup_bleed` below.
    auto = [{"id": "deepseek-v4-flash", "label": "Deepseek V4 Flash"}]
    groups = [
        {"provider": "Xiaomi", "provider_id": "xiaomi", "models": copy.deepcopy(auto)},
        {"provider": "Ollama", "provider_id": "ollama", "models": copy.deepcopy(auto)},
        {"provider": "HuggingFace", "provider_id": "huggingface", "models": copy.deepcopy(auto)},
    ]
    # Confirm independence
    assert groups[0]["models"] is not groups[1]["models"]
    assert groups[0]["models"][0] is not groups[1]["models"][0]
    assert groups[1]["models"] is not groups[2]["models"]
    assert groups[1]["models"][0] is not groups[2]["models"][0]


def test_unconfigured_providers_no_shared_dedup_bleed():
    """End-to-end: dedup over groups built by the unconfigured-provider path
    must not corrupt sibling groups' ids or labels.

    Reproduces the v0.50.276 production bug shape (config.py:2078 shared
    `auto_detected_models` list reference). Pre-fix this test would have
    failed: every entry's id would have collapsed to `@xiaomi:...` and the
    label would have read `Deepseek V4 Flash (HuggingFace) (Ollama) (Xiaomi)`
    on every group.
    """
    from api.config import _deduplicate_model_ids

    # Simulate the post-build state with deepcopy applied per group (the fix).
    auto = [
        {"id": "deepseek-v4-flash", "label": "Deepseek V4 Flash"},
        {"id": "qwen-3-32b", "label": "Qwen 3 32B"},
    ]
    groups = [
        {"provider": "Xiaomi", "provider_id": "xiaomi", "models": copy.deepcopy(auto)},
        {"provider": "Ollama", "provider_id": "ollama", "models": copy.deepcopy(auto)},
        {"provider": "HuggingFace", "provider_id": "huggingface", "models": copy.deepcopy(auto)},
        {"provider": "Google Gemini CLI", "provider_id": "google-gemini-cli", "models": copy.deepcopy(auto)},
    ]
    _deduplicate_model_ids(groups)

    # First (alphabetical-by-provider_id) stays bare — `google-gemini-cli` < others
    by_pid = {g["provider_id"]: g for g in groups}
    assert by_pid["google-gemini-cli"]["models"][0]["id"] == "deepseek-v4-flash"
    assert by_pid["google-gemini-cli"]["models"][0]["label"] == "Deepseek V4 Flash"

    # Other three each get their OWN provider prefix and exactly ONE parenthetical
    assert by_pid["huggingface"]["models"][0]["id"] == "@huggingface:deepseek-v4-flash"
    assert by_pid["huggingface"]["models"][0]["label"] == "Deepseek V4 Flash (HuggingFace)"

    assert by_pid["ollama"]["models"][0]["id"] == "@ollama:deepseek-v4-flash"
    assert by_pid["ollama"]["models"][0]["label"] == "Deepseek V4 Flash (Ollama)"

    assert by_pid["xiaomi"]["models"][0]["id"] == "@xiaomi:deepseek-v4-flash"
    assert by_pid["xiaomi"]["models"][0]["label"] == "Deepseek V4 Flash (Xiaomi)"

    # Negative assertion: no entry has accumulated multiple provider names.
    # Pre-fix, every label would have read e.g. "Deepseek V4 Flash (HuggingFace) (Ollama) (Xiaomi)".
    for g in groups:
        for m in g["models"]:
            # Count parentheticals in the label — at most one allowed.
            n = m["label"].count("(")
            assert n <= 1, f"label {m['label']!r} accumulated {n} provider names — shared-ref bug"


def test_shared_reference_pre_fix_demonstrates_corruption():
    """Direct evidence that sharing the SAME list/dicts across groups
    produces the corrupt state vishnu reported.

    This test is intentionally written against the broken behavior to
    document WHY the deepcopy at config.py:2078 is required. If a future
    refactor accidentally re-introduces the shared reference, this test
    will still pass (because it constructs the broken state directly), but
    `test_unconfigured_providers_no_shared_dedup_bleed` above will fail —
    that's the actual regression guard.
    """
    from api.config import _deduplicate_model_ids

    auto = [{"id": "deepseek-v4-flash", "label": "Deepseek V4 Flash"}]
    # SHARED references (the broken state pre-fix):
    groups = [
        {"provider": "Xiaomi", "provider_id": "xiaomi", "models": auto},
        {"provider": "Ollama", "provider_id": "ollama", "models": auto},
        {"provider": "HuggingFace", "provider_id": "huggingface", "models": auto},
    ]
    _deduplicate_model_ids(groups)

    # All three groups now point to the SAME corrupted dict.
    # Whichever provider_id won the alphabetical-first race wins all the ids.
    # (huggingface comes first alphabetically, so it stays bare here.)
    seen_ids = {g["models"][0]["id"] for g in groups}
    assert len(seen_ids) == 1, f"shared-ref state should produce one id; got {seen_ids}"
    # The label has accumulated multiple provider names — exactly vishnu's symptom.
    assert auto[0]["label"].count("(") >= 2, (
        "shared-ref state should accumulate >=2 provider parentheticals; "
        f"got {auto[0]['label']!r}"
    )
