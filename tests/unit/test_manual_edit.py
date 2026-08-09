"""Tests for manual draw/erase, undo, and the re-trace invariant (M7)."""

from __future__ import annotations

import pytest
from app.application.editing_service import SessionStore
from app.domain.geometry import GeometrySource, LineSegment, Point, Quad
from app.utils.math_utils import point_segment_distance

# --- point-to-segment distance -------------------------------------------------


def test_point_segment_distance_perpendicular():
    assert point_segment_distance(5, 5, 0, 0, 10, 0) == pytest.approx(5.0)


def test_point_segment_distance_beyond_endpoint():
    assert point_segment_distance(-3, 0, 0, 0, 10, 0) == pytest.approx(3.0)


def test_point_segment_distance_degenerate():
    assert point_segment_distance(3, 4, 0, 0, 0, 0) == pytest.approx(5.0)


# --- manual draw + undo --------------------------------------------------------


def test_add_segment_is_manual_and_undoable(qtbot):
    store = SessionStore()
    store.add_segment(Point(0, 0), Point(10, 10))
    assert len(store.lines) == 1
    assert store.lines[0].source is GeometrySource.MANUAL
    store.undo()
    assert len(store.lines) == 0


def test_erase_removes_nearby_and_undo_restores(qtbot):
    store = SessionStore()
    store.set_geometry((LineSegment(Point(0, 0), Point(10, 0)),), ())
    removed = store.erase_near(5, 0, 2.0)  # on the line
    assert removed == 1
    assert len(store.lines) == 0
    store.undo()
    assert len(store.lines) == 1


def test_erase_miss_returns_zero(qtbot):
    store = SessionStore()
    store.set_geometry((LineSegment(Point(0, 0), Point(10, 0)),), ())
    assert store.erase_near(5, 100, 2.0) == 0
    assert len(store.lines) == 1


# --- re-trace / shading invariants --------------------------------------------


def test_manual_lines_survive_retrace(qtbot):
    store = SessionStore()
    store.add_segment(Point(0, 0), Point(1, 1))  # MANUAL
    new_auto = LineSegment(Point(2, 2), Point(3, 3), source=GeometrySource.AUTO_TRACE)
    store.set_traced_lines((new_auto,))
    sources = {ls.source for ls in store.lines}
    assert GeometrySource.MANUAL in sources
    assert GeometrySource.AUTO_TRACE in sources
    assert len(store.lines) == 2


def test_retrace_replaces_only_auto_trace(qtbot):
    store = SessionStore()
    old_auto = LineSegment(Point(0, 0), Point(1, 1), source=GeometrySource.AUTO_TRACE)
    store.set_geometry((old_auto,), ())
    store.set_traced_lines(
        (LineSegment(Point(5, 5), Point(6, 6), source=GeometrySource.AUTO_TRACE),)
    )
    assert old_auto not in store.lines
    assert len(store.lines) == 1


def test_set_shading_replaces_only_shading(qtbot):
    store = SessionStore()
    store.set_traced_lines(
        (LineSegment(Point(0, 0), Point(1, 1), source=GeometrySource.AUTO_TRACE),)
    )
    quad = Quad(
        Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1), source=GeometrySource.AUTO_SHADING
    )
    store.set_shading((quad,), ())
    assert len(store.lines) == 1
    assert len(store.quads) == 1
    # Re-shading replaces quads, keeps the traced line.
    store.set_shading((), ())
    assert len(store.lines) == 1
    assert len(store.quads) == 0
