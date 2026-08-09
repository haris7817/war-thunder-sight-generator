"""Unit tests for the template brace-scan parser/injector (M2)."""

from __future__ import annotations

import pytest
from app.blk.parser import (
    SightTemplate,
    TemplateError,
    find_block_span,
    load_default_template,
    replace_block_body,
)

SIMPLE = "header:b = yes\n\ndrawLines{\n  old line\n}\n\ndrawQuads{\n}\n"


def test_find_block_span_locates_braces():
    open_b, close_b = find_block_span(SIMPLE, "drawLines")
    assert SIMPLE[open_b] == "{"
    assert SIMPLE[close_b] == "}"
    assert "old line" in SIMPLE[open_b:close_b]


def test_find_block_span_missing_raises():
    with pytest.raises(TemplateError):
        find_block_span("nothing here", "drawLines")


def test_replace_block_body_replaces_only_target():
    out = replace_block_body(SIMPLE, "drawLines", "\n  new content\n")
    assert "new content" in out
    assert "old line" not in out
    assert "drawQuads{" in out  # other block untouched


def test_replace_handles_nested_braces():
    text = "drawLines{\n  a { b } c\n}\n"
    out = replace_block_body(text, "drawLines", "\nX\n")
    assert out == "drawLines{\nX\n}\n"


def test_sight_template_render_injects_both_blocks():
    tmpl = SightTemplate(SIMPLE)
    out = tmpl.render("\n  LINE\n", "\n  QUAD\n")
    assert "  LINE" in out
    assert "  QUAD" in out
    assert "old line" not in out


def test_sight_template_requires_both_blocks():
    with pytest.raises(TemplateError):
        SightTemplate("drawLines{\n}\n")  # missing drawQuads


def test_default_template_loads_and_roundtrips():
    tmpl = load_default_template()
    # Empty render should still be a valid, brace-balanced template.
    out = tmpl.render("\n", "\n")
    assert out.count("{") == out.count("}")
    assert "drawLines{" in out
    assert "drawQuads{" in out
    assert "crosshairColor" in out
