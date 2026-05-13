from pathlib import Path

import pytest

from app.core.scrcpy_runner import SCRCPY_VERSION_TIMEOUT_SECONDS, ScrcpyRunner


class FakeProcess:
    pid = 4242


def test_scrcpy_launch_requires_serial() -> None:
    with pytest.raises(ValueError):
        ScrcpyRunner(Path("scrcpy.exe")).launch("")


def test_scrcpy_launch_uses_serial_and_argument_list(monkeypatch) -> None:
    calls = []

    def fake_popen(command, **kwargs):
        calls.append((command, kwargs))
        return FakeProcess()

    monkeypatch.setattr("app.core.scrcpy_runner.subprocess.Popen", fake_popen)

    result = ScrcpyRunner(Path("scrcpy.exe")).launch(
        "192.168.1.10:5555", "--max-size 1280"
    )

    assert calls[0][0] == [
        "scrcpy.exe",
        "-s",
        "192.168.1.10:5555",
        "--max-size",
        "1280",
    ]
    assert calls[0][1]["shell"] is False
    assert result.status == "running"


def test_scrcpy_version_uses_human_timeout(monkeypatch) -> None:
    calls = []

    class Completed:
        stdout = "scrcpy 3.0"
        stderr = ""
        returncode = 0

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return Completed()

    monkeypatch.setattr("app.core.scrcpy_runner.subprocess.run", fake_run)

    result = ScrcpyRunner(Path("scrcpy.exe")).version()

    assert calls[0][0] == ["scrcpy.exe", "--version"]
    assert calls[0][1]["timeout"] == SCRCPY_VERSION_TIMEOUT_SECONDS
    assert result.status == "success"
