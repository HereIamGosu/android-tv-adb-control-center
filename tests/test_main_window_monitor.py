import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from app.core.device_profile import AppSettings
from app.core.settings_store import SettingsDocument, SettingsStore
from app.ui.main_window import MainWindow


class MemoryStore(SettingsStore):
    def __init__(self, settings: AppSettings):
        self._settings = settings
        self.saved = []

    def load(self) -> SettingsDocument:
        return SettingsDocument(settings=self._settings, profiles=[])

    def save(self, settings, profiles) -> None:
        self.saved.append((settings, profiles))


def app_instance():
    return QApplication.instance() or QApplication(sys.argv)


def run_until(condition, timeout_ms=2000):
    app = app_instance()
    done = [False]
    t = QTimer()
    t.setSingleShot(True)
    t.timeout.connect(lambda: done.__setitem__(0, True))
    t.start(timeout_ms)
    while not condition() and not done[0]:
        app.processEvents()


def test_monitor_timer_exists_and_is_inactive_on_startup():
    app_instance()
    w = MainWindow(MemoryStore(AppSettings(adb_path="adb.exe", language="en")))
    assert hasattr(w, "_monitor_timer")
    assert not w._monitor_timer.isActive()
    w.close()


def test_monitor_timer_starts_when_device_connected_set_true():
    app_instance()
    w = MainWindow(MemoryStore(AppSettings(adb_path="adb.exe", language="en")))
    w.device_connected = True
    w.current_serial = "192.168.1.1:5555"
    w._start_monitor()
    assert w._monitor_timer.isActive()
    w._stop_monitor()
    w.close()


def test_monitor_timer_stops_after_stop_monitor():
    app_instance()
    w = MainWindow(MemoryStore(AppSettings(adb_path="adb.exe", language="en")))
    w._start_monitor()
    w._stop_monitor()
    assert not w._monitor_timer.isActive()
    w.close()
