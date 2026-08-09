"""Binarisation: Otsu, global, and adaptive thresholding.

All functions take an HxW uint8 grayscale image and return a strictly binary
(values in {0, 255}) uint8 image where **foreground/artwork is 255** and background
is 0 — the polarity OpenCV's contour finder expects.

Polarity handling (the crux for the real samples):

* Line-art on a light background (Faye_Spike): dark strokes are the subject, so the
  default (``invert=False``) maps dark pixels -> 255.
* A light subject on a dark background (Remielle, Acherona): pass ``invert=True`` so
  bright pixels -> 255. :func:`should_invert` auto-detects this from the border.
"""

from __future__ import annotations

import cv2
import numpy as np

from app.utils.math_utils import make_odd_at_least


def _thresh_type(invert: bool) -> int:
    # Default: dark subject on light bg -> BINARY_INV makes dark pixels foreground.
    # invert: light subject on dark bg -> BINARY makes bright pixels foreground.
    return cv2.THRESH_BINARY if invert else cv2.THRESH_BINARY_INV


def should_invert(gray: np.ndarray, border: int = 4) -> bool:
    """Heuristic: True if the image border is dark (=> light subject on dark bg).

    Samples a ``border``-pixel frame around the edge; if its mean luminance is below
    mid-gray the background is dark and thresholding should be inverted.
    """
    h, w = gray.shape[:2]
    b = min(border, h, w)
    if b <= 0:
        return False
    frame = np.concatenate(
        [
            gray[:b, :].ravel(),
            gray[-b:, :].ravel(),
            gray[:, :b].ravel(),
            gray[:, -b:].ravel(),
        ]
    )
    return float(frame.mean()) < 128.0


def otsu(gray: np.ndarray, *, invert: bool = False) -> np.ndarray:
    """Otsu's automatic global threshold."""
    _, out = cv2.threshold(gray, 0, 255, _thresh_type(invert) | cv2.THRESH_OTSU)
    return out


def global_threshold(gray: np.ndarray, t: int, *, invert: bool = False) -> np.ndarray:
    """Fixed global threshold at level ``t`` (0-255)."""
    t = int(max(0, min(255, t)))
    _, out = cv2.threshold(gray, t, 255, _thresh_type(invert))
    return out


def adaptive(
    gray: np.ndarray,
    block_size: int = 21,
    c: float = 5.0,
    *,
    invert: bool = False,
) -> np.ndarray:
    """Adaptive Gaussian threshold (per-neighbourhood), good for uneven lighting."""
    block = make_odd_at_least(int(block_size), 3)
    return cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        _thresh_type(invert),
        block,
        float(c),
    )
