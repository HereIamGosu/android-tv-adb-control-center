from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class ScreenshotPreviewDialog(QDialog):
    def __init__(self, image_bytes: bytes, file_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Screenshot")
        self._file_path = file_path
        self._folder = str(Path(file_path).parent)
        self._build_ui(image_bytes, file_path)

    def _build_ui(self, image_bytes: bytes, file_path: str) -> None:
        layout = QVBoxLayout(self)

        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap()
        if image_bytes and pixmap.loadFromData(image_bytes):
            scaled = pixmap.scaled(480, 270, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._image_label.setPixmap(scaled)
        else:
            self._image_label.setText("Preview unavailable")
        layout.addWidget(self._image_label)

        filename_label = QLabel(Path(file_path).name)
        filename_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(filename_label)

        path_label = QLabel(file_path)
        path_label.setAlignment(Qt.AlignCenter)
        path_label.setWordWrap(True)
        layout.addWidget(path_label)

        buttons = QHBoxLayout()
        self._open_folder_button = QPushButton("Open folder")
        self._open_folder_button.clicked.connect(self._open_folder)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        buttons.addStretch()
        buttons.addWidget(self._open_folder_button)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

    def _open_folder(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(self._folder))
