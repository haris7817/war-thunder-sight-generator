"""Orchestrate geometry -> validated .blk text -> atomic file write.

Pipeline: map each element from image-pixel space to sight units (applying the
artwork transform), enforce the element-count budget, render into the template's
drawLines/drawQuads blocks, and write atomically so a crash never leaves a
half-written sight file.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.blk.coordinate_mapper import CoordinateMapper
from app.blk.exporter import build_lines_body, build_quads_body
from app.blk.parser import SightTemplate, load_default_template
from app.domain.geometry import LineSegment, Point, Quad
from app.domain.settings import DEFAULT_MAX_ELEMENTS, DEFAULT_WARN_ELEMENTS
from app.domain.transform import ArtworkTransform
from app.infrastructure.filesystem import atomic_write_text
from app.infrastructure.logging_config import get_logger

log = get_logger("export")


@dataclass(frozen=True, slots=True)
class ExportResult:
    text: str
    line_count: int
    quad_count: int
    truncated: bool
    warnings: tuple[str, ...]

    @property
    def element_count(self) -> int:
        return self.line_count + self.quad_count


def _map_point(p: Point, mapper: CoordinateMapper, transform: ArtworkTransform) -> Point:
    sx, sy = mapper.to_sight_transformed(p.x, p.y, transform)
    return Point(sx, sy)


def map_segment(seg: LineSegment, mapper: CoordinateMapper, transform: ArtworkTransform) -> LineSegment:
    return LineSegment(
        _map_point(seg.a, mapper, transform),
        _map_point(seg.b, mapper, transform),
        source=seg.source,
    )


def map_quad(quad: Quad, mapper: CoordinateMapper, transform: ArtworkTransform) -> Quad:
    return Quad(
        _map_point(quad.tl, mapper, transform),
        _map_point(quad.tr, mapper, transform),
        _map_point(quad.br, mapper, transform),
        _map_point(quad.bl, mapper, transform),
        source=quad.source,
    )


def _enforce_budget(
    segments: list[LineSegment],
    quads: list[Quad],
    warn_elements: int,
    max_elements: int,
) -> tuple[list[LineSegment], list[Quad], bool, list[str]]:
    """Warn above ``warn_elements``; hard-cap total at ``max_elements``.

    Lines are kept first, then quads fill the remaining budget. Truncation is
    logged, never silent (per the research on silent sight-load failure).
    """
    warnings: list[str] = []
    total = len(segments) + len(quads)
    if total > warn_elements:
        msg = f"element count {total} exceeds warn threshold {warn_elements}"
        warnings.append(msg)
        log.warning(msg)

    if total <= max_elements:
        return segments, quads, False, warnings

    kept_lines = segments[:max_elements]
    remaining = max_elements - len(kept_lines)
    kept_quads = quads[: max(0, remaining)]
    msg = (
        f"element count {total} exceeds hard cap {max_elements}; "
        f"truncated to {len(kept_lines)} lines + {len(kept_quads)} quads"
    )
    warnings.append(msg)
    log.warning(msg)
    return kept_lines, kept_quads, True, warnings


def build_export(
    segments_px: list[LineSegment],
    quads_px: list[Quad],
    mapper: CoordinateMapper,
    transform: ArtworkTransform,
    template: SightTemplate | None = None,
    *,
    warn_elements: int = DEFAULT_WARN_ELEMENTS,
    max_elements: int = DEFAULT_MAX_ELEMENTS,
) -> ExportResult:
    """Full pipeline from image-pixel geometry to validated .blk text."""
    template = template or load_default_template()

    sight_lines = [map_segment(s, mapper, transform) for s in segments_px]
    sight_quads = [map_quad(q, mapper, transform) for q in quads_px]
    sight_lines, sight_quads, truncated, warnings = _enforce_budget(
        sight_lines, sight_quads, warn_elements, max_elements
    )

    text = render_sight_text(sight_lines, sight_quads, template)
    return ExportResult(
        text=text,
        line_count=len(sight_lines),
        quad_count=len(sight_quads),
        truncated=truncated,
        warnings=tuple(warnings),
    )


def render_sight_text(
    segments_sight: list[LineSegment],
    quads_sight: list[Quad],
    template: SightTemplate | None = None,
) -> str:
    """Render already-mapped (sight-unit) geometry into the template.

    Used directly by golden tests and the calibration demo, which build geometry in
    sight units and need no pixel mapping.
    """
    template = template or load_default_template()
    lines_body = build_lines_body(segments_sight)
    quads_body = build_quads_body(quads_sight)
    return template.render(lines_body, quads_body)


def write_sight_file(path: str | Path, text: str) -> Path:
    """Write sight text atomically (temp file + os.replace)."""
    p = Path(path)
    atomic_write_text(p, text)
    log.info("wrote sight file: %s (%d bytes)", p, len(text.encode("utf-8")))
    return p


def render_and_write_sight(
    segments_sight: list[LineSegment],
    quads_sight: list[Quad],
    out_path: str | Path,
    template: SightTemplate | None = None,
    *,
    warn_elements: int = DEFAULT_WARN_ELEMENTS,
    max_elements: int = DEFAULT_MAX_ELEMENTS,
) -> tuple[ExportResult, Path]:
    """Enforce budget, render already-mapped geometry, and write atomically.

    Convenience used by the calibration demo, which authors geometry directly in
    sight units.
    """
    template = template or load_default_template()
    lines, quads, truncated, warnings = _enforce_budget(
        list(segments_sight), list(quads_sight), warn_elements, max_elements
    )
    text = render_sight_text(lines, quads, template)
    path = write_sight_file(out_path, text)
    result = ExportResult(
        text=text,
        line_count=len(lines),
        quad_count=len(quads),
        truncated=truncated,
        warnings=tuple(warnings),
    )
    return result, path
