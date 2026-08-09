"""SHADING panel: Intensity slider with an On/Off badge (driven by intensity > 0)."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.domain.settings import ShadingSettings
from app.ui import theme
from app.ui.widgets.collapsible_section import CollapsibleSection
from app.ui.widgets.labelled_slider import LabelledSlider


class ShadingPanel(QWidget):
    changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        section = CollapsibleSection("SHADING")

        badge_row = QHBoxLayout()
        badge_row.addWidget(QLabel("Fills + hatch"))
        badge_row.addStretch(1)
        self._badge = QLabel("OFF")
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_row.addWidget(self._badge)
        holder = QWidget()
        holder.setLayout(badge_row)
        section.add_widget(holder)

        self._intensity = LabelledSlider("Intensity", 0, 100, 0)
        self._intensity.valueChanged.connect(self._on_intensity)
        section.add_widget(self._intensity)

        self._hatch = QCheckBox("Hatch mid-tones")
        self._hatch.setChecked(True)
        self._hatch.stateChanged.connect(lambda _s: self.changed.emit())
        section.add_widget(self._hatch)

        layout.addWidget(section)
        self._update_badge(0)

    def _on_intensity(self, value: int) -> None:
        self._update_badge(value)
        self.changed.emit()

    def _update_badge(self, value: int) -> None:
        on = value > 0
        self._badge.setText("ON" if on else "OFF")
        color = theme.ACCENT if on else theme.TEXT_MUTED
        self._badge.setStyleSheet(
            f"color: #0b0d10; background-color: {color}; border-radius: 8px; padding: 1px 8px;"
        )

    def settings(self) -> ShadingSettings:
        return ShadingSettings(intensity=self._intensity.value(), hatch=self._hatch.isChecked())
