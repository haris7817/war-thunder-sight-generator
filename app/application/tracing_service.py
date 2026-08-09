"""Orchestrate image -> traced LineSegments (pixel space).

Pipeline: preprocess -> binary trace map (edge or fill) -> contours -> simplify ->
segments, then enforce the element budget. Presets (Fast/Balanced/High) are just
named :class:`TraceSettings`. Output segments are in image-pixel coordinates; the
export service maps them to sight units.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np

from app.domain.geometry import LineSegment
from app.domain.settings import ThresholdMethod, TraceSettings
from app.infrastructure.logging_config import get_logger
from app.processing.contours import auto_canny, find_contours
from app.processing.preprocess import preprocess
from app.processing.simplify import simplify_contours
from app.processing.threshold import adaptive, global_threshold, otsu, should_invert
from app.processing.vectorize import contours_to_segments

log = get_logger("tracing")


class TraceMode(Enum):
    """How the binary trace map is produced."""

    EDGE = "edge"  # auto-Canny; polarity-independent (default; best for paintings)
    FILL = "fill"  # threshold -> region contours (clean line-art / silhouettes)


@dataclass(frozen=True, slots=True)
class TraceResult:
    segments: tuple[LineSegment, ...]
    width: int
    height: int
    contour_count: int
    truncated: bool
    warnings: tuple[str, ...]

    @property
    def segment_count(self) -> int:
        return len(self.segments)


def _binary_for_trace(
    gray: np.ndarray,
    settings: TraceSettings,
    mode: TraceMode,
    invert: bool | None,
) -> np.ndarray:
    if mode is TraceMode.EDGE:
        return auto_canny(gray)
    inv = should_invert(gray) if invert is None else invert
    method = settings.threshold_method
    if method is ThresholdMethod.OTSU:
        return otsu(gray, invert=inv)
    if method is ThresholdMethod.GLOBAL:
        return global_threshold(gray, settings.global_threshold, invert=inv)
    return adaptive(gray, settings.adaptive_block_size, settings.adaptive_c, invert=inv)


def _segment_length(seg: LineSegment) -> float:
    return float(np.hypot(seg.b.x - seg.a.x, seg.b.y - seg.a.y))


def trace(
    rgb: np.ndarray,
    settings: TraceSettings | None = None,
    *,
    mode: TraceMode = TraceMode.EDGE,
    invert: bool | None = None,
    max_segment_frac: float = 0.33,
) -> TraceResult:
    """Trace an RGB image into simplified line geometry (pixel coordinates)."""
    settings = settings or TraceSettings()
    h, w = rgb.shape[:2]

    gray = preprocess(rgb, blur_ksize=settings.blur_ksize)
    binary = _binary_for_trace(gray, settings, mode, invert)

    # Scale-aware noise floor: drop contours shorter than a small fraction of the
    # image diagonal (kills speckle) but never below the user's min_segment_length.
    diag = float(np.hypot(w, h))
    min_arc = max(settings.min_segment_length, 0.01 * diag)
    contours = find_contours(binary, min_arc_length=min_arc)

    # Sort by perimeter (most significant first) so that, if the hard cap trims the
    # list, we keep the large defining shapes and drop tiny specks — never whole
    # regions by accident of contour order.
    contours.sort(key=lambda c: cv2.arcLength(c.reshape(-1, 1, 2), True), reverse=True)

    simplified = simplify_contours(contours, settings.detail, closed=True)
    segments = contours_to_segments(simplified, closed=True)

    # Drop spurious long chords: coarse simplification of large Canny contours can
    # emit a segment that jumps across the image (cutting through empty interior).
    # Real artwork edges are short, so a segment longer than a large fraction of the
    # diagonal is almost always an artifact.
    max_seg_len = max_segment_frac * diag
    segments = [s for s in segments if _segment_length(s) <= max_seg_len]

    truncated = False
    warnings: list[str] = []
    n = len(segments)
    if n > settings.warn_elements:
        msg = f"trace produced {n} segments (warn threshold {settings.warn_elements})"
        warnings.append(msg)
        log.warning(msg)
    if n > settings.max_elements:
        segments = segments[: settings.max_elements]
        truncated = True
        msg = f"trace truncated {n} -> {settings.max_elements} segments (hard cap)"
        warnings.append(msg)
        log.warning(msg)

    return TraceResult(
        segments=tuple(segments),
        width=w,
        height=h,
        contour_count=len(contours),
        truncated=truncated,
        warnings=tuple(warnings),
    )
