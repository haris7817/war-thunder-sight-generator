"""Map image-pixel coordinates to War Thunder sight units.

Validated against real client sights (see ``scripts/analyze_blk.py``): the mapping
is isotropic (the image *height* scales both axes so aspect ratio is preserved),
the image centre maps to the sight origin, and there is **no Y-axis flip** — the
image's top row maps to negative Y (which is UP on screen; positive Y is DOWN).

    sight_x = (px - img_w/2) * (units_per_image_height / img_h)
    sight_y = (py - img_h/2) * (units_per_image_height / img_h)

The convention lives in :class:`MappingConfig` so that, if in-game testing ever
contradicts it, flipping Y or changing the divisor is a one-line change here rather
than a rewrite of the geometry.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.transform import ArtworkTransform


@dataclass(frozen=True, slots=True)
class MappingConfig:
    """Tunable coordinate convention. Defaults reflect the validated research."""

    units_per_image_height: float = 1.0
    # Research says NO flip; exposed so a contradiction in-game is a one-liner.
    flip_y: bool = False


@dataclass(frozen=True, slots=True)
class CoordinateMapper:
    """Maps between image-pixel space and sight-unit space for a given image size."""

    image_width: int
    image_height: int
    config: MappingConfig = field(default_factory=MappingConfig)

    def _scale(self) -> float:
        return self.config.units_per_image_height / self.image_height

    def to_sight(self, px: float, py: float) -> tuple[float, float]:
        """Image pixel -> base sight units (centred, isotropic, no transform)."""
        s = self._scale()
        sx = (px - self.image_width / 2.0) * s
        sy = (py - self.image_height / 2.0) * s
        if self.config.flip_y:
            sy = -sy
        return sx, sy

    def to_sight_transformed(
        self, px: float, py: float, transform: ArtworkTransform
    ) -> tuple[float, float]:
        """Image pixel -> sight units with the user's artwork transform applied."""
        sx, sy = self.to_sight(px, py)
        return transform.apply(sx, sy)

    def from_sight(self, sx: float, sy: float) -> tuple[float, float]:
        """Sight units -> image pixel (inverse of :meth:`to_sight`, no transform).

        Used by the canvas/hit-testing in later milestones.
        """
        s = self._scale()
        if s == 0:
            raise ValueError("degenerate mapping: scale is zero")
        if self.config.flip_y:
            sy = -sy
        px = sx / s + self.image_width / 2.0
        py = sy / s + self.image_height / 2.0
        return px, py
