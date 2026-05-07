from __future__ import annotations

import shlex
import subprocess
from datetime import datetime
from pathlib import Path

from app.core.command_interpreter import CommandInterpreter
from app.core.command_result import CommandResult


class ScrcpyRunner:
    def __init__(self, scrcpy_path: Path, language: str = "ru"):
        self.scrcpy_path = scrcpy_path
        self.interpreter = CommandInterpreter(language)

    def version(self) -> CommandResult:
        return self._run(["--version"])

    def launch(self, serial: str | None = None, extra_args: str = "") -> CommandResult:
        args = shlex.split(extra_args, posix=False) if extra_args.strip() else []
        selector = ["-s", serial] if serial else []
        command = [str(self.scrcpy_path), *selector, *args]
        return self._start(command)

    def launch_select_tcpip(self, extra_args: str = "") -> CommandResult:
        args = shlex.split(extra_args, posix=False) if extra_args.strip() else []
        command = [str(self.scrcpy_path), "--select-tcpip", *args]
        return self._start(command)

    def launch_tcpip(
        self, ip: str, port: int | None = None, extra_args: str = "", force: bool = False
    ) -> CommandResult:
        args = shlex.split(extra_args, posix=False) if extra_args.strip() else []
        address = f"{ip}:{port}" if port else ip
        prefix = "+" if force else ""
        command = [str(self.scrcpy_path), f"--tcpip={prefix}{address}", *args]
        return self._start(command)

    def _start(self, command: list[str]) -> CommandResult:
        command_text = " ".join(command)
        started_at = datetime.now()
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
            )
            result = CommandResult(
                command=command,
                command_text=command_text,
                started_at=started_at,
                finished_at=None,
                exit_code=process.pid,
                stdout=f"scrcpy process started, pid={process.pid}",
                stderr="",
                status="running",
                interpretation="scrcpy запущен в отдельном процессе.",
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

    def _run(self, args: list[str], timeout: int = 30) -> CommandResult:
        command = [str(self.scrcpy_path), *args]
        command_text = " ".join(command)
        started_at = datetime.now()
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,
            )
            result = CommandResult(
                command=command,
                command_text=command_text,
                started_at=started_at,
                finished_at=datetime.now(),
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                status="success" if completed.returncode == 0 else "error",
            )
        except subprocess.TimeoutExpired as exc:
            result = CommandResult(
                command=command,
                command_text=command_text,
                started_at=started_at,
                finished_at=datetime.now(),
                exit_code=None,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
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
