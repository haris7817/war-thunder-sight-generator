"""TRACE panel: quality preset, Detail slider, and a Re-trace button."""

from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from app.domain.settings import TracePreset, TraceSettings
from app.ui.panel_icons import refresh_icon, tracing_icon
from app.ui.panels.source_panel import field_label
from app.ui.widgets.chip_group import ChipGroup
from app.ui.widgets.collapsible_section import CollapsibleSection
from app.ui.widgets.labelled_slider import LabelledSlider


class TracePanel(QWidget):
    retraceRequested = Signal()
    cancelRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._busy = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        section = CollapsibleSection("Tracing", tracing_icon())

        section.add_widget(field_label("Quality preset"))
        self._preset = ChipGroup([("fast", "Fast"), ("balanced", "Balanced"), ("high", "High")])
        self._preset.selectionChanged.connect(self._on_preset)
        section.add_widget(self._preset)

        self._detail = LabelledSlider(
            "Detail", 0, 100, TraceSettings.from_preset(TracePreset.BALANCED).detail
        )
        section.add_widget(self._detail)

        self._button = QPushButton("Re-trace")
        self._button.setIcon(refresh_icon())
        self._button.setIconSize(QSize(18, 18))
        self._button.setMinimumHeight(38)
        self._button.clicked.connect(self._on_button)
        section.add_widget(self._button)

        for btn in self._preset.findChildren(QPushButton):
            if btn.text() == "Balanced":
                btn.setChecked(True)

        layout.addWidget(section)

    def _on_preset(self, key: str) -> None:
        self._detail.setValue(TraceSettings.from_preset(TracePreset(key)).detail)

    def _on_button(self) -> None:
        if self._busy:
            self.cancelRequested.emit()
        else:
            self.retraceRequested.emit()

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        self._button.setText("Cancel" if busy else "Re-trace")

    def settings(self) -> TraceSettings:
        return TraceSettings.from_preset(TracePreset(self._preset.selected())).with_detail(
            self._detail.value()
        )
