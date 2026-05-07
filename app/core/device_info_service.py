from __future__ import annotations

from app.core.adb_runner import ADBRunner
from app.core.command_result import CommandResult


DEVICE_INFO_PROPS = {
    "manufacturer": "ro.product.manufacturer",
    "model": "ro.product.model",
    "android_version": "ro.build.version.release",
    "sdk": "ro.build.version.sdk",
}


class DeviceInfoService:
    def __init__(self, adb_runner: ADBRunner):
        self.adb_runner = adb_runner

    def read(self, serial: str) -> tuple[dict[str, str], list[CommandResult]]:
        info: dict[str, str] = {}
        results: list[CommandResult] = []
        for key, prop in DEVICE_INFO_PROPS.items():
            result = self.adb_runner.getprop(serial, prop)
            results.append(result)
            info[key] = result.stdout.strip() if result.status == "success" else ""
        return info, results
