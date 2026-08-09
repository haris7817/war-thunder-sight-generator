"""SOURCE panel: import an image and choose the threshold method/level.

This is the only fully-wired panel in M5 — enough to prove the interaction loop
(import -> live threshold preview on a background thread) is responsive.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from app.ui.widgets.chip_group import ChipGroup
from app.ui.widgets.collapsible_section import CollapsibleSection
from app.ui.widgets.labelled_slider import LabelledSlider


class SourcePanel(QWidget):
    importClicked = Signal()
    settingsChanged = Signal()  # method or threshold changed

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        section = CollapsibleSection("SOURCE")
        section.body().setSpacing(12)

        self._import_btn = QPushButton("Import image…")
        self._import_btn.setObjectName("accent")
        self._import_btn.clicked.connect(self.importClicked)
        section.add_widget(self._import_btn)

        self._method = ChipGroup(
            [("otsu", "Otsu"), ("global", "Global"), ("adaptive", "Adaptive")]
        )
        self._method.selectionChanged.connect(lambda _k: self.settingsChanged.emit())
        section.add_widget(self._method)

        self._threshold = LabelledSlider("Threshold", 0, 255, 128)
        self._threshold.valueChanged.connect(lambda _v: self.settingsChanged.emit())
        section.add_widget(self._threshold)

        layout.addWidget(section)
        layout.addStretch(1)

    def method(self) -> str:
        return self._method.selected()

    def threshold(self) -> int:
        return self._threshold.value()
