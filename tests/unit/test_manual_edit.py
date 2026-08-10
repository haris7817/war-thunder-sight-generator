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


def test_erase_removes_nearest_and_undo_restores(qtbot):
    store = SessionStore()
    store.set_geometry((LineSegment(Point(0, 0), Point(10, 0)),), ())
    assert store.erase_nearest(5, 0, 2.0) is True  # on the line
    assert len(store.lines) == 0
    store.undo()
    assert len(store.lines) == 1


def test_erase_miss_returns_false(qtbot):
    store = SessionStore()
    store.set_geometry((LineSegment(Point(0, 0), Point(10, 0)),), ())
    assert store.erase_nearest(5, 100, 2.0) is False
    assert len(store.lines) == 1


def test_erase_removes_only_one_segment_of_a_contour(qtbot):
    # Three connected segments; clicking near one removes ONLY that one.
    store = SessionStore()
    a = LineSegment(Point(0, 0), Point(10, 0))
    b = LineSegment(Point(10, 0), Point(20, 0))
    c = LineSegment(Point(20, 0), Point(30, 0))
    store.set_geometry((a, b, c), ())
    assert store.erase_nearest(15, 0, 2.0) is True  # nearest is segment b
    remaining_ids = {ls.id for ls in store.lines}
    assert remaining_ids == {a.id, c.id}


def test_erase_drag_stroke_is_single_undo(qtbot):
    store = SessionStore()
    a = LineSegment(Point(0, 0), Point(10, 0))
    b = LineSegment(Point(20, 0), Point(30, 0))
    store.set_geometry((a, b), ())
    store.erase_nearest(5, 0, 2.0, record_undo=True)  # stroke start
    store.erase_nearest(25, 0, 2.0, record_undo=False)  # same stroke
    assert len(store.lines) == 0
    store.undo()  # one undo reverts the whole stroke
    assert len(store.lines) == 2


def test_nearest_segment_picks_closest():
    from app.application.hit_testing import nearest_segment

    near = LineSegment(Point(0, 0), Point(10, 0))
    far = LineSegment(Point(0, 50), Point(10, 50))
    got = nearest_segment((near, far), 5, 1, radius=5)
    assert got is near
    assert nearest_segment((near, far), 5, 100, radius=5) is None


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


def test_manual_line_exports_and_erased_line_does_not(qtbot):
    from app.application.export_service import build_export
    from app.blk.coordinate_mapper import CoordinateMapper
    from app.domain.transform import ArtworkTransform

    store = SessionStore()
    store.set_source("x", (200, 200))
    store.add_segment(Point(50, 50), Point(150, 150))
    mapper = CoordinateMapper(200, 200)

    exported = build_export(list(store.lines), [], mapper, ArtworkTransform.identity())
    assert exported.line_count == 1
    assert "line {line:p4=" in exported.text

    store.erase_nearest(100, 100, 5.0)  # erase the drawn line
    after = build_export(list(store.lines), [], mapper, ArtworkTransform.identity())
    assert after.line_count == 0
    assert "line {line:p4=" not in after.text


def test_export_truncation_never_drops_manual_lines(qtbot):
    # Client-reported bug: manual lines sit AFTER the dense auto-trace in the list,
    # so first-N truncation silently dropped the user's hand-drawn work.
    from app.application.export_service import build_export
    from app.blk.coordinate_mapper import CoordinateMapper
    from app.domain.transform import ArtworkTransform

    auto = [
        LineSegment(Point(i, 0), Point(i + 1, 0), source=GeometrySource.AUTO_TRACE)
        for i in range(10)
    ]
    manual = [
        LineSegment(Point(77, 77), Point(88, 88), source=GeometrySource.MANUAL),
        LineSegment(Point(99, 99), Point(111, 111), source=GeometrySource.MANUAL),
    ]
    segments = auto + manual  # manual at the tail, like the real SessionStore
    mapper = CoordinateMapper(200, 200)

    result = build_export(
        segments, [], mapper, ArtworkTransform.identity(), warn_elements=1, max_elements=5
    )
    assert result.truncated is True
    assert result.line_count == 5
    # Both manual lines survive; the distinctive manual coordinates are in the text.
    sx, sy = mapper.to_sight(77, 77)
    assert f"{sx:.6f},{sy:.6f}" in result.text
    sx, sy = mapper.to_sight(99, 99)
    assert f"{sx:.6f},{sy:.6f}" in result.text


def test_export_truncation_keeps_manual_fill_quads(qtbot):
    from app.application.export_service import build_export
    from app.blk.coordinate_mapper import CoordinateMapper
    from app.domain.transform import ArtworkTransform

    auto_quads = [
        Quad(
            Point(i, 0), Point(i + 1, 0), Point(i + 1, 1), Point(i, 1),
            source=GeometrySource.AUTO_SHADING,
        )
        for i in range(6)
    ]
    manual_quad = Quad(
        Point(50, 50), Point(60, 50), Point(60, 60), Point(50, 60),
        source=GeometrySource.MANUAL_FILL,
    )
    mapper = CoordinateMapper(200, 200)
    result = build_export(
        [], auto_quads + [manual_quad], mapper, ArtworkTransform.identity(),
        warn_elements=1, max_elements=3,
    )
    assert result.truncated is True
    sx, sy = mapper.to_sight(50, 50)
    assert f"{sx:.6f},{sy:.6f}" in result.text  # the manual fill survives


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
