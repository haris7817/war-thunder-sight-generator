"""Dark theme: palette constants and a global stylesheet.

Colours match the approved design: near-black app chrome, slightly lighter panels,
a distinct canvas backdrop, one accent, and light text.
"""

from __future__ import annotations

# Palette
APP_BG = "#15181c"
PANEL_BG = "#1a1e23"
CANVAS_BG = "#22262b"
ACCENT = "#2f9ee6"
TEXT = "#dfe3e8"
TEXT_MUTED = "#8b9299"
BORDER = "#2b3037"
CONTROL_BG = "#262b31"
CONTROL_HOVER = "#2f363d"

# Layout metrics
RAIL_WIDTH = 56
PANEL_WIDTH = 296

STYLESHEET = f"""
QWidget {{
    background-color: {APP_BG};
    color: {TEXT};
    font-size: 13px;
}}
QLabel {{ background: transparent; }}
QLabel#muted {{ color: {TEXT_MUTED}; }}
QLabel#sectionTitle {{ color: {TEXT_MUTED}; font-weight: 600; letter-spacing: 1px; }}

QPushButton {{
    background-color: {CONTROL_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 12px;
    color: {TEXT};
}}
QPushButton:hover {{ background-color: {CONTROL_HOVER}; }}
QPushButton:pressed {{ background-color: {ACCENT}; color: #0b0d10; }}
QPushButton#accent {{ background-color: {ACCENT}; color: #0b0d10; border: none; font-weight: 600; }}
QPushButton#accent:hover {{ background-color: #47abe9; }}

/* Chip toggle buttons */
QPushButton#chip {{
    background-color: {CONTROL_BG};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 5px 14px;
}}
QPushButton#chip:checked {{
    background-color: {ACCENT};
    color: #0b0d10;
    border: 1px solid {ACCENT};
}}

QFrame#panel {{ background-color: {PANEL_BG}; border-left: 1px solid {BORDER}; }}
QFrame#rail {{ background-color: {PANEL_BG}; border-right: 1px solid {BORDER}; }}
QFrame#hline {{ background-color: {BORDER}; max-height: 1px; }}

QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 8px;
    color: {TEXT_MUTED};
}}
QToolButton:hover {{ background-color: {CONTROL_HOVER}; color: {TEXT}; }}
QToolButton:checked {{ background-color: {CONTROL_BG}; color: {ACCENT}; }}

QSlider::groove:horizontal {{
    height: 4px; background: {BORDER}; border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT}; width: 14px; margin: -6px 0; border-radius: 7px;
}}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}

QStatusBar {{ background-color: {PANEL_BG}; color: {TEXT_MUTED}; border-top: 1px solid {BORDER}; }}
QStatusBar::item {{ border: none; }}
"""


def apply_theme(app) -> None:
    """Apply the global stylesheet to a QApplication."""
    app.setStyleSheet(STYLESHEET)
