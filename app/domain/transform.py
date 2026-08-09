"""User-controllable artwork transform (move / scale / rotate).

Implements a 2-D similarity transform as a 2x3 affine matrix. Composition order is
**scale, then rotate, then translate**, so a point ``(x, y)`` maps to::

    x' = a*x + c*y + tx
    y' = b*x + d*y + ty

with ``a = s*cosθ, c = -s*sinθ, b = s*sinθ, d = s*cosθ`` and ``(tx, ty)`` the
offset. Angles are in degrees; positive rotation follows the standard
counter-clockwise convention in a Y-up sense (which reads clockwise on screen in
the sight's Y-down space). ``apply`` operates on plain floats so this stays free of
any geometry/Qt dependency.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ArtworkTransform:
    """A 2-D similarity transform applied to traced geometry.

    Composition order (implemented in M2): scale, then rotate, then translate.
    """

    offset_x: float = 0.0
    offset_y: float = 0.0
    scale: float = 1.0
    rotation_deg: float = 0.0

    @classmethod
    def identity(cls) -> ArtworkTransform:
        return cls()

    @property
    def is_identity(self) -> bool:
        return (
            self.offset_x == 0.0
            and self.offset_y == 0.0
            and self.scale == 1.0
            and self.rotation_deg == 0.0
        )

    def to_matrix(self) -> tuple[float, float, float, float, float, float]:
        """Return the affine coefficients ``(a, b, c, d, tx, ty)``.

        Where ``x' = a*x + c*y + tx`` and ``y' = b*x + d*y + ty``.
        """
        theta = math.radians(self.rotation_deg)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        s = self.scale
        a = s * cos_t
        b = s * sin_t
        c = -s * sin_t
        d = s * cos_t
        return (a, b, c, d, self.offset_x, self.offset_y)

    def apply(self, x: float, y: float) -> tuple[float, float]:
        """Apply the transform (scale -> rotate -> translate) to a point."""
        a, b, c, d, tx, ty = self.to_matrix()
        return (a * x + c * y + tx, b * x + d * y + ty)

    def inverse(self) -> ArtworkTransform:
        """Return the transform that undoes this one.

        Only defined for non-degenerate transforms (``scale != 0``). The result is
        expressed back in ``ArtworkTransform`` terms: inverse scale ``1/s``, negated
        rotation, and the correspondingly transformed offset.
        """
        if self.scale == 0.0:
            raise ValueError("cannot invert a transform with scale == 0")
        inv_scale = 1.0 / self.scale
        inv_rot = -self.rotation_deg
        # New offset: apply the inverse linear map to the negated translation.
        theta = math.radians(inv_rot)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        # Inverse linear part (scale 1/s, rotation -theta) applied to (-tx, -ty).
        nx, ny = -self.offset_x, -self.offset_y
        off_x = inv_scale * (cos_t * nx - sin_t * ny)
        off_y = inv_scale * (sin_t * nx + cos_t * ny)
        return ArtworkTransform(
            offset_x=off_x,
            offset_y=off_y,
            scale=inv_scale,
            rotation_deg=inv_rot,
        )

    def apply_inverse(self, x: float, y: float) -> tuple[float, float]:
        """Apply the inverse transform to a point (convenience)."""
        return self.inverse().apply(x, y)
