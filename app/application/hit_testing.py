"""Geometry hit-testing shared by the eraser (deletion) and the canvas (hover
highlight), so both agree on exactly which segment is "under" the cursor.
"""

from __future__ import annotations

from app.domain.geometry import LineSegment
from app.utils.math_utils import point_segment_distance


def nearest_segment(
    segments: tuple[LineSegment, ...] | list[LineSegment],
    x: float,
    y: float,
    radius: float,
) -> LineSegment | None:
    """Return the single closest segment within ``radius`` of (x, y), or None.

    Only the nearest one is returned — clicking one segment of a many-segment contour
    removes just that segment, never the whole path.
    """
    best: LineSegment | None = None
    best_d = radius
    for seg in segments:
        d = point_segment_distance(x, y, seg.a.x, seg.a.y, seg.b.x, seg.b.y)
        if d <= best_d:
            best_d = d
            best = seg
    return best
