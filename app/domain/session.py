"""The immutable snapshot of everything an editing session holds.

``SessionState`` is a frozen value object. Edits produce a *new* state via the
``with_*`` helpers; in M6 the ``SessionStore`` owns the current state, swaps it on
each edit, and emits a change signal. Keeping state immutable makes undo (M7) and
change detection straightforward.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from app.domain.geometry import GeometrySource, LineSegment, Quad
from app.domain.settings import ShadingSettings, TraceSettings
from app.domain.transform import ArtworkTransform


@dataclass(frozen=True, slots=True)
class SessionState:
    image_path: str | None = None
    # (width, height) in pixels of the imported source image.
    image_size: tuple[int, int] | None = None
    lines: tuple[LineSegment, ...] = ()
    quads: tuple[Quad, ...] = ()
    trace_settings: TraceSettings = field(default_factory=TraceSettings)
    shading_settings: ShadingSettings = field(default_factory=ShadingSettings)
    transform: ArtworkTransform = field(default_factory=ArtworkTransform.identity)

    @property
    def element_count(self) -> int:
        return len(self.lines) + len(self.quads)

    def with_lines(self, lines: tuple[LineSegment, ...]) -> SessionState:
        return replace(self, lines=tuple(lines))

    def with_quads(self, quads: tuple[Quad, ...]) -> SessionState:
        return replace(self, quads=tuple(quads))

    def with_transform(self, transform: ArtworkTransform) -> SessionState:
        return replace(self, transform=transform)

    def replace_auto_geometry(
        self,
        lines: tuple[LineSegment, ...],
        quads: tuple[Quad, ...],
    ) -> SessionState:
        """Re-trace invariant (M7): swap in freshly generated auto geometry while
        preserving every user-authored (non-auto) element.

        Implemented here so the rule lives with the data it protects.
        """
        kept_lines = tuple(ls for ls in self.lines if not ls.source.is_auto)
        kept_quads = tuple(q for q in self.quads if not q.source.is_auto)
        new_auto_lines = tuple(ls for ls in lines if ls.source.is_auto)
        new_auto_quads = tuple(q for q in quads if q.source.is_auto)
        return replace(
            self,
            lines=kept_lines + new_auto_lines,
            quads=kept_quads + new_auto_quads,
        )

    def replace_lines_of_source(
        self, new_lines: tuple[LineSegment, ...], source: GeometrySource
    ) -> SessionState:
        """Replace only lines of ``source`` (e.g. re-trace swaps AUTO_TRACE, keeps rest)."""
        kept = tuple(ls for ls in self.lines if ls.source is not source)
        return replace(self, lines=kept + tuple(new_lines))

    def replace_quads_of_source(
        self, new_quads: tuple[Quad, ...], source: GeometrySource
    ) -> SessionState:
        kept = tuple(q for q in self.quads if q.source is not source)
        return replace(self, quads=kept + tuple(new_quads))

    def manual_geometry_count(self) -> int:
        manual_sources = (GeometrySource.MANUAL, GeometrySource.MANUAL_FILL)
        n = sum(1 for ls in self.lines if ls.source in manual_sources)
        n += sum(1 for q in self.quads if q.source in manual_sources)
        return n
