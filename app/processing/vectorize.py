"""Convert simplified contours/polylines into domain LineSegments (pixel space).

Output segments are tagged ``AUTO_TRACE`` and carry image-pixel coordinates; the
export service maps them to sight units later.
"""

from __future__ import annotations

import numpy as np

from app.domain.geometry import GeometrySource, LineSegment, Point


def polyline_to_segments(
    points: np.ndarray,
    *,
    closed: bool,
    source: GeometrySource = GeometrySource.AUTO_TRACE,
) -> list[LineSegment]:
    """Turn an ``(N, 2)`` polyline into consecutive LineSegments.

    A closed polyline adds the final segment back to the first point. Degenerate
    (zero-length) segments are skipped.
    """
    pts = np.asarray(points, dtype=float).reshape(-1, 2)
    n = len(pts)
    if n < 2:
        return []

    segments: list[LineSegment] = []
    limit = n if closed else n - 1
    for i in range(limit):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        if ax == bx and ay == by:
            continue
        segments.append(LineSegment(Point(float(ax), float(ay)), Point(float(bx), float(by)), source=source))
    return segments


def contours_to_segments(
    contours: list[np.ndarray],
    *,
    closed: bool = True,
    source: GeometrySource = GeometrySource.AUTO_TRACE,
) -> list[LineSegment]:
    segments: list[LineSegment] = []
    for c in contours:
        segments.extend(polyline_to_segments(c, closed=closed, source=source))
    return segments
