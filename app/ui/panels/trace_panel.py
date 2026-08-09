"""TRACE panel: preset chips, Detail slider, and a Re-trace button.

The Re-trace button doubles as a cancel affordance while a trace is running.
Selecting a preset snaps the Detail slider to that preset's detail.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from app.domain.settings import TracePreset, TraceSettings
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

        section = CollapsibleSection("TRACE")

        self._preset = ChipGroup([("fast", "Fast"), ("balanced", "Balanced"), ("high", "High")])
        self._preset.selectionChanged.connect(self._on_preset)
        section.add_widget(self._preset)

        self._detail = LabelledSlider("Detail", 0, 100, TraceSettings.from_preset(TracePreset.BALANCED).detail)
        section.add_widget(self._detail)

        self._button = QPushButton("Re-trace")
        self._button.setObjectName("accent")
        self._button.clicked.connect(self._on_button)
        section.add_widget(self._button)

        # Preselect Balanced so the panel matches the default detail.
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
