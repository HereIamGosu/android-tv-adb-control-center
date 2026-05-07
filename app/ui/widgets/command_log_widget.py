from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLabel, QPlainTextEdit, QWidget

from app.core.command_result import CommandResult


LOG_TRANSLATIONS = {
    "en": {
        "command": "Command",
        "exit_code": "Exit code",
        "stdout": "stdout",
        "stderr": "stderr",
        "interpretation": "Interpretation",
    },
    "ru": {
        "command": "Команда",
        "exit_code": "Код выхода",
        "stdout": "stdout",
        "stderr": "stderr",
        "interpretation": "Пояснение",
    },
}


class CommandLogWidget(QWidget):
    def __init__(self, language: str = "en", parent: QWidget | None = None):
        super().__init__(parent)
        self.command_label = QLabel("-")
        self.exit_code_label = QLabel("-")
        self.stdout_edit = QPlainTextEdit()
        self.stderr_edit = QPlainTextEdit()
        self.interpretation_edit = QPlainTextEdit()
        for edit in (self.stdout_edit, self.stderr_edit, self.interpretation_edit):
            edit.setReadOnly(True)
            edit.setMinimumHeight(70)

        self.command_title = QLabel()
        self.exit_code_title = QLabel()
        self.stdout_title = QLabel()
        self.stderr_title = QLabel()
        self.interpretation_title = QLabel()

        self.layout = QFormLayout(self)
        self.layout.addRow(self.command_title, self.command_label)
        self.layout.addRow(self.exit_code_title, self.exit_code_label)
        self.layout.addRow(self.stdout_title, self.stdout_edit)
        self.layout.addRow(self.stderr_title, self.stderr_edit)
        self.layout.addRow(self.interpretation_title, self.interpretation_edit)
        self.set_language(language)

    def set_language(self, language: str) -> None:
        labels = LOG_TRANSLATIONS.get(language, LOG_TRANSLATIONS["en"])
        self.command_title.setText(labels["command"])
        self.exit_code_title.setText(labels["exit_code"])
        self.stdout_title.setText(labels["stdout"])
        self.stderr_title.setText(labels["stderr"])
        self.interpretation_title.setText(labels["interpretation"])

    def show_result(self, result: CommandResult) -> None:
        self.command_label.setText(result.command_text)
        self.exit_code_label.setText(
            "-" if result.exit_code is None else str(result.exit_code)
        )
        self.stdout_edit.setPlainText(result.stdout)
        self.stderr_edit.setPlainText(result.stderr)
        self.interpretation_edit.setPlainText(result.interpretation)
