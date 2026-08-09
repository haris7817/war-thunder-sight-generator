"""Immutable geometry primitives and their provenance tagging.

These are pure data. Coordinate-space conversion lives in ``app.blk`` and
convexity enforcement for quads lives at generation/export time (M2/M7) — the
domain objects here deliberately do not validate geometric shape so that, for
example, a triangle-as-degenerate-quad (two duplicated corners) is representable.
"""

from __future__ import annotations

import itertools
import threading
from dataclasses import dataclass, field
from enum import Enum

# Monotonic, thread-safe identity source. IDs are runtime handles only — they are
# never written to the .blk and are excluded from equality (compare=False) so that
# two geometrically-equal elements compare equal regardless of id. This keeps the
# golden export tests (which compare geometry, not ids) deterministic.
_id_counter = itertools.count(1)
_id_lock = threading.Lock()


def _next_id() -> int:
    with _id_lock:
        return next(_id_counter)


class GeometrySource(Enum):
    """Where a geometry element came from.

    The distinction matters for the re-trace invariant (M7): re-tracing replaces
    only ``AUTO_TRACE``/``AUTO_SHADING`` and must never delete user-authored
    ``MANUAL``/``MANUAL_FILL`` geometry.
    """

    AUTO_TRACE = "auto_trace"
    MANUAL = "manual"
    SHADING = "shading"
    AUTO_SHADING = "auto_shading"
    MANUAL_FILL = "manual_fill"

    @property
    def is_auto(self) -> bool:
        """True for machine-generated sources that re-trace is allowed to replace."""
        return self in (GeometrySource.AUTO_TRACE, GeometrySource.AUTO_SHADING)


@dataclass(frozen=True, slots=True)
class Point:
    """A 2-D point in a coordinate space determined by context (image px or sight units)."""

    x: float
    y: float

    def __iter__(self):
        yield self.x
        yield self.y


@dataclass(frozen=True, slots=True)
class LineSegment:
    """A straight segment between two points."""

    a: Point
    b: Point
    source: GeometrySource = GeometrySource.AUTO_TRACE
    id: int = field(default_factory=_next_id, compare=False)


@dataclass(frozen=True, slots=True)
class Quad:
    """A four-vertex polygon used for filled/shaded regions.

    Vertex order is ``tl -> tr -> br -> bl`` (clockwise in the sight's Y-down
    space). A triangle is expressed by duplicating two adjacent corners.
    Convexity is required by the game and is asserted at export, not here.
    """

    tl: Point
    tr: Point
    br: Point
    bl: Point
    source: GeometrySource = GeometrySource.AUTO_SHADING
    id: int = field(default_factory=_next_id, compare=False)

    @property
    def vertices(self) -> tuple[Point, Point, Point, Point]:
        return (self.tl, self.tr, self.br, self.bl)
