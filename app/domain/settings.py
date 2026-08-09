"""User-facing settings for tracing and shading, with range clamping.

Settings are immutable value objects. Out-of-range inputs are clamped on
construction (e.g. ``detail=150`` becomes ``100``) rather than raising, so the UI
sliders and the CLI can pass raw values without pre-validation.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from app.utils.math_utils import clamp, make_odd_at_least

# Element-count budget. The research cited ~800 warn / ~3000 hard ceiling, but the
# client's own working sights measured 4.5k-7.4k elements (see scripts/analyze_blk.py
# on the reference sights), so the game tolerates far more. We warn earlier than the
# cap and cap generously; both are configurable per TraceSettings.
DEFAULT_WARN_ELEMENTS = 1500
DEFAULT_MAX_ELEMENTS = 6000


class ThresholdMethod(Enum):
    OTSU = "otsu"
    GLOBAL = "global"
    ADAPTIVE = "adaptive"


class TracePreset(Enum):
    """Named bundles of trace parameters. Mapped to concrete TraceSettings by
    :func:`TraceSettings.from_preset`."""

    FAST = "fast"
    BALANCED = "balanced"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class TraceSettings:
    """Parameters controlling image -> geometry tracing."""

    threshold_method: ThresholdMethod = ThresholdMethod.OTSU
    # 0-255; only used when threshold_method is GLOBAL.
    global_threshold: int = 128
    # Odd, >= 3; only used when threshold_method is ADAPTIVE.
    adaptive_block_size: int = 21
    adaptive_c: float = 5.0
    # 0-100; higher = more detail retained (smaller approxPolyDP epsilon).
    detail: int = 50
    # Gaussian blur kernel size (odd, or 0 to disable) applied before threshold.
    blur_ksize: int = 0
    # Invert before contour finding (for light-subject-on-dark-background art).
    invert: bool = False
    # Drop contours shorter than this many pixels (noise specks).
    min_segment_length: float = 3.0
    # Element-count guards.
    warn_elements: int = DEFAULT_WARN_ELEMENTS
    max_elements: int = DEFAULT_MAX_ELEMENTS

    def __post_init__(self) -> None:
        object.__setattr__(self, "global_threshold", clamp(int(self.global_threshold), 0, 255))
        object.__setattr__(
            self, "adaptive_block_size", make_odd_at_least(int(self.adaptive_block_size), 3)
        )
        object.__setattr__(self, "adaptive_c", float(self.adaptive_c))
        object.__setattr__(self, "detail", clamp(int(self.detail), 0, 100))
        object.__setattr__(self, "blur_ksize", max(0, int(self.blur_ksize)))
        object.__setattr__(self, "min_segment_length", max(0.0, float(self.min_segment_length)))
        object.__setattr__(self, "warn_elements", max(1, int(self.warn_elements)))
        object.__setattr__(self, "max_elements", max(1, int(self.max_elements)))

    def with_detail(self, detail: int) -> TraceSettings:
        return replace(self, detail=detail)

    @classmethod
    def from_preset(cls, preset: TracePreset) -> TraceSettings:
        """A preset is just a named TraceSettings instance."""
        if preset is TracePreset.FAST:
            return cls(detail=45, blur_ksize=3)
        if preset is TracePreset.BALANCED:
            return cls(detail=68)
        if preset is TracePreset.HIGH:
            return cls(detail=82)
        raise ValueError(f"unknown preset: {preset!r}")


@dataclass(frozen=True, slots=True)
class ShadingSettings:
    """Parameters controlling shading (filled quads + hatch lines)."""

    # 0-100. 0 means shading is OFF: the shading service returns [] before any
    # computation, and the exported .blk contains no generated quad geometry.
    intensity: int = 0
    # Emit hatch lines for mid-tone regions in addition to solid fills.
    hatch: bool = True
    warn_elements: int = DEFAULT_WARN_ELEMENTS
    max_elements: int = DEFAULT_MAX_ELEMENTS

    def __post_init__(self) -> None:
        object.__setattr__(self, "intensity", clamp(int(self.intensity), 0, 100))
        object.__setattr__(self, "warn_elements", max(1, int(self.warn_elements)))
        object.__setattr__(self, "max_elements", max(1, int(self.max_elements)))

    @property
    def enabled(self) -> bool:
        return self.intensity > 0
