"""Shading orchestration — kept separate from tracing_service so neither becomes a
god object. Thin wrapper over :func:`app.processing.shading.generate_shading`.
"""

from __future__ import annotations

import numpy as np

from app.domain.geometry import LineSegment, Quad
from app.domain.settings import ShadingSettings
from app.processing.shading import generate_shading


def generate(
    rgb: np.ndarray, settings: ShadingSettings
) -> tuple[list[Quad], list[LineSegment]]:
    """Return ``(fill_quads, hatch_lines)``; empty when shading is disabled."""
    return generate_shading(rgb, settings)
