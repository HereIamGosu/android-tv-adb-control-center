from app.core.adb_runner import parse_adb_devices


def test_parse_adb_devices_states_and_details() -> None:
    output = """List of devices attached
192.168.1.45:45678 device product:sabrina model:Google_TV
192.168.1.46:33333 offline
emulator-5554 unauthorized
abc recovery
"""

    devices = parse_adb_devices(output)

    assert [(item.serial, item.state) for item in devices] == [
        ("192.168.1.45:45678", "device"),
        ("192.168.1.46:33333", "offline"),
        ("emulator-5554", "unauthorized"),
        ("abc", "unknown"),
    ]
    assert devices[0].details == "product:sabrina model:Google_TV"
