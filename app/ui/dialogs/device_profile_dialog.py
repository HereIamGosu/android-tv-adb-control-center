from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.device_profile import DeviceProfile
from app.core.validators import validate_ip_or_host, validate_port


TEXT = {
    "en": {
        "title": "Device Profile",
        "name": "Name",
        "ip": "IP / hostname",
        "ip_hint": "Enter only the IP part. If TV shows 192.168.1.113:39631, enter 192.168.1.113.",
        "connect_port": "Connect port",
        "connect_hint": "Stable ADB TCP/IP port from the main Wireless Debugging screen. For many Android TV devices this is 5555.",
        "scrcpy_args": "scrcpy args",
        "screenshot_dir": "Screenshot folder",
        "browse": "Browse",
        "save": "Save",
        "cancel": "Cancel",
        "select_screenshots": "Select screenshot folder",
        "invalid_profile": "Invalid profile",
        "empty_name": "Profile name must not be empty.",
    },
    "ru": {
        "title": "Профиль устройства",
        "name": "Название",
        "ip": "IP / hostname",
        "ip_hint": "Вводи только IP. Если TV показывает 192.168.1.113:39631, введи 192.168.1.113.",
        "connect_port": "Connect port",
        "connect_hint": "Стабильный ADB TCP/IP порт с главного экрана Wireless Debugging. Для многих Android TV это 5555.",
        "scrcpy_args": "Аргументы scrcpy",
        "screenshot_dir": "Папка скриншотов",
        "browse": "Обзор",
        "save": "Сохранить",
        "cancel": "Отмена",
        "select_screenshots": "Выбери папку скриншотов",
        "invalid_profile": "Некорректный профиль",
        "empty_name": "Название профиля не должно быть пустым.",
    },
}


class DeviceProfileDialog(QDialog):
    def __init__(
        self,
        profile: DeviceProfile | None = None,
        language: str = "en",
        parent=None,
    ):
        super().__init__(parent)
        self.language = language if language in TEXT else "en"
        self.setWindowTitle(self._t("title"))
        self.profile = profile
        self.name_edit = QLineEdit(profile.name if profile else "")
        self.ip_edit = QLineEdit(profile.ip if profile else "")
        self.ip_edit.setPlaceholderText("Example: 192.168.1.113")
        self.connect_port_edit = QLineEdit(
            str(profile.connect_port) if profile and profile.connect_port else ""
        )
        self.connect_port_edit.setPlaceholderText("Example: 5555")
        self.scrcpy_args_edit = QLineEdit(profile.scrcpy_args if profile else "")
        self.screenshot_dir_edit = QLineEdit(
            profile.screenshot_dir
            if profile
            else str(Path.home() / "Pictures" / "ADBTVControlCenter")
        )

        form = QFormLayout()
        form.addRow(self._t("name"), self.name_edit)
        form.addRow(self._t("ip"), self._field_with_hint(self.ip_edit, self._t("ip_hint")))
        form.addRow(
            self._t("connect_port"),
            self._field_with_hint(self.connect_port_edit, self._t("connect_hint")),
        )
        form.addRow(self._t("scrcpy_args"), self.scrcpy_args_edit)
        form.addRow(self._t("screenshot_dir"), self._dir_row())

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

    def device_profile(self) -> DeviceProfile:
        name = self.name_edit.text().strip()
        ip = self.ip_edit.text().strip()
        connect_port = (
            int(self.connect_port_edit.text().strip())
            if self.connect_port_edit.text().strip()
            else None
        )
        if self.profile:
            self.profile.name = name
            self.profile.ip = ip
            self.profile.connect_port = connect_port
            self.profile.last_serial = f"{ip}:{connect_port}" if connect_port else None
            self.profile.scrcpy_args = self.scrcpy_args_edit.text().strip()
            self.profile.screenshot_dir = self.screenshot_dir_edit.text().strip()
            return self.profile
        return DeviceProfile.create(
            name=name,
            ip=ip,
            connect_port=connect_port,
            scrcpy_args=self.scrcpy_args_edit.text().strip(),
            screenshot_dir=self.screenshot_dir_edit.text().strip(),
        )

    def _dir_row(self) -> QHBoxLayout:
        button = QPushButton(self._t("browse"))
        button.clicked.connect(self._browse_dir)
        row = QHBoxLayout()
        row.addWidget(self.screenshot_dir_edit)
        row.addWidget(button)
        return row

    def _browse_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, self._t("select_screenshots"))
        if path:
            self.screenshot_dir_edit.setText(path)

    def _field_with_hint(self, field: QLineEdit, hint: str) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(field)
        label = QLabel(hint)
        label.setWordWrap(True)
        label.setStyleSheet("color: #555;")
        layout.addWidget(label)
        return container

    def _validate_and_accept(self) -> None:
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, self._t("invalid_profile"), self._t("empty_name"))
            return
        for validator, value in (
            (validate_ip_or_host, self.ip_edit.text()),
            (validate_port, self.connect_port_edit.text()),
        ):
            is_valid, error = validator(value)
            if not is_valid:
                QMessageBox.warning(self, self._t("invalid_profile"), error)
                return
        self.accept()

    def _t(self, key: str) -> str:
        return TEXT[self.language][key]
