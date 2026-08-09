"""Unit tests for the M1 domain model: geometry, settings, session."""

from __future__ import annotations

import dataclasses

import pytest
from app.domain.geometry import GeometrySource, LineSegment, Point, Quad
from app.domain.session import SessionState
from app.domain.settings import (
    ShadingSettings,
    ThresholdMethod,
    TracePreset,
    TraceSettings,
)
from app.domain.transform import ArtworkTransform

# --- Point / LineSegment / Quad construction & immutability ---------------------


def test_point_construction_and_iter():
    p = Point(1.5, -2.0)
    assert p.x == 1.5
    assert p.y == -2.0
    assert tuple(p) == (1.5, -2.0)


def test_point_is_frozen():
    p = Point(0.0, 0.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.x = 9.0  # type: ignore[misc]


def test_line_segment_defaults_to_auto_trace():
    seg = LineSegment(Point(0, 0), Point(1, 1))
    assert seg.source is GeometrySource.AUTO_TRACE
    assert seg.source.is_auto is True


def test_quad_vertices_order():
    q = Quad(Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1))
    assert q.vertices == (q.tl, q.tr, q.br, q.bl)
    assert q.source is GeometrySource.AUTO_SHADING


def test_quad_is_frozen():
    q = Quad(Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1))
    with pytest.raises(dataclasses.FrozenInstanceError):
        q.tl = Point(5, 5)  # type: ignore[misc]


# --- ID uniqueness (excluded from equality) ------------------------------------


def test_ids_are_unique_across_elements():
    segs = [LineSegment(Point(0, 0), Point(1, 1)) for _ in range(100)]
    ids = {s.id for s in segs}
    assert len(ids) == 100


def test_equal_geometry_compares_equal_despite_distinct_ids():
    a = LineSegment(Point(0, 0), Point(1, 1))
    b = LineSegment(Point(0, 0), Point(1, 1))
    assert a.id != b.id
    assert a == b  # id has compare=False


# --- GeometrySource semantics --------------------------------------------------


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (GeometrySource.AUTO_TRACE, True),
        (GeometrySource.AUTO_SHADING, True),
        (GeometrySource.MANUAL, False),
        (GeometrySource.MANUAL_FILL, False),
        (GeometrySource.SHADING, False),
    ],
)
def test_is_auto_classification(source, expected):
    assert source.is_auto is expected


# --- Settings clamping ---------------------------------------------------------


def test_trace_detail_clamped_high():
    assert TraceSettings(detail=150).detail == 100


def test_trace_detail_clamped_low():
    assert TraceSettings(detail=-10).detail == 0


def test_global_threshold_clamped():
    assert TraceSettings(global_threshold=999).global_threshold == 255
    assert TraceSettings(global_threshold=-5).global_threshold == 0


def test_adaptive_block_size_forced_odd_and_min():
    assert TraceSettings(adaptive_block_size=20).adaptive_block_size == 21
    assert TraceSettings(adaptive_block_size=1).adaptive_block_size == 3


def test_presets_are_named_trace_settings():
    fast = TraceSettings.from_preset(TracePreset.FAST)
    balanced = TraceSettings.from_preset(TracePreset.BALANCED)
    high = TraceSettings.from_preset(TracePreset.HIGH)
    assert fast.detail < balanced.detail < high.detail
    assert fast.threshold_method is ThresholdMethod.OTSU


def test_shading_intensity_zero_is_disabled():
    s = ShadingSettings(intensity=0)
    assert s.enabled is False


def test_shading_intensity_clamped_and_enabled():
    s = ShadingSettings(intensity=250)
    assert s.intensity == 100
    assert s.enabled is True


# --- Transform identity --------------------------------------------------------


def test_artwork_transform_identity():
    t = ArtworkTransform.identity()
    assert t.is_identity is True
    assert (t.offset_x, t.offset_y, t.scale, t.rotation_deg) == (0.0, 0.0, 1.0, 0.0)


# --- SessionState re-trace invariant -------------------------------------------


def test_replace_auto_geometry_preserves_manual():
    manual = LineSegment(Point(0, 0), Point(1, 1), source=GeometrySource.MANUAL)
    old_auto = LineSegment(Point(2, 2), Point(3, 3), source=GeometrySource.AUTO_TRACE)
    state = SessionState(lines=(manual, old_auto))

    new_auto = LineSegment(Point(5, 5), Point(6, 6), source=GeometrySource.AUTO_TRACE)
    updated = state.replace_auto_geometry(lines=(new_auto,), quads=())

    sources = [ls.source for ls in updated.lines]
    assert GeometrySource.MANUAL in sources
    assert manual in updated.lines
    assert old_auto not in updated.lines
    assert new_auto in updated.lines
    assert updated.manual_geometry_count() == 1


def test_session_element_count():
    state = SessionState(
        lines=(LineSegment(Point(0, 0), Point(1, 1)),),
        quads=(Quad(Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)),),
    )
    assert state.element_count == 2
