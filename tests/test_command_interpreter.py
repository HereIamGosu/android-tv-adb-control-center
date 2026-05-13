from datetime import datetime

from app.core.command_interpreter import CommandInterpreter
from app.core.command_result import CommandResult


def result(stdout: str = "", stderr: str = "", status: str = "error") -> CommandResult:
    return CommandResult(
        command=["adb"],
        command_text="adb",
        started_at=datetime.now(),
        finished_at=datetime.now(),
        exit_code=1 if status == "error" else 0,
        stdout=stdout,
        stderr=stderr,
        status=status,
    )


def test_interprets_protocol_fault_in_russian() -> None:
    message = CommandInterpreter("ru").interpret(result(stderr="protocol fault"))
    assert "неправильный порт" in message
    assert "adb pair" in message
    assert "adb connect" in message


def test_interprets_install_signature_error() -> None:
    message = CommandInterpreter("ru").interpret(
        result(stderr="INSTALL_FAILED_UPDATE_INCOMPATIBLE")
    )
    assert "другой подписью" in message


def test_interprets_timeout() -> None:
    message = CommandInterpreter("en").interpret(result(status="timeout"))
    assert "did not finish in time" in message
