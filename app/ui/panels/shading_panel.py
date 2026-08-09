"""SHADING panel: an On/Off pill in the header + Intensity slider and hatch toggle."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QPushButton, QVBoxLayout, QWidget

from app.domain.settings import ShadingSettings
from app.ui.panel_icons import shading_icon
from app.ui.widgets.collapsible_section import CollapsibleSection
from app.ui.widgets.labelled_slider import LabelledSlider

DEFAULT_ON_INTENSITY = 50


class ShadingPanel(QWidget):
    changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        section = CollapsibleSection("Shading", shading_icon())

        self._pill = QPushButton("OFF")
        self._pill.setObjectName("pill")
        self._pill.setCursor(self._pill.cursor())
        self._pill.clicked.connect(self._toggle_pill)
        section.set_header_widget(self._pill)

        self._intensity = LabelledSlider("Intensity", 0, 100, 0)
        self._intensity.valueChanged.connect(self._on_intensity)
        section.add_widget(self._intensity)

        self._hatch = QCheckBox("Hatch mid-tones")
        self._hatch.setChecked(True)
        self._hatch.stateChanged.connect(lambda _s: self.changed.emit())
        section.add_widget(self._hatch)

        layout.addWidget(section)
        self._refresh_pill()

    def _toggle_pill(self) -> None:
        # Turning on restores a sensible default intensity; off zeroes it.
        self._intensity.setValue(0 if self._intensity.value() > 0 else DEFAULT_ON_INTENSITY)

    def _on_intensity(self, _value: int) -> None:
        self._refresh_pill()
        self.changed.emit()

    def _refresh_pill(self) -> None:
        on = self._intensity.value() > 0
        self._pill.setText("ON" if on else "OFF")
        self._pill.setProperty("on", "true" if on else "false")
        self._pill.style().unpolish(self._pill)
        self._pill.style().polish(self._pill)

    def settings(self) -> ShadingSettings:
        return ShadingSettings(intensity=self._intensity.value(), hatch=self._hatch.isChecked())
