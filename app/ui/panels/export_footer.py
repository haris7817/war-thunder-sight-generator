"""Pinned export footer: section label, template dropdown, prominent Export button.

Styled via the ``#footer`` object name in the global stylesheet — no local
setStyleSheet (a blanket local background bleeds onto the accent Export button).
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.ui.panel_icons import download_icon, export_icon


class ExportFooter(QFrame):
    exportRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("footer")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(6)
        icon = QLabel()
        icon.setPixmap(export_icon().pixmap(18, 18))
        title = QLabel("Export")
        title.setStyleSheet("font-weight: 600;")
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch(1)
        layout.addLayout(header)

        self._template = QComboBox()
        self._template.addItem("base_sight.blk", "default")
        layout.addWidget(self._template)

        self._export = QPushButton("Export .blk")
        self._export.setObjectName("accent")
        self._export.setIcon(download_icon())
        self._export.setIconSize(QSize(18, 18))
        self._export.setMinimumHeight(42)
        self._export.setCursor(Qt.CursorShape.PointingHandCursor)
        self._export.clicked.connect(self.exportRequested)
        layout.addWidget(self._export)

    def template(self) -> str:
        return self._template.currentData()

    def set_icon(self, icon: QIcon) -> None:  # reserved for future template icons
        self._export.setIcon(icon)
