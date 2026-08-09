"""User-controllable artwork transform (move / scale / rotate).

M1 defines only the immutable fields and the identity constructor. The affine
math (``to_matrix`` / ``apply`` / ``inverse``) lands in M2, where it is unit-tested
against hand-computed values with the composition order scale -> rotate -> translate.
"""

from __future__ import annotations

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
