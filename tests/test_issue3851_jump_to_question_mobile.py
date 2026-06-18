"""Regression test for issue #3851: mobile jump-to-question visibility.

Ensures that .msg-question-jump-btn remains visible on mobile screens
instead of being completely hidden with display: none.
"""
import re
import pytest


def test_msg_question_jump_btn_mobile_not_display_none():
    """Assert the mobile media query for .msg-question-jump-btn does NOT hide it."""
    css_path = 'static/style.css'

    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # Find the mobile media query that contains .msg-question-jump-btn
    # Pattern: @media (max-width: 600px) { ... .msg-question-jump-btn ... }
    mobile_pattern = r'@media\s*\([^)]*max-width\s*:\s*600px[^)]*\)\s*\{[^}]*\.msg-question-jump-btn[^}]*\}'
    mobile_match = re.search(mobile_pattern, css_content, re.DOTALL)

    assert mobile_match is not None, (
        "No mobile media query found for .msg-question-jump-btn"
    )

    mobile_rule = mobile_match.group(0)

    # Check that it does NOT contain display: none or display:none
    assert 'display: none' not in mobile_rule and 'display:none' not in mobile_rule, (
        f"Mobile rule for .msg-question-jump-btn should not have display: none. "
        f"Found: {mobile_rule}"
    )


def test_msg_question_jump_btn_mobile_has_visible_styling():
    """Assert the mobile media query provides visible styling for the button."""
    css_path = 'static/style.css'

    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # Find the mobile media query that contains .msg-question-jump-btn
    mobile_pattern = r'@media\s*\([^)]*max-width\s*:\s*600px[^)]*\)\s*\{[^}]*\.msg-question-jump-btn[^}]*\}'
    mobile_match = re.search(mobile_pattern, css_content, re.DOTALL)

    assert mobile_match is not None, (
        "No mobile media query found for .msg-question-jump-btn"
    )

    mobile_rule = mobile_match.group(0)

    # Check that it has some styling (padding, gap, or other properties)
    # but specifically that it's not just setting display: none
    has_padding = 'padding' in mobile_rule
    has_gap = 'gap' in mobile_rule
    has_height = 'height' in mobile_rule
    has_width = 'width' in mobile_rule
    has_some_property = has_padding or has_gap or has_height or has_width

    assert has_some_property, (
        f"Mobile rule for .msg-question-jump-btn should have visible styling "
        f"(padding, gap, height, or width). Found: {mobile_rule}"
    )


def test_msg_question_jump_btn_text_span_hidden_on_mobile():
    """Assert that the text span (second child) is hidden on mobile."""
    css_path = 'static/style.css'

    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # Find the mobile media query that hides the text span inside .msg-question-jump-btn
    # Look for the pattern: span:last-child { display: none; }
    span_hide_pattern = r'\.msg-question-jump-btn\s+span:last-child\s*\{\s*display\s*:\s*none\s*;\s*\}'
    span_hide_match = re.search(span_hide_pattern, css_content, re.DOTALL)

    assert span_hide_match is not None, (
        "Missing span:last-child { display: none; } rule for .msg-question-jump-btn. "
        "The mobile media query should hide the text span while keeping the button visible."
    )
