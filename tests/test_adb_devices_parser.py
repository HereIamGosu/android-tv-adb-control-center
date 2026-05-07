from __future__ import annotations

from app.core.adb_runner import parse_adb_devices


def test_parse_adb_devices_l() -> None:
    output = """List of devices attached
192.168.1.45:45678 device product:foo model:Xiaomi_TV device:bar transport_id:3
emulator-5554 offline transport_id:1
"""
    entries = parse_adb_devices(output)

    assert len(entries) == 2
    assert entries[0].serial == "192.168.1.45:45678"
    assert entries[0].state == "device"
    assert "model:Xiaomi_TV" in entries[0].details
    assert entries[1].state == "offline"
