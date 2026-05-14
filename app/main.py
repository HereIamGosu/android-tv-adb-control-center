from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.core.settings_store import SettingsStore
from app.ui.dialogs.setup_wizard import SetupWizard
from app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    store = SettingsStore()
    doc = store.load()
    if not doc.settings.adb_path:
        wizard = SetupWizard(store)
        wizard.exec()
    window = MainWindow(store)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
