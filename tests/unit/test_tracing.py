"""Unit tests for the tracing pipeline (M4): simplify, vectorize, tracing_service."""

from __future__ import annotations

import time

import cv2
import numpy as np
from app.application.export_service import build_export
from app.application.tracing_service import TraceMode, trace
from app.blk.coordinate_mapper import CoordinateMapper
from app.domain.geometry import GeometrySource
from app.domain.settings import ThresholdMethod, TraceSettings
from app.domain.transform import ArtworkTransform
from app.processing.simplify import epsilon_for_detail, simplify_polyline
from app.processing.vectorize import polyline_to_segments

from tests.fixtures import synthetic

# --- simplify + vectorize ------------------------------------------------------


def test_collinear_points_collapse_to_one_segment():
    pts = np.array([[i, 0] for i in range(100)], dtype=np.int32)
    simplified = simplify_polyline(pts, detail=50, closed=False)
    segments = polyline_to_segments(simplified, closed=False)
    assert len(segments) == 1


def test_epsilon_decreases_with_detail():
    # Higher detail -> smaller epsilon -> more points retained.
    assert epsilon_for_detail(0, 1000) > epsilon_for_detail(100, 1000)


def test_closed_square_yields_four_segments():
    square = np.array([[0, 0], [10, 0], [10, 10], [0, 10]], dtype=np.int32)
    segments = polyline_to_segments(square, closed=True)
    assert len(segments) == 4
    # Closed: last segment ends where the first began.
    assert segments[-1].b.x == segments[0].a.x
    assert segments[-1].b.y == segments[0].a.y


def test_open_polyline_skips_closing_segment():
    square = np.array([[0, 0], [10, 0], [10, 10], [0, 10]], dtype=np.int32)
    assert len(polyline_to_segments(square, closed=False)) == 3


def test_zero_length_segments_are_skipped():
    pts = np.array([[0, 0], [0, 0], [5, 5]], dtype=np.int32)
    segments = polyline_to_segments(pts, closed=False)
    assert all(not (s.a.x == s.b.x and s.a.y == s.b.y) for s in segments)


# --- tracing_service -----------------------------------------------------------


def test_trace_produces_auto_segments():
    # A circle traces to many short segments that survive the long-chord filter.
    result = trace(synthetic.filled_circle(300), TraceSettings(detail=60))
    assert result.segment_count > 0
    assert all(s.source is GeometrySource.AUTO_TRACE for s in result.segments)


def test_detail_increases_segment_count():
    img = synthetic.filled_circle(400)
    low = trace(img, TraceSettings(detail=20))
    high = trace(img, TraceSettings(detail=95))
    assert high.segment_count > low.segment_count


def test_trace_is_deterministic():
    img = synthetic.filled_circle(300)
    a = trace(img, TraceSettings(detail=60))
    b = trace(img, TraceSettings(detail=60))
    # LineSegment equality ignores id and compares points + source.
    assert a.segments == b.segments


def test_noise_floor_drops_short_contours():
    # find_contours' min_arc_length must drop tiny specks while keeping big shapes.
    from app.processing.contours import find_contours

    binary = np.zeros((400, 400), dtype=np.uint8)
    cv2.circle(binary, (200, 200), 100, 255, 2)  # big ring (perimeter ~628)
    cv2.circle(binary, (30, 30), 1, 255, -1)  # tiny speck
    all_c = find_contours(binary, min_arc_length=0)
    filtered = find_contours(binary, min_arc_length=50)
    assert len(filtered) < len(all_c)
    assert len(filtered) >= 1  # the big ring survives


def test_hard_cap_truncates():
    img = synthetic.noise(300, seed=1)  # lots of edges
    result = trace(img, TraceSettings(detail=80, warn_elements=10, max_elements=50))
    assert result.truncated is True
    assert result.segment_count <= 50


def test_long_chord_filter_drops_cross_image_segments():
    img = synthetic.line_art(400)
    loose = trace(img, TraceSettings(detail=60), max_segment_frac=1.0)
    tight = trace(img, TraceSettings(detail=60), max_segment_frac=0.05)
    assert tight.segment_count < loose.segment_count


def test_fill_mode_runs():
    result = trace(
        synthetic.filled_circle(256),
        TraceSettings(detail=60, threshold_method=ThresholdMethod.ADAPTIVE),
        mode=TraceMode.FILL,
    )
    assert result.segment_count > 0


# --- end-to-end PNG -> valid .blk ----------------------------------------------


def test_trace_then_export_is_valid_blk():
    img = synthetic.crosshair(200)
    result = trace(img, TraceSettings(detail=60))
    mapper = CoordinateMapper(image_width=result.width, image_height=result.height)
    export = build_export(list(result.segments), [], mapper, ArtworkTransform.identity())
    assert export.text.count("{") == export.text.count("}")
    assert "drawLines{" in export.text
    assert export.line_count == result.segment_count


def test_trace_performance_2000px_under_budget():
    img = synthetic.line_art(2000)
    start = time.perf_counter()
    trace(img, TraceSettings(detail=68))
    elapsed = time.perf_counter() - start
    assert elapsed < 3.0  # generous CI bound; locally well under
