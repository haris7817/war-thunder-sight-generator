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


def make_odd_at_least(value: int, minimum: int = 3) -> int:
    """Return the smallest odd int >= ``value`` and >= ``minimum``.

    OpenCV adaptive-threshold block sizes must be odd and >= 3.
    """
    value = max(value, minimum)
    return value if value % 2 == 1 else value + 1
