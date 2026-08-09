"""SessionStore: the single owner of the editing session's geometry, transform and
settings. It wraps the immutable :class:`SessionState`, swaps it on each edit, and
emits Qt signals so the canvas and panels stay in sync.

Centralising mutation here is what makes the re-trace invariant (M7: never delete
manual geometry) and single-level undo enforceable in one place.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from app.application.hit_testing import nearest_segment
from app.domain.geometry import GeometrySource, LineSegment, Point, Quad
from app.domain.session import SessionState
from app.domain.settings import ShadingSettings, TraceSettings
from app.domain.transform import ArtworkTransform


class SessionStore(QObject):
    geometryChanged = Signal()
    transformChanged = Signal()
    stateChanged = Signal()  # any change

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._state = SessionState()
        self._undo_state: SessionState | None = None  # single-level undo

    def _push_undo(self) -> None:
        self._undo_state = self._state

    def can_undo(self) -> bool:
        return self._undo_state is not None

    def undo(self) -> None:
        """Restore the state from before the last manual edit (single level)."""
        if self._undo_state is not None:
            restored, self._undo_state = self._undo_state, None
            self._set_state(restored, geometry=True)

    @property
    def state(self) -> SessionState:
        return self._state

    def _set_state(self, state: SessionState, *, geometry: bool = False, transform: bool = False) -> None:
        self._state = state
        if geometry:
            self.geometryChanged.emit()
        if transform:
            self.transformChanged.emit()
        self.stateChanged.emit()

    # --- source ---------------------------------------------------------------

    def set_source(self, image_path: str | None, image_size: tuple[int, int] | None) -> None:
        from dataclasses import replace

        self._set_state(replace(self._state, image_path=image_path, image_size=image_size))

    # --- geometry -------------------------------------------------------------

    def set_auto_geometry(
        self, lines: tuple[LineSegment, ...], quads: tuple[Quad, ...] = ()
    ) -> None:
        """Replace auto-generated geometry, preserving any manual elements (M7)."""
        self._set_state(self._state.replace_auto_geometry(lines, quads), geometry=True)

    def set_geometry(self, lines: tuple[LineSegment, ...], quads: tuple[Quad, ...]) -> None:
        self._set_state(
            self._state.with_lines(lines).with_quads(quads), geometry=True
        )

    def set_traced_lines(self, lines: tuple[LineSegment, ...]) -> None:
        """Re-trace: replace only AUTO_TRACE lines; keep manual + shading geometry."""
        self._set_state(
            self._state.replace_lines_of_source(lines, GeometrySource.AUTO_TRACE),
            geometry=True,
        )

    def set_shading(
        self, quads: tuple[Quad, ...], hatch_lines: tuple[LineSegment, ...] = ()
    ) -> None:
        """Replace only AUTO_SHADING geometry (fills + hatch); keep everything else."""
        state = self._state.replace_quads_of_source(quads, GeometrySource.AUTO_SHADING)
        state = state.replace_lines_of_source(hatch_lines, GeometrySource.AUTO_SHADING)
        self._set_state(state, geometry=True)

    # --- manual edits ---------------------------------------------------------

    def add_segment(self, a: Point, b: Point) -> None:
        """Add a user-drawn (MANUAL) line. Undoable."""
        self._push_undo()
        seg = LineSegment(a, b, source=GeometrySource.MANUAL)
        self._set_state(self._state.with_lines(self._state.lines + (seg,)), geometry=True)

    def erase_nearest(self, x: float, y: float, radius: float, *, record_undo: bool = True) -> bool:
        """Remove the single nearest line within ``radius`` of (x,y). Returns whether one
        was removed. Shading quads are never touched.

        ``record_undo`` is True on the first erase of a stroke (mouse-down) and False for
        subsequent drag erases, so undoing reverts the whole erase stroke at once.
        """
        seg = nearest_segment(self._state.lines, x, y, radius)
        if seg is None:
            return False
        if record_undo:
            self._push_undo()
        kept = tuple(ls for ls in self._state.lines if ls.id != seg.id)
        self._set_state(self._state.with_lines(kept), geometry=True)
        return True

    @property
    def lines(self) -> tuple[LineSegment, ...]:
        return self._state.lines

    @property
    def quads(self) -> tuple[Quad, ...]:
        return self._state.quads

    # --- transform ------------------------------------------------------------

    def set_transform(self, transform: ArtworkTransform) -> None:
        self._set_state(self._state.with_transform(transform), transform=True)

    @property
    def transform(self) -> ArtworkTransform:
        return self._state.transform

    def reset_transform(self) -> None:
        self.set_transform(ArtworkTransform.identity())

    # --- settings -------------------------------------------------------------

    def set_trace_settings(self, settings: TraceSettings) -> None:
        from dataclasses import replace

        self._set_state(replace(self._state, trace_settings=settings))

    def set_shading_settings(self, settings: ShadingSettings) -> None:
        from dataclasses import replace

        self._set_state(replace(self._state, shading_settings=settings))
