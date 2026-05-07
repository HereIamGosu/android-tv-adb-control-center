from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.adb_runner import ADBRunner


DANGEROUS_PATTERNS = (
    "pm uninstall",
    "cmd package uninstall",
    "settings put",
    "reboot bootloader",
    "reboot recovery",
    "wipe",
    "rm -rf",
    "dd",
    "su",
)

TEXT = {
    "en": {
        "run": "Run",
        "danger_title": "Potentially dangerous command",
        "danger_text": "This command can change or damage the device. Run it?",
        "interpretation": "interpretation",
    },
    "ru": {
        "run": "Выполнить",
        "danger_title": "Потенциально опасная команда",
        "danger_text": "Команда может изменить или повредить устройство. Выполнить её?",
        "interpretation": "пояснение",
    },
}


class ShellWindow(QWidget):
    def __init__(
        self,
        adb_runner: ADBRunner,
        serial: str,
        language: str = "en",
        parent=None,
    ):
        super().__init__(parent)
        self.language = language if language in TEXT else "en"
        self.setWindowTitle(f"ADB Shell - {serial}")
        self.adb_runner = adb_runner
        self.serial = serial
        self.command_edit = QLineEdit()
        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(True)

        run_button = QPushButton(self._t("run"))
        run_button.clicked.connect(self._run_command)

        top = QHBoxLayout()
        top.addWidget(self.command_edit)
        top.addWidget(run_button)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.output_edit)

    def _run_command(self) -> None:
        command = self.command_edit.text().strip()
        if not command:
            return
        lowered = command.lower()
        if any(pattern in lowered for pattern in DANGEROUS_PATTERNS):
            answer = QMessageBox.warning(
                self,
                self._t("danger_title"),
                self._t("danger_text"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        result = self.adb_runner.shell(self.serial, command)
        self.output_edit.appendPlainText(f"> {command}")
        self.output_edit.appendPlainText(result.stdout)
        if result.stderr:
            self.output_edit.appendPlainText(f"stderr:\n{result.stderr}")
        if result.interpretation:
            self.output_edit.appendPlainText(
                f"{self._t('interpretation')}:\n{result.interpretation}"
            )

    def _t(self, key: str) -> str:
        return TEXT[self.language][key]
