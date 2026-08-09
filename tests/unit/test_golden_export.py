"""Byte-exact golden test for the full BLK export (M2).

Renders the calibration geometry through the real template and asserts it matches
the committed golden file exactly. This is the regression guard for the entire
header + injection + float-formatting pipeline: if any of it changes, this fails.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.application.export_service import render_sight_text
from scripts.export_demo import calibration_geometry

# A number in scientific notation, e.g. 1e-05 or 2.5E+3 (fatal to the game).
_SCI_RE = re.compile(r"\d\s*[eE][+-]?\d")
# Standalone nan/inf tokens (avoid matching substrings inside header words).
_NONFINITE_RE = re.compile(r"(?<![a-z])(nan|inf|infinity)(?![a-z])", re.IGNORECASE)

GOLDEN = Path(__file__).resolve().parents[1] / "golden" / "calibration.blk"


def test_calibration_export_matches_golden():
    lines, quads = calibration_geometry()
    rendered = render_sight_text(lines, quads)

    # Compare as text with LF newlines (the game's required ending). read_text uses
    # universal newlines, so a CRLF checkout of the golden still compares as LF.
    expected = GOLDEN.read_text(encoding="utf-8")
    assert rendered == expected


def test_golden_has_no_scientific_notation_or_nonfinite():
    content = GOLDEN.read_text(encoding="utf-8")
    assert _SCI_RE.search(content) is None
    assert _NONFINITE_RE.search(content) is None


def test_golden_is_brace_balanced():
    content = GOLDEN.read_text(encoding="utf-8")
    assert content.count("{") == content.count("}")
