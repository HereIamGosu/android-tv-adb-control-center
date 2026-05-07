from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


STATUS_LABELS = {
    "en": {"serial": "Serial"},
    "ru": {"serial": "Serial"},
}


class DeviceStatusWidget(QWidget):
    def __init__(self, language: str = "en", parent: QWidget | None = None):
        super().__init__(parent)
        self.status_label = QLabel("Not configured")
        self.serial_label = QLabel("Serial: -")
        self.language = language
        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.serial_label)

    def set_status(self, status: str, serial: str | None = None) -> None:
        self.status_label.setText(status)
        self.serial_label.setText(f"{STATUS_LABELS.get(self.language, STATUS_LABELS['en'])['serial']}: {serial or '-'}")

    def set_language(self, language: str) -> None:
        self.language = language
        current_status = self.status_label.text()
        current_serial = self.serial_label.text().split(":", 1)[1].strip() if ":" in self.serial_label.text() else "-"
        self.set_status(current_status, None if current_serial == "-" else current_serial)
