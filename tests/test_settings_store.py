from pathlib import Path

from app.core.device_profile import AppSettings, DeviceProfile
from app.core.settings_store import SettingsStore


def test_settings_store_roundtrip_profile_pair_port(tmp_path: Path) -> None:
    store = SettingsStore(tmp_path / "settings.json")
    profile = DeviceProfile.create(
        name="TV",
        ip="192.168.1.10",
        pair_port=37123,
        connect_port=5555,
        scrcpy_args="--max-size 1280",
        screenshot_dir=str(tmp_path),
    )

    store.save(AppSettings(adb_path="C:/adb.exe"), [profile])
    document = store.load()

    assert document.settings.adb_path == "C:/adb.exe"
    assert document.profiles[0].pair_port == 37123
    assert document.profiles[0].last_serial == "192.168.1.10:5555"


def test_settings_store_backs_up_corrupted_json(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text("{bad json", encoding="utf-8")
    store = SettingsStore(path)

    document = store.load()

    assert document.warning
    assert path.exists()
    assert list(tmp_path.glob("settings.json.corrupted.*.bak"))
