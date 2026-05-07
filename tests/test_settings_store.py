from __future__ import annotations

from pathlib import Path

from app.core.device_profile import AppSettings, DeviceProfile
from app.core.settings_store import SettingsStore


def test_settings_store_save_and_load(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    store = SettingsStore(path)
    settings = AppSettings(adb_path="C:\\tools\\adb.exe", scrcpy_path="C:\\tools\\scrcpy.exe", default_screenshot_dir="C:\\shots")
    profile = DeviceProfile.create("Xiaomi TV Stick", "192.168.1.45", 37123, 45678, '--window-title "Xiaomi"', "C:\\shots")

    store.save(settings, [profile])
    document = store.load()

    assert document.settings.adb_path == settings.adb_path
    assert document.profiles[0].last_serial == "192.168.1.45:45678"


def test_settings_store_backs_up_corrupted_json(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text("{bad json", encoding="utf-8")
    document = SettingsStore(path).load()

    assert document.warning is not None
    assert path.exists()
    assert list(tmp_path.glob("settings.json.corrupted.*.bak"))
