from __future__ import annotations

from pathlib import Path

from app.core.adb_runner import ADBRunner
from app.core.command_result import CommandResult
from app.core.validators import validate_apk_path


class APKInstallService:
    def __init__(self, adb_runner: ADBRunner):
        self.adb_runner = adb_runner

    def install(self, serial: str, apk_path: Path) -> CommandResult:
        is_valid, error = validate_apk_path(str(apk_path))
        if not is_valid:
            raise ValueError(error)
        return self.adb_runner.install_apk(serial, apk_path)
