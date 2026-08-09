"""Tests for SessionStore (M6)."""

from __future__ import annotations

from app.application.editing_service import SessionStore
from app.domain.geometry import GeometrySource, LineSegment, Point
from app.domain.transform import ArtworkTransform


def test_transform_change_emits_signal(qtbot):
    store = SessionStore()
    seen = []
    store.transformChanged.connect(lambda: seen.append(1))
    store.set_transform(ArtworkTransform(scale=2.0))
    assert seen == [1]
    assert store.transform.scale == 2.0


def test_geometry_change_emits_signal(qtbot):
    store = SessionStore()
    seen = []
    store.geometryChanged.connect(lambda: seen.append(1))
    store.set_geometry((LineSegment(Point(0, 0), Point(1, 1)),), ())
    assert seen == [1]
    assert len(store.lines) == 1


def test_auto_replace_preserves_manual(qtbot):
    store = SessionStore()
    manual = LineSegment(Point(0, 0), Point(1, 1), source=GeometrySource.MANUAL)
    old_auto = LineSegment(Point(2, 2), Point(3, 3), source=GeometrySource.AUTO_TRACE)
    store.set_geometry((manual, old_auto), ())

    new_auto = LineSegment(Point(5, 5), Point(6, 6), source=GeometrySource.AUTO_TRACE)
    store.set_auto_geometry((new_auto,), ())

    assert manual in store.lines
    assert new_auto in store.lines
    assert old_auto not in store.lines


def test_reset_transform(qtbot):
    store = SessionStore()
    store.set_transform(ArtworkTransform(offset_x=1.0, scale=3.0))
    store.reset_transform()
    assert store.transform.is_identity
