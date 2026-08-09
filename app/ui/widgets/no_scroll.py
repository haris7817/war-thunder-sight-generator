"""Slider/spin-box variants that don't hijack the mouse wheel.

By default QSlider/QDoubleSpinBox consume wheel events to change their value, which
makes scrolling the surrounding panel inconsistent (the value jumps instead of the
panel scrolling). These variants ignore the wheel unless the control has focus, so
the event propagates to the scroll area and the panel scrolls smoothly. Click a
control first to adjust it with the wheel.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDoubleSpinBox, QSlider


class NoScrollSlider(QSlider):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event) -> None:
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NoScrollDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event) -> None:
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()
