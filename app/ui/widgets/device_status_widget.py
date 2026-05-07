from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class DeviceStatusWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.status_label = QLabel("Not configured")
        self.serial_label = QLabel("Serial: -")
        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.serial_label)

    def set_status(self, status: str, serial: str | None = None) -> None:
        self.status_label.setText(status)
        self.serial_label.setText(f"Serial: {serial or '-'}")
