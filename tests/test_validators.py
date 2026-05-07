from __future__ import annotations

from pathlib import Path

from app.core.validators import validate_apk_path, validate_ip_or_host, validate_port, validate_serial


def test_validate_ip_or_host_accepts_ipv4_and_hostname() -> None:
    assert validate_ip_or_host("192.168.1.45") == (True, None)
    assert validate_ip_or_host("living-room-tv.local") == (True, None)


def test_validate_ip_or_host_rejects_empty_spaces_and_metacharacters() -> None:
    assert validate_ip_or_host("")[0] is False
    assert validate_ip_or_host("192.168.1.45 ")[0] is False
    assert validate_ip_or_host("192.168.1.45;rm")[0] is False


def test_validate_port_accepts_range() -> None:
    assert validate_port("1") == (True, None)
    assert validate_port("65535") == (True, None)


def test_validate_port_rejects_invalid_values() -> None:
    assert validate_port("0")[0] is False
    assert validate_port("65536")[0] is False
    assert validate_port("abc")[0] is False


def test_validate_apk_path(tmp_path: Path) -> None:
    apk = tmp_path / "app.apk"
    apk.write_bytes(b"fake")
    txt = tmp_path / "app.txt"
    txt.write_text("fake", encoding="utf-8")
    assert validate_apk_path(str(apk)) == (True, None)
    assert validate_apk_path(str(txt))[0] is False
    assert validate_apk_path(str(tmp_path / "missing.apk"))[0] is False


def test_validate_serial() -> None:
    assert validate_serial("192.168.1.45:45678") == (True, None)
    assert validate_serial("serial with space")[0] is False
    assert validate_serial("serial;rm")[0] is False
