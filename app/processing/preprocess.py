"""Grayscale conversion, optional blur, and resize for the tracing pipeline.

The pipeline is grayscale-first: colour only ever contributes to luminance, and no
colour is carried into the exported sight (crosshair colour comes from the template).
"""

from __future__ import annotations

import cv2
import numpy as np

from app.utils.math_utils import make_odd_at_least


def to_grayscale(rgb: np.ndarray) -> np.ndarray:
    """Convert an HxWx3 RGB uint8 array to an HxW uint8 grayscale array."""
    if rgb.ndim == 2:
        return rgb.astype(np.uint8)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)


def gaussian_blur(gray: np.ndarray, ksize: int) -> np.ndarray:
    """Gaussian blur with an auto-corrected odd kernel; ``ksize <= 0`` is a no-op."""
    if ksize <= 0:
        return gray
    k = make_odd_at_least(ksize, 3)
    return cv2.GaussianBlur(gray, (k, k), 0)


def resize_to_max(gray: np.ndarray, max_dimension: int) -> np.ndarray:
    """Downscale so the longest edge is ``max_dimension`` (no upscaling)."""
    h, w = gray.shape[:2]
    longest = max(h, w)
    if longest <= max_dimension:
        return gray
    factor = max_dimension / longest
    new_size = (max(1, round(w * factor)), max(1, round(h * factor)))
    return cv2.resize(gray, new_size, interpolation=cv2.INTER_AREA)


def preprocess(rgb: np.ndarray, *, blur_ksize: int = 0) -> np.ndarray:
    """Full preprocess: RGB -> grayscale -> optional blur."""
    gray = to_grayscale(rgb)
    return gaussian_blur(gray, blur_ksize)
