"""Generate shading geometry from an image: convex filled quads for solid dark
regions, plus optional hatch lines for mid-tones.

Two hard rules (mirrored by assertions at export time):

* ``intensity == 0`` short-circuits to empty output *before any computation*.
* every emitted quad is convex and non-degenerate (built from ``minAreaRect``).

Background handling: dark regions connected to the image border are treated as
background and excluded, so a dark-background painting (e.g. Acherona) is not filled
edge-to-edge — only the subject's interior dark areas become fills.
"""

from __future__ import annotations

import cv2
import numpy as np

from app.domain.geometry import GeometrySource, LineSegment, Point, Quad
from app.domain.settings import ShadingSettings
from app.processing.preprocess import to_grayscale


def _dark_cutoff(intensity: int) -> int:
    # intensity 1..100 -> cutoff ~13..128 (more intensity fills lighter pixels too).
    return int(round(13 + (intensity / 100.0) * 115))


def _interior_mask(dark: np.ndarray) -> np.ndarray:
    """Remove connected components that touch the image border (the background)."""
    num, labels = cv2.connectedComponents(dark)
    if num <= 1:
        return dark
    border = set(np.unique(labels[0, :])) | set(np.unique(labels[-1, :]))
    border |= set(np.unique(labels[:, 0])) | set(np.unique(labels[:, -1]))
    border.discard(0)
    keep = np.isin(labels, list(border), invert=True) & (labels != 0)
    return (keep.astype(np.uint8)) * 255


def _quad_from_contour(contour: np.ndarray) -> Quad:
    box = cv2.boxPoints(cv2.minAreaRect(contour))  # 4 corners, convex order
    pts = [Point(float(x), float(y)) for x, y in box]
    return Quad(pts[0], pts[1], pts[2], pts[3], source=GeometrySource.AUTO_SHADING)


def generate_shading(
    rgb: np.ndarray, settings: ShadingSettings
) -> tuple[list[Quad], list[LineSegment]]:
    """Return ``(fill_quads, hatch_lines)`` for the given image and settings.

    Returns ``([], [])`` immediately when shading is disabled (intensity 0).
    """
    if not settings.enabled:
        return [], []

    gray = to_grayscale(rgb)
    h, w = gray.shape[:2]
    diag = float(np.hypot(w, h))

    cutoff = _dark_cutoff(settings.intensity)
    dark = (gray < cutoff).astype(np.uint8) * 255
    dark = _interior_mask(dark)
    # Clean speckle so we get solid fillable regions.
    kernel = np.ones((3, 3), np.uint8)
    dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, kernel)

    min_area = (0.004 * diag) ** 2  # ignore tiny blobs
    contours, _ = cv2.findContours(dark, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    quads: list[Quad] = []
    for c in contours:
        if cv2.contourArea(c) < min_area:
            continue
        rect = cv2.minAreaRect(c)
        (_, _), (rw, rh), _ = rect
        if rw < 1 or rh < 1:
            continue
        quads.append(_quad_from_contour(c))
        if len(quads) >= settings.max_elements:
            break

    hatch: list[LineSegment] = []
    if settings.hatch:
        hatch = _hatch_lines(gray, cutoff, diag, settings)

    return quads, hatch


def _hatch_lines(
    gray: np.ndarray, dark_cutoff: int, diag: float, settings: ShadingSettings
) -> list[LineSegment]:
    """Diagonal hatch across mid-tone pixels (between dark and light)."""
    h, w = gray.shape[:2]
    mid_hi = min(255, dark_cutoff + 70)
    mid = (gray >= dark_cutoff) & (gray < mid_hi)
    if not mid.any():
        return []

    # Spacing tightens with intensity; clamp so counts stay bounded.
    step = max(8, int(diag * (0.05 - settings.intensity / 100.0 * 0.035)))
    lines: list[LineSegment] = []
    # Diagonal lines y = x + c; sample points along each and emit short segments
    # where the pixel is mid-tone.
    for c in range(-h, w, step):
        prev: tuple[int, int] | None = None
        for x in range(0, w, 3):
            y = x - c
            if 0 <= y < h and mid[y, x]:
                if prev is None:
                    prev = (x, y)
            else:
                if prev is not None:
                    lines.append(
                        LineSegment(
                            Point(float(prev[0]), float(prev[1])),
                            Point(float(x), float(y)),
                            source=GeometrySource.AUTO_SHADING,
                        )
                    )
                    prev = None
        if len(lines) >= settings.max_elements:
            break
    return lines
