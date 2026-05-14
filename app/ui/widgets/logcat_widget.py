from __future__ import annotations

from PySide6.QtCore import QProcess
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
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

_LEVEL_COLORS: dict[str, str] = {
    "E": "#cc0000",
    "W": "#cc6600",
    "D": "#888888",
    "V": "#888888",
}


def _level_color(level: str) -> str | None:
    return _LEVEL_COLORS.get(level)


def _parse_level(line: str) -> str:
    parts = line.split()
    if len(parts) >= 5:
        return parts[4]
    return ""


class LogcatWidget(QWidget):
    def __init__(self, language: str = "en", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._language = language
        self._process: QProcess | None = None
        self._serial: str = ""
        self._started_once: bool = False

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

    def _append_line(self, line: str) -> None:
        tag_filter = self.filter_edit.text().strip().lower()
        if tag_filter and tag_filter not in line.lower():
            return

        level = _parse_level(line)
        color = _level_color(level)

        cursor = self.output_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        if color:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            cursor.setCharFormat(fmt)
            cursor.insertText(line + "\n")
            cursor.setCharFormat(QTextCharFormat())
        else:
            cursor.insertText(line + "\n")

        doc = self.output_edit.document()
        if doc.blockCount() > _MAX_LINES:
            trim_cursor = self.output_edit.textCursor()
            trim_cursor.movePosition(QTextCursor.MoveOperation.Start)
            trim_cursor.movePosition(
                QTextCursor.MoveOperation.Down,
                QTextCursor.MoveMode.KeepAnchor,
                doc.blockCount() - _TRIM_TO,
            )
            trim_cursor.removeSelectedText()

        self.output_edit.setTextCursor(cursor)
        self.output_edit.ensureCursorVisible()

    def start(self, adb_path: str, serial: str) -> None:
        self._serial = serial
        separator = "--- reconnected ---" if self._started_once else "--- started ---"
        self._started_once = True
        self._stop_process()
        self._append_line(separator)
        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._on_data)
        self._process.finished.connect(self._on_process_finished)
        self._process.start(adb_path, ["-s", serial, "logcat", "-v", "threadtime"])

    def stop(self) -> None:
        self._stop_process()
        self._append_line("--- stopped ---")

    def _stop_process(self) -> None:
        if self._process is not None:
            self._process.readyReadStandardOutput.disconnect()
            self._process.finished.disconnect()
            self._process.terminate()
            if not self._process.waitForFinished(1000):
                self._process.kill()
            self._process = None

    def _on_data(self) -> None:
        if self._process is None:
            return
        raw = self._process.readAllStandardOutput().data()
        text = raw.decode("utf-8", errors="replace")
        for line in text.splitlines():
            if line.strip():
                self._append_line(line)

    def _on_process_finished(self, exit_code: int, exit_status) -> None:
        self._append_line("--- logcat disconnected ---")
        self._process = None
