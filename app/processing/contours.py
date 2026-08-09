"""Extract contours from an image for vectorisation.

Two trace inputs are supported, both reduced to a binary map that OpenCV's
``findContours`` walks:

* **edge mode (default)** — ``auto_canny`` finds tonal edges. It is polarity-
  independent, which is essential for the real client paintings (Remielle is
  majority-light with a dark subject on a dark background surrounded by white
  wings — no fill threshold can separate it, but its edges are unambiguous).
* **fill mode** — a caller-supplied binary (from ``app.processing.threshold``) for
  clean line-art / silhouettes.

``find_contours`` filters out short/small specks and returns each contour as an
``(N, 2)`` int array of pixel points.
"""

from __future__ import annotations

import cv2
import numpy as np


def auto_canny(gray: np.ndarray, sigma: float = 0.33) -> np.ndarray:
    """Canny edges with thresholds derived from the image median (no manual tuning)."""
    med = float(np.median(gray))
    low = int(max(0, (1.0 - sigma) * med))
    high = int(min(255, (1.0 + sigma) * med))
    if high <= low:
        high = low + 1
    return cv2.Canny(gray, low, high)


def find_contours(
    binary: np.ndarray,
    *,
    min_arc_length: float = 0.0,
    min_area: float = 0.0,
    external_only: bool = False,
) -> list[np.ndarray]:
    """Find contours in a binary image, filtered by perimeter and area.

    Returns a list of ``(N, 2)`` int arrays (pixel coordinates). ``RETR_LIST`` keeps
    every contour (edge loops have no meaningful hierarchy); ``external_only`` uses
    ``RETR_EXTERNAL`` to keep just outer boundaries (useful for solid silhouettes).
    """
    mode = cv2.RETR_EXTERNAL if external_only else cv2.RETR_LIST
    contours, _ = cv2.findContours(binary, mode, cv2.CHAIN_APPROX_SIMPLE)
    out: list[np.ndarray] = []
    for c in contours:
        if min_arc_length > 0 and cv2.arcLength(c, True) < min_arc_length:
            continue
        if min_area > 0 and cv2.contourArea(c) < min_area:
            continue
        out.append(c.reshape(-1, 2))
    return out
