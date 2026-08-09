"""Unit tests for BLK exporter formatting and convexity rules (M2)."""

from __future__ import annotations

import math

import pytest
from app.blk.exporter import (
    build_lines_body,
    build_quads_body,
    format_number,
    is_convex_quad,
    line_to_blk,
    quad_to_blk,
)
from app.domain.geometry import LineSegment, Point, Quad

# --- float formatting ----------------------------------------------------------


def test_format_number_six_decimals():
    assert format_number(0.1) == "0.100000"
    assert format_number(0.1234567) == "0.123457"  # rounded to 6 dp


def test_format_number_normalises_negative_zero():
    assert format_number(-0.0) == "0.000000"
    assert format_number(-0.0000004) == "0.000000"  # rounds to -0 -> normalised


def test_format_number_never_scientific_notation():
    for v in [1e-8, -1e-8, 1e-12, 123456.789, -0.000001]:
        assert "e" not in format_number(v).lower()


def test_format_number_rejects_non_finite():
    for bad in [math.nan, math.inf, -math.inf]:
        with pytest.raises(ValueError):
            format_number(bad)


# --- line syntax ---------------------------------------------------------------


def test_line_to_blk_exact_syntax():
    seg = LineSegment(Point(-0.1, 0.2), Point(0.3, -0.4))
    assert (
        line_to_blk(seg)
        == "  line {line:p4=-0.100000,0.200000,0.300000,-0.400000;move:b=false;}"
    )


def test_line_carries_move_false():
    seg = LineSegment(Point(0, 0), Point(1, 1))
    assert "move:b=false;" in line_to_blk(seg)


# --- quad syntax & convexity ---------------------------------------------------


def test_quad_to_blk_exact_syntax():
    q = Quad(Point(0, 0), Point(0.1, 0), Point(0.1, 0.1), Point(0, 0.1))
    assert (
        quad_to_blk(q)
        == "  quad {tl:p2=0.000000,0.000000;tr:p2=0.100000,0.000000;"
        "br:p2=0.100000,0.100000;bl:p2=0.000000,0.100000;}"
    )


def test_convex_square_is_convex():
    assert is_convex_quad(Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)) is True


def test_triangle_as_degenerate_quad_is_allowed():
    # Duplicating two corners yields a valid triangle.
    assert is_convex_quad(Point(0, 0), Point(1, 0), Point(0, 1), Point(0, 1)) is True


def test_crossed_quad_is_not_convex():
    assert is_convex_quad(Point(0, 0), Point(1, 1), Point(1, 0), Point(0, 1)) is False


def test_quad_to_blk_rejects_non_convex():
    bad = Quad(Point(0, 0), Point(1, 1), Point(1, 0), Point(0, 1))
    with pytest.raises(ValueError):
        quad_to_blk(bad)


# --- block bodies --------------------------------------------------------------


def test_empty_lines_body():
    assert build_lines_body([]) == "\n"


def test_empty_quads_body():
    assert build_quads_body([]) == "\n"


def test_lines_body_wraps_with_newlines():
    body = build_lines_body([LineSegment(Point(0, 0), Point(1, 1))])
    assert body.startswith("\n")
    assert body.endswith("\n")
    assert body.count("line {") == 1
