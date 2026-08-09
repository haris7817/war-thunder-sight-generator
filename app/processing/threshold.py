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


def should_invert(gray: np.ndarray, border: int = 6, inset_frac: float = 0.03) -> bool:
    """Heuristic: True if the background is dark (=> light subject on dark bg).

    Samples a thin band of the image *inset* from each edge, using the **median**
    luminance. The inset skips a decorative frame (real client art like Remielle has
    a thin white border around a dark image that would otherwise flip the polarity);
    the median resists outliers. Below mid-gray => dark background => invert.
    """
    h, w = gray.shape[:2]
    inset = int(min(h, w) * inset_frac)
    b = max(1, min(border, (min(h, w) - inset) // 2))
    if b <= 0 or inset + b >= min(h, w):
        inset = 0  # too small for an inset; fall back to the outer edge
    bands = [
        gray[inset : inset + b, :],
        gray[h - inset - b : h - inset, :],
        gray[:, inset : inset + b],
        gray[:, w - inset - b : w - inset],
    ]
    frame = np.concatenate([band.ravel() for band in bands])
    return float(np.median(frame)) < 128.0


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
