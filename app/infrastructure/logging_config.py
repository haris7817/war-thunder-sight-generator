"""Application logging setup: console + rotating file handler.

Logs go to ``logs/app.log`` beside the executable (frozen) or in the project root
(dev), rotating to keep disk usage bounded.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from app.infrastructure.filesystem import ensure_dir, user_data_dir

_CONFIGURED = False
_LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure root logging once (idempotent). Returns the app logger."""
    global _CONFIGURED
    root = logging.getLogger()
    if not _CONFIGURED:
        root.setLevel(level)
        formatter = logging.Formatter(_LOG_FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root.addHandler(console)

        log_dir = ensure_dir(user_data_dir() / "logs")
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

        _CONFIGURED = True

    return logging.getLogger("app")


def get_logger(name: str) -> logging.Logger:
    """Convenience accessor for a module-scoped logger under the ``app`` tree."""
    return logging.getLogger(f"app.{name}")
