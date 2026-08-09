"""Unit tests for the export orchestration service (M2)."""

from __future__ import annotations

from app.application.export_service import (
    build_export,
    render_and_write_sight,
    render_sight_text,
)
from app.blk.coordinate_mapper import CoordinateMapper
from app.domain.geometry import LineSegment, Point, Quad
from app.domain.transform import ArtworkTransform

MAPPER = CoordinateMapper(image_width=200, image_height=200)
IDENTITY = ArtworkTransform.identity()


def _seg(x1, y1, x2, y2):
    return LineSegment(Point(x1, y1), Point(x2, y2))


def test_build_export_maps_pixels_and_renders():
    # Centre pixel (100,100) -> sight origin; corner (0,0) -> (-0.5,-0.5).
    segs = [_seg(100, 100, 0, 0)]
    result = build_export(segs, [], MAPPER, IDENTITY)
    assert result.line_count == 1
    assert result.quad_count == 0
    assert "line {line:p4=0.000000,0.000000,-0.500000,-0.500000;move:b=false;}" in result.text
    assert not result.truncated


def test_build_export_warns_above_threshold():
    segs = [_seg(0, 0, 1, 1) for _ in range(10)]
    result = build_export(segs, [], MAPPER, IDENTITY, warn_elements=5, max_elements=1000)
    assert result.warnings
    assert any("warn threshold" in w for w in result.warnings)
    assert not result.truncated


def test_build_export_hard_caps_elements():
    segs = [_seg(0, 0, 1, 1) for _ in range(10)]
    result = build_export(segs, [], MAPPER, IDENTITY, warn_elements=1, max_elements=4)
    assert result.truncated
    assert result.line_count == 4
    assert any("hard cap" in w for w in result.warnings)


def test_render_sight_text_is_valid_blk():
    text = render_sight_text([_seg(0, 0, 0.1, 0.1)], [])
    assert text.count("{") == text.count("}")
    assert "drawLines{" in text and "drawQuads{" in text


def test_render_and_write_sight_round_trips(tmp_path):
    lines = [_seg(0.0, 0.0, 0.1, 0.1)]
    quads = [Quad(Point(0, 0), Point(0.1, 0), Point(0.1, 0.1), Point(0, 0.1))]
    out = tmp_path / "out.blk"
    result, path = render_and_write_sight(lines, quads, out)
    assert path.exists()
    written = path.read_text(encoding="utf-8")
    assert written == result.text
    assert result.line_count == 1
    assert result.quad_count == 1
    # Written file must be LF (game requirement) and brace-balanced.
    assert "\r\n" not in path.read_bytes().decode("utf-8")
    assert written.count("{") == written.count("}")
