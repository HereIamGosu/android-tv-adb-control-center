from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QPushButton, QWidget


KEY_BUTTONS = [
    ("up", "KEYCODE_DPAD_UP", 0, 1),
    ("left", "KEYCODE_DPAD_LEFT", 1, 0),
    ("ok", "KEYCODE_DPAD_CENTER", 1, 1),
    ("right", "KEYCODE_DPAD_RIGHT", 1, 2),
    ("down", "KEYCODE_DPAD_DOWN", 2, 1),
    ("back", "KEYCODE_BACK", 3, 0),
    ("home", "KEYCODE_HOME", 3, 1),
    ("menu", "KEYCODE_MENU", 3, 2),
    ("volume_up", "KEYCODE_VOLUME_UP", 4, 0),
    ("volume_down", "KEYCODE_VOLUME_DOWN", 4, 1),
    ("power", "KEYCODE_POWER", 4, 2),
]


REMOTE_TRANSLATIONS = {
    "en": {
        "up": "Up",
        "left": "Left",
        "ok": "OK",
        "right": "Right",
        "down": "Down",
        "back": "Back",
        "home": "Home",
        "menu": "Menu",
        "volume_up": "Volume Up",
        "volume_down": "Volume Down",
        "power": "Power",
    },
    "ru": {
        "up": "Вверх",
        "left": "Влево",
        "ok": "OK",
        "right": "Вправо",
        "down": "Вниз",
        "back": "Назад",
        "home": "Домой",
        "menu": "Меню",
        "volume_up": "Громче",
        "volume_down": "Тише",
        "power": "Питание",
    },
}


class RemoteControlWidget(QWidget):
    keyevent_requested = Signal(str)

    def __init__(self, language: str = "en", parent: QWidget | None = None):
        super().__init__(parent)
        self.buttons: dict[str, QPushButton] = {}
        layout = QGridLayout(self)
        for label_key, keycode, row, column in KEY_BUTTONS:
            button = QPushButton()
            button.clicked.connect(
                lambda checked=False, code=keycode: self.keyevent_requested.emit(code)
            )
            layout.addWidget(button, row, column)
            self.buttons[label_key] = button
        self.set_language(language)

    def set_controls_enabled(self, enabled: bool) -> None:
        for button in self.buttons.values():
            button.setEnabled(enabled)

    def set_language(self, language: str) -> None:
        labels = REMOTE_TRANSLATIONS.get(language, REMOTE_TRANSLATIONS["en"])
        for label_key, button in self.buttons.items():
            button.setText(labels[label_key])
