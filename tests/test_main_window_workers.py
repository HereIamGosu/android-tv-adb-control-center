import os
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from app.core.device_profile import AppSettings
from app.core.settings_store import SettingsDocument, SettingsStore
from app.ui.main_window import MainWindow


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class MemoryStore(SettingsStore):
    def __init__(self, settings: AppSettings):
        self._settings = settings
        self.saved = []

    def load(self) -> SettingsDocument:
        return SettingsDocument(settings=self._settings, profiles=[])

    def save(self, settings, profiles) -> None:
        self.saved.append((settings, profiles))


def app_instance() -> QApplication:
    return QApplication.instance() or QApplication(sys.argv)


def run_until(condition, timeout_ms: int = 2000) -> None:
    app = app_instance()
    deadline = [False]
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(lambda: deadline.__setitem__(0, True))
    timer.start(timeout_ms)
    while not condition() and not deadline[0]:
        app.processEvents()
    assert condition()


def test_check_tools_missing_executables_finishes_without_crash() -> None:
    app_instance()
    window = MainWindow(
        MemoryStore(
            AppSettings(
                adb_path="missing-adb.exe",
                scrcpy_path="missing-scrcpy.exe",
                language="en",
            )
        )
    )

    window._check_tools()
    run_until(lambda: not window.operation_running)

    assert not window._active_workers
    assert "missing-scrcpy.exe --version" == window.log_widget.command_label.text()
    assert window.log_widget.stderr_edit.toPlainText()
    window.close()


def test_worker_callback_exception_is_reported_without_leaking_worker(monkeypatch) -> None:
    app_instance()
    messages = []
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda parent, title, message: messages.append((title, message)),
    )
    window = MainWindow(MemoryStore(AppSettings(adb_path="adb.exe", language="en")))

    def fail_callback(payload) -> None:
        raise RuntimeError("callback failed")

    window._run_worker(lambda: "payload", fail_callback, "failing callback")
    run_until(lambda: not window.operation_running)

    assert not window._active_workers
    assert messages == [("Error", "callback failed")]
    assert window.operation_label.text() == "Failed"
    window.close()
