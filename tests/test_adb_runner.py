from pathlib import Path

from app.core.adb_runner import (
    APK_INSTALL_TIMEOUT_SECONDS,
    FAST_COMMAND_TIMEOUT_SECONDS,
    PAIR_CONNECT_TIMEOUT_SECONDS,
    SCREENSHOT_TIMEOUT_SECONDS,
    SHELL_COMMAND_TIMEOUT_SECONDS,
    ADBRunner,
)


class Completed:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def test_adb_runner_uses_argument_list_and_shell_false(monkeypatch) -> None:
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return Completed(stdout="ok")

    monkeypatch.setattr("app.core.adb_runner.subprocess.run", fake_run)

    result = ADBRunner(Path("adb.exe")).install_apk(
        "192.168.1.10:5555", Path("C:/tmp/app with space.apk")
    )

    command, kwargs = calls[0]
    assert command == [
        "adb.exe",
        "-s",
        "192.168.1.10:5555",
        "install",
        "C:\\tmp\\app with space.apk",
    ]
    assert kwargs["shell"] is False
    assert kwargs["capture_output"] is True
    assert result.status == "success"


def test_pairing_code_goes_to_stdin_not_command_text(monkeypatch) -> None:
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return Completed(stdout="Successfully paired")

    monkeypatch.setattr("app.core.adb_runner.subprocess.run", fake_run)

    result = ADBRunner(Path("adb.exe")).pair("192.168.1.10", 37123, "123456")

    assert calls[0][0] == ["adb.exe", "pair", "192.168.1.10:37123"]
    assert calls[0][1]["input"] == "123456\n"
    assert "123456" not in result.command_text


def test_screenshot_keeps_png_as_bytes(monkeypatch) -> None:
    png = b"\x89PNG\r\n\x1a\n"

    def fake_run(command, **kwargs):
        assert kwargs["text"] is False
        return Completed(stdout=png)

    monkeypatch.setattr("app.core.adb_runner.subprocess.run", fake_run)

    result = ADBRunner(Path("adb.exe")).screenshot_bytes("192.168.1.10:5555")

    assert result.binary_stdout == png
    assert result.stdout == "[binary stdout: 8 bytes]"


def test_adb_runner_uses_human_timeouts(monkeypatch) -> None:
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs["timeout"]))
        return Completed(stdout="ok")

    monkeypatch.setattr("app.core.adb_runner.subprocess.run", fake_run)
    runner = ADBRunner(Path("adb.exe"))

    runner.version()
    runner.devices()
    runner.pair("192.168.1.10", 37123, "123456")
    runner.connect("192.168.1.10", 5555)
    runner.disconnect("192.168.1.10:5555")
    runner.install_apk("192.168.1.10:5555", Path("C:/tmp/app.apk"))
    runner.shell("192.168.1.10:5555", "echo ok")
    runner.keyevent("192.168.1.10:5555", "KEYCODE_HOME")
    runner.getprop("192.168.1.10:5555", "ro.product.model")
    runner.screenshot_bytes("192.168.1.10:5555")

    assert [timeout for _command, timeout in calls] == [
        FAST_COMMAND_TIMEOUT_SECONDS,
        FAST_COMMAND_TIMEOUT_SECONDS,
        PAIR_CONNECT_TIMEOUT_SECONDS,
        PAIR_CONNECT_TIMEOUT_SECONDS,
        FAST_COMMAND_TIMEOUT_SECONDS,
        APK_INSTALL_TIMEOUT_SECONDS,
        SHELL_COMMAND_TIMEOUT_SECONDS,
        FAST_COMMAND_TIMEOUT_SECONDS,
        FAST_COMMAND_TIMEOUT_SECONDS,
        SCREENSHOT_TIMEOUT_SECONDS,
    ]
