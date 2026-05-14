import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

_app = QApplication.instance() or QApplication([])

from unittest.mock import MagicMock
from app.ui.dialogs.device_selector_dialog import DeviceSelectorDialog
from app.core.device_profile import DeviceProfile


def _make_profile(name: str, ip: str, connect_port: int) -> DeviceProfile:
    return DeviceProfile(
        id=name.lower(),
        name=name,
        ip=ip,
        pair_port=None,
        connect_port=connect_port,
        last_serial=f"{ip}:{connect_port}",
        scrcpy_args="",
        screenshot_dir="",
        created_at="",
        updated_at="",
    )


def test_dialog_constructs_empty():
    adb = MagicMock()
    dlg = DeviceSelectorDialog([], [], adb, None)
    assert dlg is not None


def test_table_has_four_columns():
    adb = MagicMock()
    dlg = DeviceSelectorDialog([], [], adb, None)
    assert dlg.table.columnCount() == 4


def test_table_populated_with_devices():
    adb = MagicMock()
    profiles = [_make_profile("Xiaomi TV", "192.168.1.5", 5555)]
    devices = [("192.168.1.5:5555", "device")]
    dlg = DeviceSelectorDialog(profiles, devices, adb, None)
    assert dlg.table.rowCount() == 1


def test_profile_name_shown_when_serial_matches():
    adb = MagicMock()
    profiles = [_make_profile("Xiaomi TV", "192.168.1.5", 5555)]
    devices = [("192.168.1.5:5555", "device")]
    dlg = DeviceSelectorDialog(profiles, devices, adb, None)
    name_item = dlg.table.item(0, 0)
    assert name_item is not None
    assert name_item.text() == "Xiaomi TV"


def test_dash_shown_when_no_profile_matches():
    adb = MagicMock()
    devices = [("192.168.1.99:5555", "device")]
    dlg = DeviceSelectorDialog([], devices, adb, None)
    name_item = dlg.table.item(0, 0)
    assert name_item is not None
    assert name_item.text() == "—"


def test_selected_serial_is_none_initially():
    adb = MagicMock()
    dlg = DeviceSelectorDialog([], [], adb, None)
    assert dlg.selected_serial is None
