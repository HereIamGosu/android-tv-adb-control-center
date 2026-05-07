from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


CommandStatus = Literal["success", "error", "timeout", "running"]


@dataclass
class CommandResult:
    command: list[str]
    command_text: str
    started_at: datetime
    finished_at: datetime | None
    exit_code: int | None
    stdout: str
    stderr: str
    status: CommandStatus
    interpretation: str = ""
    binary_stdout: bytes | None = field(default=None, repr=False)
