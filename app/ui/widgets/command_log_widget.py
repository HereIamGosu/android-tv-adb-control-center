from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLabel, QPlainTextEdit, QWidget

from app.core.command_result import CommandResult


class CommandLogWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.command_label = QLabel("-")
        self.exit_code_label = QLabel("-")
        self.stdout_edit = QPlainTextEdit()
        self.stderr_edit = QPlainTextEdit()
        self.interpretation_edit = QPlainTextEdit()
        for edit in (self.stdout_edit, self.stderr_edit, self.interpretation_edit):
            edit.setReadOnly(True)
            edit.setMinimumHeight(70)

        layout = QFormLayout(self)
        layout.addRow("Command", self.command_label)
        layout.addRow("Exit code", self.exit_code_label)
        layout.addRow("stdout", self.stdout_edit)
        layout.addRow("stderr", self.stderr_edit)
        layout.addRow("Interpretation", self.interpretation_edit)

    def show_result(self, result: CommandResult) -> None:
        self.command_label.setText(result.command_text)
        self.exit_code_label.setText(
            "-" if result.exit_code is None else str(result.exit_code)
        )
        self.stdout_edit.setPlainText(result.stdout)
        self.stderr_edit.setPlainText(result.stderr)
        self.interpretation_edit.setPlainText(result.interpretation)
