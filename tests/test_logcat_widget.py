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
