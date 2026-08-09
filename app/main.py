"""Application entry point: dark-themed main window with a global exception hook."""

from __future__ import annotations

import sys

from app import __version__
from app.infrastructure.config import APP_NAME
from app.infrastructure.logging_config import configure_logging

log = configure_logging()


def _install_exception_hook(app) -> None:
    """Log uncaught exceptions and show a dialog instead of silently dying."""
    from PySide6.QtWidgets import QMessageBox

    def hook(exc_type, exc_value, exc_tb):
        import traceback

        text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        log.critical("Unhandled exception:\n%s", text)
        try:
            QMessageBox.critical(None, "Unexpected error", str(exc_value))
        except Exception:  # noqa: BLE001 - never let the handler itself crash
            pass

    sys.excepthook = hook


def main() -> int:
    log.info("Starting %s v%s", APP_NAME, __version__)

    from PySide6.QtWidgets import QApplication

    from app.ui import theme
    from app.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    theme.apply_theme(app)
    _install_exception_hook(app)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
