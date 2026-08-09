"""SessionStore: the single owner of the editing session's geometry, transform and
settings. It wraps the immutable :class:`SessionState`, swaps it on each edit, and
emits Qt signals so the canvas and panels stay in sync.

Centralising mutation here is what makes the re-trace invariant (M7: never delete
manual geometry) and single-level undo enforceable in one place.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from app.domain.geometry import LineSegment, Quad
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
