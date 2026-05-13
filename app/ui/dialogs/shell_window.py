from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
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
from app.core.command_result import CommandResult


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


class ShellWorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class ShellCommandWorker(QRunnable):
    def __init__(self, callback: Callable[[], CommandResult]):
        super().__init__()
        self.setAutoDelete(False)
        self.callback = callback
        self.signals = ShellWorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            self.signals.finished.emit(self.callback())
        except Exception as exc:
            self.signals.failed.emit(str(exc))


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
        self.thread_pool = QThreadPool.globalInstance()
        self.command_running = False
        self._active_workers: set[ShellCommandWorker] = set()
        self.command_edit = QLineEdit()
        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(True)

        self.run_button = QPushButton(self._t("run"))
        self.run_button.clicked.connect(self._run_command)

        top = QHBoxLayout()
        top.addWidget(self.command_edit)
        top.addWidget(self.run_button)

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
        self.command_running = True
        self.run_button.setEnabled(False)
        self.output_edit.appendPlainText(f"> {command}")
        worker = ShellCommandWorker(lambda: self.adb_runner.shell(self.serial, command))
        self._active_workers.add(worker)
        worker.signals.finished.connect(
            lambda result, active_worker=worker: self._show_result(
                active_worker, result
            )
        )
        worker.signals.failed.connect(
            lambda message, active_worker=worker: self._show_error(
                active_worker, message
            )
        )
        self.thread_pool.start(worker)

    def _show_result(self, worker: ShellCommandWorker, result: CommandResult) -> None:
        self._active_workers.discard(worker)
        self.command_running = False
        self.run_button.setEnabled(True)
        self.output_edit.appendPlainText(result.stdout)
        if result.stderr:
            self.output_edit.appendPlainText(f"stderr:\n{result.stderr}")
        if result.interpretation:
            self.output_edit.appendPlainText(
                f"{self._t('interpretation')}:\n{result.interpretation}"
            )

    def _show_error(self, worker: ShellCommandWorker, message: str) -> None:
        self._active_workers.discard(worker)
        self.command_running = False
        self.run_button.setEnabled(True)
        self.output_edit.appendPlainText(f"error:\n{message}")

    def closeEvent(self, event) -> None:
        if self._active_workers:
            self.thread_pool.waitForDone(5000)
            self._active_workers.clear()
        super().closeEvent(event)

    def _t(self, key: str) -> str:
        return TEXT[self.language][key]
