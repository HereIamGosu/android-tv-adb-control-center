from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.device_profile import AppSettings, DeviceProfile


@dataclass
class SettingsDocument:
    settings: AppSettings = field(default_factory=AppSettings)
    profiles: list[DeviceProfile] = field(default_factory=list)
    warning: str | None = None


class SettingsStore:
    def __init__(self, path: Path | None = None):
        self.path = path or default_settings_path()

    def load(self) -> SettingsDocument:
        if not self.path.exists():
            document = SettingsDocument()
            self.save(document.settings, document.profiles)
            return document
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            backup_path = self._backup_corrupted_file()
            document = SettingsDocument(
                warning=f"Повреждённый JSON сохранён как {backup_path}. Создан новый settings.json."
            )
            self.save(document.settings, document.profiles)
            return document
        settings = AppSettings.from_dict(data.get("settings", data))
        profiles = [DeviceProfile.from_dict(item) for item in data.get("profiles", [])]
        return SettingsDocument(settings=settings, profiles=profiles)

    def save(self, settings: AppSettings, profiles: list[DeviceProfile]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "settings": settings.to_dict(),
            "profiles": [profile.to_dict() for profile in profiles],
        }
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    def _backup_corrupted_file(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.path.with_name(f"{self.path.name}.corrupted.{timestamp}.bak")
        shutil.copy2(self.path, backup_path)
        return backup_path


def default_settings_path() -> Path:
    appdata = os.getenv("APPDATA")
    base_dir = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
    return base_dir / "ADBTVControlCenter" / "settings.json"
