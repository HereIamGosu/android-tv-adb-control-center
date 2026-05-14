import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QCheckBox, QLineEdit

_app = QApplication.instance() or QApplication([])

from unittest.mock import MagicMock
from app.ui.dialogs.setup_wizard import SetupWizard


def _make_store(adb_path: str = "") -> MagicMock:
    store = MagicMock()
    settings = MagicMock()
    settings.adb_path = adb_path
    settings.scrcpy_path = ""
    settings.default_screenshot_dir = ""
    doc = MagicMock()
    doc.settings = settings
    doc.profiles = []
    store.load.return_value = doc
    return store


def test_wizard_constructs():
    store = _make_store()
    wiz = SetupWizard(store)
    assert wiz is not None


def test_wizard_has_three_pages():
    store = _make_store()
    wiz = SetupWizard(store)
    assert len(wiz.pageIds()) == 3


def test_skip_scrcpy_checkbox_exists():
    store = _make_store()
    wiz = SetupWizard(store)
    page = wiz.page(1)  # page index 1 = scrcpy page
    checkboxes = page.findChildren(QCheckBox)
    assert checkboxes


def test_skip_scrcpy_disables_scrcpy_field():
    store = _make_store()
    wiz = SetupWizard(store)
    page = wiz.page(1)
    checkboxes = page.findChildren(QCheckBox)
    cb = checkboxes[0]
    fields = page.findChildren(QLineEdit)
    cb.setChecked(True)
    assert not fields[0].isEnabled()


def test_wizard_constructs_when_adb_already_set():
    store = _make_store(adb_path="C:/platform-tools/adb.exe")
    wiz = SetupWizard(store)
    assert wiz is not None
