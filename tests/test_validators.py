from pathlib import Path

from app.core.validators import (
    validate_apk_path,
    validate_ip_or_host,
    validate_port,
    validate_serial,
)


def test_validate_ip_or_host_rejects_shell_metacharacters() -> None:
    assert validate_ip_or_host("192.168.1.1;reboot")[0] is False
    assert validate_ip_or_host("tv.local")[0] is True


def test_validate_port_range() -> None:
    assert validate_port("1")[0] is True
    assert validate_port("65535")[0] is True
    assert validate_port("0")[0] is False
    assert validate_port("65536")[0] is False


def test_validate_serial_rejects_metacharacters() -> None:
    assert validate_serial("192.168.1.10:5555")[0] is True
    assert validate_serial("192.168.1.10:5555 && adb shell")[0] is False


def test_validate_apk_path(tmp_path: Path) -> None:
    apk = tmp_path / "app.apk"
    apk.write_bytes(b"fake")
    txt = tmp_path / "app.txt"
    txt.write_text("fake", encoding="utf-8")

    assert validate_apk_path(str(apk))[0] is True
    assert validate_apk_path(str(txt))[0] is False
