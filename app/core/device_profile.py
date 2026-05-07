from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass
class DeviceProfile:
    id: str
    name: str
    ip: str
    pair_port: int | None
    connect_port: int | None
    last_serial: str | None
    scrcpy_args: str
    screenshot_dir: str
    created_at: str
    updated_at: str

    @classmethod
    def create(
        cls,
        name: str,
        ip: str,
        pair_port: int | None,
        connect_port: int | None,
        scrcpy_args: str,
        screenshot_dir: str,
    ) -> "DeviceProfile":
        now = datetime.now().isoformat(timespec="seconds")
        profile_id = "-".join(name.lower().split()) or "device-profile"
        last_serial = f"{ip}:{connect_port}" if ip and connect_port else None
        return cls(
            id=profile_id,
            name=name,
            ip=ip,
            pair_port=pair_port,
            connect_port=connect_port,
            last_serial=last_serial,
            scrcpy_args=scrcpy_args,
            screenshot_dir=screenshot_dir,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceProfile":
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            ip=str(data.get("ip", "")),
            pair_port=_optional_int(data.get("pair_port")),
            connect_port=_optional_int(data.get("connect_port")),
            last_serial=data.get("last_serial"),
            scrcpy_args=str(data.get("scrcpy_args", "")),
            screenshot_dir=str(data.get("screenshot_dir", "")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AppSettings:
    adb_path: str = ""
    scrcpy_path: str = ""
    default_screenshot_dir: str = ""
    theme: str = "system"
    last_device_profile_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppSettings":
        return cls(
            adb_path=str(data.get("adb_path", "")),
            scrcpy_path=str(data.get("scrcpy_path", "")),
            default_screenshot_dir=str(data.get("default_screenshot_dir", "")),
            theme=str(data.get("theme", "system")),
            last_device_profile_id=data.get("last_device_profile_id"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)
