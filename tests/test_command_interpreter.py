from __future__ import annotations

from datetime import datetime

from app.core.command_interpreter import CommandInterpreter
from app.core.command_result import CommandResult


def make_result(stdout: str = "", stderr: str = "", status: str = "error") -> CommandResult:
    return CommandResult(
        command=["adb"],
        command_text="adb",
        started_at=datetime.now(),
        finished_at=datetime.now(),
        exit_code=1 if status == "error" else 0,
        stdout=stdout,
        stderr=stderr,
        status=status,  # type: ignore[arg-type]
    )


def test_interprets_failed_to_connect() -> None:
    result = make_result(stderr="adb: failed to connect to 192.168.1.45:45678")
    assert "ADB не смог подключиться" in CommandInterpreter().interpret(result)


def test_interprets_install_signature_error() -> None:
    result = make_result(stdout="Failure [INSTALL_FAILED_UPDATE_INCOMPATIBLE]")
    assert "другой подписью" in CommandInterpreter().interpret(result)


def test_success_message() -> None:
    result = make_result(stdout="OK", status="success")
    assert CommandInterpreter().interpret(result) == "Команда выполнена успешно."
