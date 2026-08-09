"""A slider with a title and a live value readout."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.ui.widgets.no_scroll import NoScrollSlider


class LabelledSlider(QWidget):
    """Title + value label above a horizontal slider. Emits ``valueChanged(int)``."""

    valueChanged = Signal(int)

    def __init__(
        self,
        title: str,
        minimum: int = 0,
        maximum: int = 100,
        value: int = 50,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QHBoxLayout()
        self._title = QLabel(title)
        self._value = QLabel(str(value))
        self._value.setObjectName("muted")
        self._value.setAlignment(Qt.AlignmentFlag.AlignRight)
        header.addWidget(self._title)
        header.addStretch(1)
        header.addWidget(self._value)
        layout.addLayout(header)

        self._slider = NoScrollSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(minimum, maximum)
        self._slider.setValue(value)
        self._slider.valueChanged.connect(self._on_changed)
        layout.addWidget(self._slider)

    def _on_changed(self, v: int) -> None:
        self._value.setText(str(v))
        self.valueChanged.emit(v)

    def value(self) -> int:
        return self._slider.value()

    def setValue(self, v: int) -> None:
        self._slider.setValue(v)
