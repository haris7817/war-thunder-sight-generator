"""Small numeric helpers with no third-party dependencies."""

from __future__ import annotations


def clamp[Number: (int, float)](value: Number, low: Number, high: Number) -> Number:
    """Clamp ``value`` into the inclusive ``[low, high]`` range.

    Preserves the input type (int stays int, float stays float).
    """
    if low > high:
        raise ValueError(f"clamp bounds inverted: low={low} > high={high}")
    if value < low:
        return low
    if value > high:
        return high
    return value


def point_segment_distance(
    px: float, py: float, ax: float, ay: float, bx: float, by: float
) -> float:
    """Shortest distance from point (px,py) to segment (a,b), incl. endpoint cases."""
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    cx, cy = ax + t * dx, ay + t * dy
    return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5


def make_odd_at_least(value: int, minimum: int = 3) -> int:
    """Return the smallest odd int >= ``value`` and >= ``minimum``.

    OpenCV adaptive-threshold block sizes must be odd and >= 3.
    """
    value = max(value, minimum)
    return value if value % 2 == 1 else value + 1
