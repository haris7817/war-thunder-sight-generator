"""SOURCE panel: import an image and choose the threshold method/level."""

from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from app.ui.panel_icons import source_icon, upload_icon
from app.ui.widgets.chip_group import ChipGroup
from app.ui.widgets.collapsible_section import CollapsibleSection
from app.ui.widgets.labelled_slider import LabelledSlider


def field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("fieldLabel")
    return lbl


class SourcePanel(QWidget):
    importClicked = Signal()
    settingsChanged = Signal()  # method or threshold changed

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        section = CollapsibleSection("Source", source_icon())

        self._import_btn = QPushButton("Import PNG / JPG")
        self._import_btn.setIcon(upload_icon())
        self._import_btn.setIconSize(QSize(18, 18))
        self._import_btn.setMinimumHeight(38)
        self._import_btn.clicked.connect(self.importClicked)
        section.add_widget(self._import_btn)

        section.add_widget(field_label("Threshold method"))
        self._method = ChipGroup(
            [("otsu", "Otsu"), ("global", "Global"), ("adaptive", "Adaptive")]
        )
        self._method.selectionChanged.connect(lambda _k: self.settingsChanged.emit())
        section.add_widget(self._method)

        self._threshold = LabelledSlider("Threshold", 0, 255, 128)
        self._threshold.valueChanged.connect(lambda _v: self.settingsChanged.emit())
        section.add_widget(self._threshold)

        layout.addWidget(section)

    def method(self) -> str:
        return self._method.selected()

    def threshold(self) -> int:
        return self._threshold.value()
