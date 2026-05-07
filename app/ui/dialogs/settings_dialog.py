from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.core.device_profile import AppSettings
from app.core.validators import validate_executable


TEXT = {
    "en": {
        "title": "Settings",
        "screenshot_dir": "Screenshot folder",
        "browse": "Browse",
        "save": "Save",
        "cancel": "Cancel",
        "select": "Select {name}",
        "select_screenshots": "Select screenshot folder",
        "invalid_path": "Invalid path",
    },
    "ru": {
        "title": "Настройки",
        "screenshot_dir": "Папка скриншотов",
        "browse": "Обзор",
        "save": "Сохранить",
        "cancel": "Отмена",
        "select": "Выбери {name}",
        "select_screenshots": "Выбери папку скриншотов",
        "invalid_path": "Некорректный путь",
    },
}


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, language: str = "en", parent=None):
        super().__init__(parent)
        self.language = language if language in TEXT else "en"
        self.setWindowTitle(self._t("title"))
        self.adb_path_edit = QLineEdit(settings.adb_path)
        self.scrcpy_path_edit = QLineEdit(settings.scrcpy_path)
        self.screenshot_dir_edit = QLineEdit(settings.default_screenshot_dir)

        form = QFormLayout()
        form.addRow("adb.exe", self._path_row(self.adb_path_edit, "adb.exe"))
        form.addRow("scrcpy.exe", self._path_row(self.scrcpy_path_edit, "scrcpy.exe"))
        form.addRow(self._t("screenshot_dir"), self._dir_row(self.screenshot_dir_edit))

        save_button = QPushButton(self._t("save"))
        cancel_button = QPushButton(self._t("cancel"))
        save_button.clicked.connect(self._validate_and_accept)
        cancel_button.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

    def settings(self) -> AppSettings:
        return AppSettings(
            adb_path=self.adb_path_edit.text().strip(),
            scrcpy_path=self.scrcpy_path_edit.text().strip(),
            default_screenshot_dir=self.screenshot_dir_edit.text().strip(),
        )

    def _path_row(self, edit: QLineEdit, expected_name: str) -> QHBoxLayout:
        button = QPushButton(self._t("browse"))
        button.clicked.connect(lambda: self._browse_file(edit, expected_name))
        row = QHBoxLayout()
        row.addWidget(edit)
        row.addWidget(button)
        return row

    def _dir_row(self, edit: QLineEdit) -> QHBoxLayout:
        button = QPushButton(self._t("browse"))
        button.clicked.connect(lambda: self._browse_dir(edit))
        row = QHBoxLayout()
        row.addWidget(edit)
        row.addWidget(button)
        return row

    def _browse_file(self, edit: QLineEdit, expected_name: str) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, self._t("select").format(name=expected_name), "", "Executable (*.exe)"
        )
        if path:
            edit.setText(path)

    def _browse_dir(self, edit: QLineEdit) -> None:
        path = QFileDialog.getExistingDirectory(self, self._t("select_screenshots"))
        if path:
            edit.setText(path)

    def _validate_and_accept(self) -> None:
        for path, expected_name in (
            (self.adb_path_edit.text().strip(), "adb.exe"),
            (self.scrcpy_path_edit.text().strip(), "scrcpy.exe"),
        ):
            is_valid, error = validate_executable(path, expected_name)
            if not is_valid:
                QMessageBox.warning(self, self._t("invalid_path"), error)
                return
        if not self.screenshot_dir_edit.text().strip():
            self.screenshot_dir_edit.setText(
                str(Path.home() / "Pictures" / "ADBTVControlCenter")
            )
        self.accept()

    def _t(self, key: str) -> str:
        return TEXT[self.language][key]
