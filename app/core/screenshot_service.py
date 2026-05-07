from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.core.adb_runner import ADBRunner
from app.core.command_result import CommandResult


class ScreenshotService:
    def __init__(self, adb_runner: ADBRunner):
        self.adb_runner = adb_runner

    def capture(
        self, serial: str, output_dir: Path
    ) -> tuple[CommandResult, Path | None]:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = (
            output_dir
            / f"screenshot_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
        )
        result = self.adb_runner.screenshot_bytes(serial)
        if result.status != "success":
            return result, None
        data = result.binary_stdout or b""
        if not data:
            result.status = "error"
            result.stderr = "screencap returned empty stdout"
            result.interpretation = "ADB не вернул PNG-данные скриншота."
            return result, None
        output_path.write_bytes(data)
        result.stdout = str(output_path)
        result.interpretation = f"Скриншот сохранён: {output_path}"
        return result, output_path
