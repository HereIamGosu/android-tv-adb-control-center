from __future__ import annotations

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QVBoxLayout, QWidget

LOGCAT_TRANSLATIONS = {
    "en": {
        "title": "Logcat",
        "filter_placeholder": "Filter by tag",
        "no_device": "No device connected",
    },
    "ru": {
        "title": "Logcat",
        "filter_placeholder": "Фильтр по тегу",
        "no_device": "Устройство не подключено",
    },
}

_MAX_LINES = 2000
_TRIM_TO = 1800


class LogcatWidget(QWidget):
    def __init__(self, language: str = "en", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._language = language
        self._process: QProcess | None = None
        self._serial: str = ""

        self.filter_label = QLabel()
        self.filter_edit = QLineEdit()

        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setMaximumBlockCount(0)  # managed manually

        filter_row = QHBoxLayout()
        filter_row.addWidget(self.filter_label)
        filter_row.addWidget(self.filter_edit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(filter_row)
        layout.addWidget(self.output_edit)

        self.set_language(language)

    def set_language(self, language: str) -> None:
        self._language = language
        t = LOGCAT_TRANSLATIONS.get(language, LOGCAT_TRANSLATIONS["en"])
        self.filter_label.setText(t["title"] + ":")
        self.filter_edit.setPlaceholderText(t["filter_placeholder"])

    def _t(self, key: str) -> str:
        t = LOGCAT_TRANSLATIONS.get(self._language, LOGCAT_TRANSLATIONS["en"])
        return t[key]
