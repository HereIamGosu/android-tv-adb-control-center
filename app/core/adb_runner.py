from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.core.command_interpreter import CommandInterpreter
from app.core.command_result import CommandResult

KNOWN_DEVICE_STATES = {"device", "offline", "unauthorized"}
FAST_COMMAND_TIMEOUT_SECONDS = 10
PAIR_CONNECT_TIMEOUT_SECONDS = 30
SHELL_COMMAND_TIMEOUT_SECONDS = 45
SCREENSHOT_TIMEOUT_SECONDS = 20
APK_INSTALL_TIMEOUT_SECONDS = 180


@dataclass(frozen=True)
class DeviceEntry:
    serial: str
    state: str
    details: str


def parse_adb_devices(output: str) -> list[DeviceEntry]:
    entries: list[DeviceEntry] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("List of devices attached"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        state = parts[1] if parts[1] in KNOWN_DEVICE_STATES else "unknown"
        entries.append(
            DeviceEntry(serial=parts[0], state=state, details=" ".join(parts[2:]))
        )
    return entries


class ADBRunner:
    def __init__(self, adb_path: Path, language: str = "ru"):
        self.adb_path = adb_path
        self.interpreter = CommandInterpreter(language)

    def version(self) -> CommandResult:
        return self._run(["version"], timeout=FAST_COMMAND_TIMEOUT_SECONDS)

    def devices(self) -> CommandResult:
        return self._run(["devices", "-l"], timeout=FAST_COMMAND_TIMEOUT_SECONDS)

    def pair(self, ip: str, port: int, pairing_code: str) -> CommandResult:
        return self._run(
            ["pair", f"{ip}:{port}"],
            input_text=pairing_code + "\n",
            timeout=PAIR_CONNECT_TIMEOUT_SECONDS,
        )

    def connect(self, ip: str, port: int) -> CommandResult:
        return self._run(
            ["connect", f"{ip}:{port}"], timeout=PAIR_CONNECT_TIMEOUT_SECONDS
        )

    def disconnect(self, serial: str | None = None) -> CommandResult:
        args = ["disconnect", serial] if serial else ["disconnect"]
        return self._run(args, timeout=FAST_COMMAND_TIMEOUT_SECONDS)

    def kill_server(self) -> CommandResult:
        return self._run(["kill-server"], timeout=FAST_COMMAND_TIMEOUT_SECONDS)

    def start_server(self) -> CommandResult:
        return self._run(["start-server"], timeout=FAST_COMMAND_TIMEOUT_SECONDS)

    def install_apk(self, serial: str, apk_path: Path) -> CommandResult:
        return self._run(
            ["-s", serial, "install", str(apk_path)],
            timeout=APK_INSTALL_TIMEOUT_SECONDS,
        )

    def shell(self, serial: str, command: str) -> CommandResult:
        return self._run(
            ["-s", serial, "shell", command], timeout=SHELL_COMMAND_TIMEOUT_SECONDS
        )

    def keyevent(self, serial: str, keycode: str) -> CommandResult:
        return self._run(
            ["-s", serial, "shell", "input", "keyevent", keycode],
            timeout=FAST_COMMAND_TIMEOUT_SECONDS,
        )

    def getprop(self, serial: str, prop: str) -> CommandResult:
        return self._run(
            ["-s", serial, "shell", "getprop", prop],
            timeout=FAST_COMMAND_TIMEOUT_SECONDS,
        )

    def screenshot_bytes(self, serial: str) -> CommandResult:
        return self._run(
            ["-s", serial, "exec-out", "screencap", "-p"],
            text=False,
            timeout=SCREENSHOT_TIMEOUT_SECONDS,
        )

    def _run(
        self,
        args: list[str],
        *,
        input_text: str | None = None,
        text: bool = True,
        timeout: int = 30,
    ) -> CommandResult:
        command = [str(self.adb_path), *args]
        command_text = " ".join(command)
        started_at = datetime.now()
        try:
            completed = subprocess.run(
                command,
                input=input_text,
                capture_output=True,
                text=text,
                timeout=timeout,
                shell=False,
            )
            finished_at = datetime.now()
            binary_stdout = (
                completed.stdout if isinstance(completed.stdout, bytes) else None
            )
            stdout = (
                f"[binary stdout: {len(binary_stdout)} bytes]"
                if binary_stdout is not None
                else _decode_output(completed.stdout)
            )
            stderr = _decode_output(completed.stderr)
            status = "success" if completed.returncode == 0 else "error"
            result = CommandResult(
                command=command,
                command_text=command_text,
                started_at=started_at,
                finished_at=finished_at,
                exit_code=completed.returncode,
                stdout=stdout,
                stderr=stderr,
                status=status,
                binary_stdout=binary_stdout,
            )
        except subprocess.TimeoutExpired as exc:
            result = CommandResult(
                command=command,
                command_text=command_text,
                started_at=started_at,
                finished_at=datetime.now(),
                exit_code=None,
                stdout=_decode_output(exc.stdout),
                stderr=_decode_output(exc.stderr),
                status="timeout",
            )
        except OSError as exc:
            result = CommandResult(
                command=command,
                command_text=command_text,
                started_at=started_at,
                finished_at=datetime.now(),
                exit_code=None,
                stdout="",
                stderr=str(exc),
                status="error",
            )
        result.interpretation = self.interpreter.interpret(result)
        return result


def _decode_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
