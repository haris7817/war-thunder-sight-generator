"""Application entry point.

M1: opens a blank, titled window to prove the PySide6 toolchain works end to end.
The real main window, dark theme, canvas, and global exception hook arrive in M5.
"""

from __future__ import annotations

import sys

from app import __version__
from app.infrastructure.config import APP_NAME
from app.infrastructure.logging_config import configure_logging


def main() -> int:
    log = configure_logging()
    log.info("Starting %s v%s", APP_NAME, __version__)

    # Imported inside main so that importing app.main (e.g. in tooling) does not
    # require a Qt display to be available.
    from PySide6.QtWidgets import QApplication, QLabel, QMainWindow

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    window = QMainWindow()
    window.setWindowTitle(f"{APP_NAME}  v{__version__}")
    window.resize(1100, 720)

    placeholder = QLabel("War Thunder Sight Generator\n\nScaffold ready — UI arrives in M5.")
    placeholder.setContentsMargins(24, 24, 24, 24)
    window.setCentralWidget(placeholder)

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
