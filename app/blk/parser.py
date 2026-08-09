"""Minimal, injection-only handling of a War Thunder sight template.

This is deliberately NOT a general Gaijin BLK parser (that is a multi-day scope
trap worth nothing to the MVP). All we need is to locate the top-level
``drawLines{ ... }`` and ``drawQuads{ ... }`` blocks by a brace-depth scan and
replace their bodies with generated geometry, leaving the rest of the header
byte-for-byte untouched.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.infrastructure.filesystem import resource_path

DRAW_LINES = "drawLines"
DRAW_QUADS = "drawQuads"


class TemplateError(ValueError):
    """Raised when the template is missing a required injection block."""


def find_block_span(text: str, keyword: str) -> tuple[int, int]:
    """Locate the top-level ``keyword{ ... }`` block via a brace-depth scan.

    Returns ``(open_brace_index, close_brace_index)`` where both indices point at
    the literal ``{`` and matching ``}`` characters. Raises :class:`TemplateError`
    if the block or its braces are absent/unbalanced.
    """
    kw = text.find(keyword)
    if kw == -1:
        raise TemplateError(f"template missing '{keyword}' block")
    open_brace = text.find("{", kw)
    if open_brace == -1:
        raise TemplateError(f"'{keyword}' has no opening brace")
    depth = 0
    for i in range(open_brace, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return open_brace, i
    raise TemplateError(f"'{keyword}' block is unbalanced (no closing brace)")


def replace_block_body(text: str, keyword: str, new_body: str) -> str:
    """Replace the content between ``keyword{`` and its matching ``}``.

    ``new_body`` is inserted verbatim between the braces — the caller (exporter)
    owns all formatting, indentation, and newlines.
    """
    open_brace, close_brace = find_block_span(text, keyword)
    return text[: open_brace + 1] + new_body + text[close_brace:]


@dataclass(frozen=True, slots=True)
class SightTemplate:
    """A loaded sight template with injectable drawLines/drawQuads blocks."""

    text: str

    def __post_init__(self) -> None:
        # Fail fast if the template lacks either injection point.
        find_block_span(self.text, DRAW_LINES)
        find_block_span(self.text, DRAW_QUADS)

    def render(self, lines_body: str, quads_body: str) -> str:
        """Return the full .blk text with both draw blocks' bodies replaced.

        Replaces drawQuads first, then drawLines, so the earlier block's edit does
        not invalidate the later block's indices.
        """
        out = replace_block_body(self.text, DRAW_QUADS, quads_body)
        out = replace_block_body(out, DRAW_LINES, lines_body)
        return out


def load_default_template() -> SightTemplate:
    """Load the bundled ``app/blk/template.blk`` (source and frozen-safe)."""
    path = resource_path("app", "blk", "template.blk")
    return SightTemplate(path.read_text(encoding="utf-8"))
