"""Application constants and persisted-setting keys.

QSettings-backed persistence (last import/export dirs, last-used settings) is wired
in M6; M1 defines the app identity constants and key names used there.
"""

from __future__ import annotations

APP_NAME = "War Thunder Sight Generator"
ORG_NAME = "haris7817"
# QSettings scope identifiers.
QSETTINGS_ORG = "haris7817"
QSETTINGS_APP = "WarThunderSightGenerator"

# Persisted-setting keys (used by M6).
KEY_LAST_IMPORT_DIR = "paths/last_import_dir"
KEY_LAST_EXPORT_DIR = "paths/last_export_dir"
KEY_LAST_TRACE_PRESET = "trace/last_preset"
KEY_LAST_DETAIL = "trace/last_detail"

# Default in-game install hint shown in docs/UI.
USER_SIGHTS_HINT = (
    r"Documents\My Games\WarThunder\Saves\<user ID>\production\UserSights"
    r"\<vehicle_id or all_tanks>\sight_1.blk"
)


def _qsettings():
    """A QSettings scoped to this app (Qt imported lazily so headless code is unaffected)."""
    from PySide6.QtCore import QSettings

    return QSettings(QSETTINGS_ORG, QSETTINGS_APP)


def get_setting(key: str, default: str = "") -> str:
    return str(_qsettings().value(key, default))


def set_setting(key: str, value: str) -> None:
    _qsettings().setValue(key, value)
