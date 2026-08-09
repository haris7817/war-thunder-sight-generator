"""Pinned export footer: template selection + a prominent Export button.

The footer only expresses intent (``exportRequested``); the main window owns the save
dialog, the export service call, and the success toast.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFrame, QPushButton, QVBoxLayout, QWidget

from app.ui import theme


class ExportFooter(QWidget):
    exportRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(8)

        divider = QFrame()
        divider.setObjectName("hline")
        divider.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(divider)

        self._template = QComboBox()
        self._template.addItem("Default template", "default")
        layout.addWidget(self._template)

        self._export = QPushButton("Export .blk")
        self._export.setObjectName("accent")
        self._export.setMinimumHeight(38)
        self._export.clicked.connect(self.exportRequested)
        layout.addWidget(self._export)

        self.setStyleSheet(f"background-color: {theme.PANEL_BG};")

    def template(self) -> str:
        return self._template.currentData()
