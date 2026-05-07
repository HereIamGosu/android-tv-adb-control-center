from __future__ import annotations

import ipaddress
import re
from pathlib import Path


SHELL_METACHARACTERS = set("&|><;`$")
HOST_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$")
SERIAL_RE = re.compile(r"^[A-Za-z0-9_.:-]+$")


def validate_ip_or_host(value: str) -> tuple[bool, str | None]:
    candidate = value.strip()
    if not candidate:
        return False, "IP или hostname не должен быть пустым."
    if candidate != value or any(char.isspace() for char in candidate):
        return False, "IP или hostname не должен содержать пробелы."
    if any(char in SHELL_METACHARACTERS for char in candidate):
        return False, "IP или hostname содержит запрещённые shell-символы."
    try:
        ipaddress.IPv4Address(candidate)
        return True, None
    except ValueError:
        pass
    if not HOST_RE.fullmatch(candidate) or ".." in candidate:
        return False, "Hostname должен содержать только буквы, цифры, точки и дефисы."
    return True, None


def validate_port(value: str) -> tuple[bool, str | None]:
    candidate = value.strip()
    if not candidate:
        return False, "Порт не должен быть пустым."
    if not candidate.isdigit():
        return False, "Порт должен быть целым числом."
    port = int(candidate)
    if not 1 <= port <= 65535:
        return False, "Порт должен быть в диапазоне 1..65535."
    return True, None


def validate_executable(path: str, expected_name: str) -> tuple[bool, str | None]:
    candidate = Path(path)
    if not path:
        return False, f"Укажите путь к {expected_name}."
    if not candidate.exists() or not candidate.is_file():
        return False, "Файл не найден."
    if candidate.name.lower() != expected_name.lower():
        return False, f"Ожидался файл {expected_name}."
    return True, None


def validate_apk_path(path: str) -> tuple[bool, str | None]:
    candidate = Path(path)
    if not path:
        return False, "Укажите путь к APK."
    if not candidate.exists() or not candidate.is_file():
        return False, "APK-файл не найден."
    if candidate.suffix.lower() != ".apk":
        return False, "Файл должен иметь расширение .apk."
    return True, None


def validate_serial(value: str) -> tuple[bool, str | None]:
    candidate = value.strip()
    if not candidate:
        return False, "Serial не должен быть пустым."
    if any(char.isspace() for char in candidate):
        return False, "Serial не должен содержать пробелы."
    if any(char in SHELL_METACHARACTERS for char in candidate):
        return False, "Serial содержит запрещённые shell-символы."
    if not SERIAL_RE.fullmatch(candidate):
        return False, "Serial содержит недопустимые символы."
    return True, None
