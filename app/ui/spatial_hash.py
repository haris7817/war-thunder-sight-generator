"""Uniform-grid spatial hash over line segments (image-space) for fast hit-testing.

Built in M5 so M7's erase tool is additive. Each segment is bucketed into the grid
cells its bounding box overlaps; :meth:`candidates_near` returns the segments in the
cells around a query point — a small superset to run exact distance checks against.
"""

from __future__ import annotations

import math
from collections.abc import Iterable

from app.domain.geometry import LineSegment


class SpatialHash:
    def __init__(self, cell_size: float = 32.0) -> None:
        self.cell_size = max(1.0, cell_size)
        self._cells: dict[tuple[int, int], list[LineSegment]] = {}

    def _cell(self, x: float, y: float) -> tuple[int, int]:
        return (int(math.floor(x / self.cell_size)), int(math.floor(y / self.cell_size)))

    def build(self, segments: Iterable[LineSegment]) -> None:
        self._cells.clear()
        for seg in segments:
            cx0, cy0 = self._cell(min(seg.a.x, seg.b.x), min(seg.a.y, seg.b.y))
            cx1, cy1 = self._cell(max(seg.a.x, seg.b.x), max(seg.a.y, seg.b.y))
            for cx in range(cx0, cx1 + 1):
                for cy in range(cy0, cy1 + 1):
                    self._cells.setdefault((cx, cy), []).append(seg)

    def candidates_near(self, x: float, y: float, radius: float) -> list[LineSegment]:
        cells = max(0, int(math.ceil(radius / self.cell_size)))
        cx, cy = self._cell(x, y)
        seen: dict[int, LineSegment] = {}
        for gx in range(cx - cells, cx + cells + 1):
            for gy in range(cy - cells, cy + cells + 1):
                for seg in self._cells.get((gx, gy), ()):
                    seen[seg.id] = seg
        return list(seen.values())
