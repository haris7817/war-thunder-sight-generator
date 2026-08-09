"""Polyline simplification via Douglas-Peucker (approxPolyDP).

The Detail slider (0-100) maps to the simplification epsilon as a fraction of each
contour's perimeter, so it is scale-invariant: higher detail -> smaller epsilon ->
more points retained -> more segments.
"""

from __future__ import annotations

import cv2
import numpy as np

# epsilon fraction of perimeter at the extremes of the Detail slider.
_EPS_FRAC_AT_MIN_DETAIL = 0.05  # detail=0  -> coarse
_EPS_FRAC_AT_MAX_DETAIL = 0.001  # detail=100 -> fine
_MIN_EPSILON_PX = 0.5


def epsilon_for_detail(detail: int, perimeter: float) -> float:
    """Absolute approxPolyDP epsilon (pixels) for a given detail and perimeter."""
    d = max(0, min(100, detail)) / 100.0
    frac = _EPS_FRAC_AT_MIN_DETAIL + d * (_EPS_FRAC_AT_MAX_DETAIL - _EPS_FRAC_AT_MIN_DETAIL)
    return max(_MIN_EPSILON_PX, frac * perimeter)


def simplify_polyline(points: np.ndarray, detail: int, *, closed: bool) -> np.ndarray:
    """Simplify an ``(N, 2)`` polyline; returns an ``(M, 2)`` array with M <= N."""
    pts = np.asarray(points, dtype=np.int32).reshape(-1, 1, 2)
    if len(pts) < 3:
        return pts.reshape(-1, 2)
    perimeter = cv2.arcLength(pts, closed)
    eps = epsilon_for_detail(detail, perimeter)
    simplified = cv2.approxPolyDP(pts, eps, closed)
    return simplified.reshape(-1, 2)


def simplify_contours(contours: list[np.ndarray], detail: int, *, closed: bool = True) -> list[np.ndarray]:
    return [simplify_polyline(c, detail, closed=closed) for c in contours]
