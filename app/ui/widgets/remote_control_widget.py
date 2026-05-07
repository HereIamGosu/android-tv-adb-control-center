from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QPushButton, QWidget


KEY_BUTTONS = [
    ("Up", "KEYCODE_DPAD_UP", 0, 1),
    ("Left", "KEYCODE_DPAD_LEFT", 1, 0),
    ("OK", "KEYCODE_DPAD_CENTER", 1, 1),
    ("Right", "KEYCODE_DPAD_RIGHT", 1, 2),
    ("Down", "KEYCODE_DPAD_DOWN", 2, 1),
    ("Back", "KEYCODE_BACK", 3, 0),
    ("Home", "KEYCODE_HOME", 3, 1),
    ("Menu", "KEYCODE_MENU", 3, 2),
    ("Volume Up", "KEYCODE_VOLUME_UP", 4, 0),
    ("Volume Down", "KEYCODE_VOLUME_DOWN", 4, 1),
    ("Power", "KEYCODE_POWER", 4, 2),
]


class RemoteControlWidget(QWidget):
    keyevent_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.buttons: list[QPushButton] = []
        layout = QGridLayout(self)
        for label, keycode, row, column in KEY_BUTTONS:
            button = QPushButton(label)
            button.clicked.connect(
                lambda checked=False, code=keycode: self.keyevent_requested.emit(code)
            )
            layout.addWidget(button, row, column)
            self.buttons.append(button)

    def set_controls_enabled(self, enabled: bool) -> None:
        for button in self.buttons:
            button.setEnabled(enabled)
