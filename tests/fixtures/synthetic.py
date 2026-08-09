"""Procedurally-generated image fixtures.

Built at test time so no binary assets enter the repo and CI runs without any
client artwork. All generators return uint8 NumPy arrays: RGB (HxWx3) unless noted.
"""

from __future__ import annotations

import cv2
import numpy as np

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def white_canvas(height: int, width: int) -> np.ndarray:
    return np.full((height, width, 3), 255, dtype=np.uint8)


def crosshair(size: int = 200, thickness: int = 2) -> np.ndarray:
    """Black plus-shaped crosshair on white (clean dark-on-light line art)."""
    img = white_canvas(size, size)
    c = size // 2
    cv2.line(img, (0, c), (size - 1, c), BLACK, thickness)
    cv2.line(img, (c, 0), (c, size - 1), BLACK, thickness)
    return img


def line_art(size: int = 256, thickness: int = 2) -> np.ndarray:
    """A rectangle + diagonal, black on white."""
    img = white_canvas(size, size)
    a, b = size // 4, 3 * size // 4
    cv2.rectangle(img, (a, a), (b, b), BLACK, thickness)
    cv2.line(img, (a, a), (b, b), BLACK, thickness)
    return img


def gradient(size: int = 256) -> np.ndarray:
    """Horizontal 0..255 luminance gradient (defeats a single global threshold)."""
    row = np.linspace(0, 255, size, dtype=np.uint8)
    g = np.tile(row, (size, 1))
    return np.dstack([g, g, g])


def noise(size: int = 128, seed: int = 0) -> np.ndarray:
    """Deterministic uniform noise (seeded)."""
    rng = np.random.default_rng(seed)
    g = rng.integers(0, 256, (size, size), dtype=np.uint8)
    return np.dstack([g, g, g])


def bimodal(size: int = 100, low: int = 40, high: int = 200, split: float = 0.5) -> np.ndarray:
    """Left band at ``low``, right band at ``high`` — histogram has a clear valley.

    Otsu should place its threshold between ``low`` and ``high``.
    """
    gray = np.full((size, size), high, dtype=np.uint8)
    gray[:, : int(size * split)] = low
    return np.dstack([gray, gray, gray])


def light_on_dark(size: int = 200) -> np.ndarray:
    """White filled circle on black background (needs the invert path)."""
    img = np.zeros((size, size, 3), dtype=np.uint8)
    c = size // 2
    cv2.circle(img, (c, c), size // 4, WHITE, -1)
    return img


def alpha_art(size: int = 128) -> np.ndarray:
    """RGBA: opaque black square centred on a fully transparent background.

    Flattening over white must yield black-on-white, not black-on-black.
    """
    rgba = np.zeros((size, size, 4), dtype=np.uint8)
    q = size // 4
    rgba[q : 3 * q, q : 3 * q, 3] = 255  # opaque alpha in centre
    rgba[q : 3 * q, q : 3 * q, 0:3] = 0  # black subject
    return rgba
