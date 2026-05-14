import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from app.ui.widgets.logcat_widget import LogcatWidget

def app_instance():
    return QApplication.instance() or QApplication(sys.argv)

def test_widget_creates_with_english_labels():
    app_instance()
    w = LogcatWidget(language="en")
    assert w.filter_edit.placeholderText() == "Filter by tag"
    assert w.output_edit.isReadOnly()

def test_set_language_switches_to_russian():
    app_instance()
    w = LogcatWidget(language="en")
    w.set_language("ru")
    assert w.filter_edit.placeholderText() == "Фильтр по тегу"

from app.ui.widgets.logcat_widget import _level_color

def test_error_level_is_red():
    assert _level_color("E") == "#cc0000"

def test_warning_level_is_orange():
    assert _level_color("W") == "#cc6600"

def test_debug_level_is_gray():
    assert _level_color("D") == "#888888"

def test_verbose_level_is_gray():
    assert _level_color("V") == "#888888"

def test_info_level_returns_none():
    assert _level_color("I") is None

def test_unknown_level_returns_none():
    assert _level_color("X") is None
