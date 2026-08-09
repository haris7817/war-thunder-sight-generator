"""TRANSFORM panel: move / scale / rotate the artwork, with live canvas updates.

Values are in sight units (offset) / multiplier (scale) / degrees (rotation) and map
directly onto :class:`ArtworkTransform`. Every change emits ``transformChanged`` so the
canvas re-renders immediately and the export stays in sync.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.domain.transform import ArtworkTransform
from app.ui.widgets.collapsible_section import CollapsibleSection


class TransformPanel(QWidget):
    transformChanged = Signal(object)  # ArtworkTransform

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        section = CollapsibleSection("TRANSFORM")
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(8)

        self._offset_x = self._spin(-2.0, 2.0, 0.01, 0.0)
        self._offset_y = self._spin(-2.0, 2.0, 0.01, 0.0)
        self._scale = self._spin(0.05, 8.0, 0.05, 1.0)
        self._rotation = self._spin(-180.0, 180.0, 1.0, 0.0)

        form.addRow("Offset X", self._offset_x)
        form.addRow("Offset Y", self._offset_y)
        form.addRow("Scale", self._scale)
        form.addRow("Rotation", self._rotation)

        holder = QWidget()
        holder.setLayout(form)
        section.add_widget(holder)

        self._reset = QPushButton("Reset")
        self._reset.clicked.connect(self.reset)
        section.add_widget(self._reset)

        layout.addWidget(section)

        for spin in (self._offset_x, self._offset_y, self._scale, self._rotation):
            spin.valueChanged.connect(self._emit)

    @staticmethod
    def _spin(lo: float, hi: float, step: float, value: float) -> QDoubleSpinBox:
        s = QDoubleSpinBox()
        s.setRange(lo, hi)
        s.setSingleStep(step)
        s.setDecimals(3)
        s.setValue(value)
        return s

    def transform(self) -> ArtworkTransform:
        return ArtworkTransform(
            offset_x=self._offset_x.value(),
            offset_y=self._offset_y.value(),
            scale=self._scale.value(),
            rotation_deg=self._rotation.value(),
        )

    def _emit(self) -> None:
        self.transformChanged.emit(self.transform())

    def reset(self) -> None:
        for spin, val in (
            (self._offset_x, 0.0),
            (self._offset_y, 0.0),
            (self._scale, 1.0),
            (self._rotation, 0.0),
        ):
            spin.blockSignals(True)
            spin.setValue(val)
            spin.blockSignals(False)
        self._emit()
