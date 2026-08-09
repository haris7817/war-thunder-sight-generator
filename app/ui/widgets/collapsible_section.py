"""A titled panel section: a small icon + title header over a content area.

Clicking the header collapses/expands the content. The header can host a right-side
widget (used for the Shading On/Off pill).
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QToolButton, QVBoxLayout, QWidget


class CollapsibleSection(QWidget):
    def __init__(self, title: str, icon: QIcon | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(10)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(6)

        self._toggle = QToolButton()
        self._toggle.setObjectName("sectionHeader")
        self._toggle.setText(title)
        if icon is not None:
            self._toggle.setIcon(icon)
            self._toggle.setIconSize(QSize(18, 18))
            self._toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggle.setCheckable(True)
        self._toggle.setChecked(True)
        self._toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle.toggled.connect(self._on_toggled)
        header_row.addWidget(self._toggle)
        header_row.addStretch(1)

        self._header_right = QHBoxLayout()
        self._header_right.setContentsMargins(0, 0, 0, 0)
        header_row.addLayout(self._header_right)

        header = QWidget()
        header.setLayout(header_row)
        self._layout.addWidget(header)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(10)
        self._layout.addWidget(self._content)

    def body(self) -> QVBoxLayout:
        return self._content_layout

    def add_widget(self, widget: QWidget) -> None:
        self._content_layout.addWidget(widget)

    def set_header_widget(self, widget: QWidget) -> None:
        """Place a widget on the right side of the header row (e.g. an On/Off pill)."""
        self._header_right.addWidget(widget)

    def _on_toggled(self, expanded: bool) -> None:
        self._content.setVisible(expanded)
