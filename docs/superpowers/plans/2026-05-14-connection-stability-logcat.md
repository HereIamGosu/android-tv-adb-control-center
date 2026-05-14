# Connection Stability & Logcat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a QTimer-based connection monitor that auto-detects device drops, and an always-on LogcatWidget that streams `adb logcat` output inside the main window.

**Architecture:** `QTimer` (30 s) polls `adb devices -l` silently when connected; state changes drive `device_connected` and start/stop a new `LogcatWidget`. The widget owns a `QProcess` that streams `adb logcat -v threadtime`, color-codes lines by severity, and filters by tag. Both lifecycle events are managed from `MainWindow`.

**Tech Stack:** Python 3.x, PySide6 (`QTimer`, `QProcess`, `QPlainTextEdit`, `QTextCharFormat`), pytest + `QT_QPA_PLATFORM=offscreen`

---

## File Map

| Path | Action | Responsibility |
|------|--------|---------------|
| `app/ui/widgets/logcat_widget.py` | **Create** | `LogcatWidget` — QProcess, output display, tag filter, color formatting |
| `app/ui/widgets/__init__.py` | **Modify** | Export `LogcatWidget` |
| `app/ui/main_window.py` | **Modify** | Add QTimer monitor, integrate LogcatWidget, remove logcat stub button |
| `tests/test_logcat_widget.py` | **Create** | Unit tests for LogcatWidget |
| `tests/test_main_window_monitor.py` | **Create** | Integration tests for the connection monitor |

No changes to `app/core/` — existing APIs are used as-is.

---

## Task 1: Create LogcatWidget — skeleton + language support

**Files:**
- Create: `app/ui/widgets/logcat_widget.py`
- Create: `tests/test_logcat_widget.py`

- [ ] **Step 1: Write failing test for widget construction and language**

```python
# tests/test_logcat_widget.py
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
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/test_logcat_widget.py -v
```
Expected: `ImportError` or `AttributeError` — `LogcatWidget` does not exist yet.

- [ ] **Step 3: Implement LogcatWidget skeleton**

Create `app/ui/widgets/logcat_widget.py`:

```python
from __future__ import annotations

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QVBoxLayout, QWidget

LOGCAT_TRANSLATIONS = {
    "en": {
        "title": "Logcat",
        "filter_placeholder": "Filter by tag",
        "no_device": "No device connected",
    },
    "ru": {
        "title": "Logcat",
        "filter_placeholder": "Фильтр по тегу",
        "no_device": "Устройство не подключено",
    },
}

_MAX_LINES = 2000
_TRIM_TO = 1800


class LogcatWidget(QWidget):
    def __init__(self, language: str = "en", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._language = language
        self._process: QProcess | None = None

        self.filter_label = QLabel()
        self.filter_edit = QLineEdit()

        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setMaximumBlockCount(0)  # we manage manually

        filter_row = QHBoxLayout()
        filter_row.addWidget(self.filter_label)
        filter_row.addWidget(self.filter_edit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(filter_row)
        layout.addWidget(self.output_edit)

        self.set_language(language)

    def set_language(self, language: str) -> None:
        self._language = language
        t = LOGCAT_TRANSLATIONS.get(language, LOGCAT_TRANSLATIONS["en"])
        self.filter_label.setText(t["title"] + ":")
        self.filter_edit.setPlaceholderText(t["filter_placeholder"])

    def _t(self, key: str) -> str:
        t = LOGCAT_TRANSLATIONS.get(self._language, LOGCAT_TRANSLATIONS["en"])
        return t[key]
```

- [ ] **Step 4: Run test to verify it passes**

```
pytest tests/test_logcat_widget.py -v
```
Expected: both tests PASS.

- [ ] **Step 5: Commit**

```
git add app/ui/widgets/logcat_widget.py tests/test_logcat_widget.py
git commit -m "feat: add LogcatWidget skeleton with language support"
```

---

## Task 2: LogcatWidget — color formatting

**Files:**
- Modify: `app/ui/widgets/logcat_widget.py`
- Modify: `tests/test_logcat_widget.py`

- [ ] **Step 1: Write failing test for color formatting**

Add to `tests/test_logcat_widget.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_logcat_widget.py::test_error_level_is_red -v
```
Expected: `ImportError` — `_level_color` not defined.

- [ ] **Step 3: Add `_level_color` function and `_append_line` method**

Add to `app/ui/widgets/logcat_widget.py` (after imports, before class):

```python
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor

_LEVEL_COLORS: dict[str, str] = {
    "E": "#cc0000",
    "W": "#cc6600",
    "D": "#888888",
    "V": "#888888",
}


def _level_color(level: str) -> str | None:
    return _LEVEL_COLORS.get(level)


def _parse_level(line: str) -> str:
    """Extract level char from threadtime format: date time pid tid LEVEL tag: msg"""
    parts = line.split()
    if len(parts) >= 5:
        return parts[4]
    return ""
```

Add `_append_line` method to `LogcatWidget`:

```python
def _append_line(self, line: str) -> None:
    tag_filter = self.filter_edit.text().strip().lower()
    if tag_filter and tag_filter not in line.lower():
        return

    level = _parse_level(line)
    color = _level_color(level)

    cursor = self.output_edit.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)

    if color:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.insertText(line + "\n")
        cursor.setCharFormat(QTextCharFormat())  # reset
    else:
        cursor.insertText(line + "\n")

    # Trim buffer
    doc = self.output_edit.document()
    if doc.blockCount() > _MAX_LINES:
        trim_cursor = self.output_edit.textCursor()
        trim_cursor.movePosition(QTextCursor.MoveOperation.Start)
        trim_cursor.movePosition(
            QTextCursor.MoveOperation.Down,
            QTextCursor.MoveMode.KeepAnchor,
            doc.blockCount() - _TRIM_TO,
        )
        trim_cursor.removeSelectedText()

    self.output_edit.setTextCursor(cursor)
    self.output_edit.ensureCursorVisible()
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_logcat_widget.py -v
```
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```
git add app/ui/widgets/logcat_widget.py tests/test_logcat_widget.py
git commit -m "feat: add logcat line color formatting by severity level"
```

---

## Task 3: LogcatWidget — start/stop with QProcess

**Files:**
- Modify: `app/ui/widgets/logcat_widget.py`
- Modify: `tests/test_logcat_widget.py`

- [ ] **Step 1: Write failing tests for start/stop**

Add to `tests/test_logcat_widget.py`:

```python
from PySide6.QtCore import QTimer

def run_until(condition, timeout_ms=2000):
    app = app_instance()
    done = [False]
    t = QTimer()
    t.setSingleShot(True)
    t.timeout.connect(lambda: done.__setitem__(0, True))
    t.start(timeout_ms)
    while not condition() and not done[0]:
        app.processEvents()

def test_start_appends_separator():
    app_instance()
    w = LogcatWidget()
    w.start("adb", "192.168.1.1:5555")
    w.stop()
    text = w.output_edit.toPlainText()
    assert "--- started ---" in text

def test_stop_appends_stopped_separator():
    app_instance()
    w = LogcatWidget()
    w.start("adb", "192.168.1.1:5555")
    w.stop()
    text = w.output_edit.toPlainText()
    assert "--- stopped ---" in text

def test_second_start_appends_reconnected():
    app_instance()
    w = LogcatWidget()
    w.start("adb", "192.168.1.1:5555")
    w.stop()
    w.start("adb", "192.168.1.1:5555")
    w.stop()
    text = w.output_edit.toPlainText()
    assert "--- reconnected ---" in text
    assert "--- started ---" in text
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_logcat_widget.py::test_start_appends_separator -v
```
Expected: `AttributeError` — `start` not defined.

- [ ] **Step 3: Implement `start` and `stop` methods**

Add to `LogcatWidget` class in `app/ui/widgets/logcat_widget.py`:

```python
def start(self, adb_path: str, serial: str) -> None:
    self._serial = serial
    separator = "--- reconnected ---" if self._process is not None else "--- started ---"
    self._stop_process()

    self._append_line(separator)

    self._process = QProcess(self)
    self._process.readyReadStandardOutput.connect(self._on_data)
    self._process.finished.connect(self._on_process_finished)
    self._process.start(adb_path, ["-s", serial, "logcat", "-v", "threadtime"])

def stop(self) -> None:
    self._stop_process()
    self._append_line("--- stopped ---")

def _stop_process(self) -> None:
    if self._process is not None:
        self._process.readyReadStandardOutput.disconnect()
        self._process.finished.disconnect()
        self._process.terminate()
        if not self._process.waitForFinished(1000):
            self._process.kill()
        self._process = None

def _on_data(self) -> None:
    if self._process is None:
        return
    raw = self._process.readAllStandardOutput().data()
    text = raw.decode("utf-8", errors="replace")
    for line in text.splitlines():
        if line.strip():
            self._append_line(line)

def _on_process_finished(self, exit_code: int, exit_status) -> None:
    self._append_line("--- logcat disconnected ---")
    self._process = None
```

Also add `self._serial: str = ""` to `__init__` after `self._process: QProcess | None = None`.

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_logcat_widget.py -v
```
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```
git add app/ui/widgets/logcat_widget.py tests/test_logcat_widget.py
git commit -m "feat: implement logcat start/stop with QProcess streaming"
```

---

## Task 4: Export LogcatWidget and add translations to main_window

**Files:**
- Modify: `app/ui/widgets/__init__.py`
- Modify: `app/ui/main_window.py` (translations only)

- [ ] **Step 1: Export LogcatWidget**

Edit `app/ui/widgets/__init__.py`:

```python
"""Reusable UI widgets."""
from app.ui.widgets.logcat_widget import LogcatWidget

__all__ = ["LogcatWidget"]
```

- [ ] **Step 2: Add translation keys to TRANSLATIONS in main_window.py**

In `app/ui/main_window.py`, in the `"en"` dict, add after `"error"`:

```python
"logcat": "Logcat",
"logcat_filter": "Filter by tag",
"logcat_no_device": "No device connected",
```

In the `"ru"` dict, add after `"error"`:

```python
"logcat": "Logcat",
"logcat_filter": "Фильтр по тегу",
"logcat_no_device": "Устройство не подключено",
```

- [ ] **Step 3: Verify import works**

```
python -c "from app.ui.widgets import LogcatWidget; print('OK')"
```
Expected: `OK`

- [ ] **Step 4: Commit**

```
git add app/ui/widgets/__init__.py app/ui/main_window.py
git commit -m "feat: export LogcatWidget and add logcat translation keys"
```

---

## Task 5: Integrate LogcatWidget into MainWindow UI

**Files:**
- Modify: `app/ui/main_window.py`

- [ ] **Step 1: Add import and widget instantiation**

At the top of `app/ui/main_window.py`, add to existing imports:

```python
from app.ui.widgets.logcat_widget import LogcatWidget
```

In `MainWindow.__init__`, after `self._apply_enabled_state()`:

```python
# no new line needed — LogcatWidget added in _build_ui
```

In `_build_ui`, after the log group block (right column), add:

```python
self.logcat_widget = LogcatWidget(self.settings.language)
self.logcat_group = QGroupBox()
logcat_layout = QVBoxLayout(self.logcat_group)
logcat_layout.addWidget(self.logcat_widget)
right_column.addWidget(self.logcat_group, 1)
```

- [ ] **Step 2: Remove the stub logcat button**

In `_build_device_actions_group`, remove:
- `self.logcat_button = QPushButton()`
- `self.logcat_button.clicked.connect(lambda: QMessageBox.information(self, "Logcat", self._t("logcat_stub")))`
- `self.logcat_button` from the `for button in (...)` loop

In `_apply_enabled_state`, remove:
```python
self.logcat_button,
```
from the `for button in (...)` block that checks `adb_ready and can_use_device`.

In `_apply_language`, remove:
```python
self.logcat_button.setText(self._t("start_logcat"))
```

Also remove the `"logcat_stub"` key from both language dicts in `TRANSLATIONS`.

- [ ] **Step 3: Wire logcat title to `_apply_language`**

In `_apply_language`, add at the end:

```python
self.logcat_group.setTitle(self._t("logcat"))
self.logcat_widget.set_language(self.settings.language)
```

- [ ] **Step 4: Run existing tests to verify no regressions**

```
pytest tests/ -v
```
Expected: all previously passing tests still PASS.

- [ ] **Step 5: Commit**

```
git add app/ui/main_window.py
git commit -m "feat: integrate LogcatWidget into main window, remove stub logcat button"
```

---

## Task 6: Add QTimer connection monitor

**Files:**
- Modify: `app/ui/main_window.py`
- Create: `tests/test_main_window_monitor.py`

- [ ] **Step 1: Write failing tests for monitor**

Create `tests/test_main_window_monitor.py`:

```python
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from app.core.device_profile import AppSettings
from app.core.settings_store import SettingsDocument, SettingsStore
from app.ui.main_window import MainWindow


class MemoryStore(SettingsStore):
    def __init__(self, settings: AppSettings):
        self._settings = settings
        self.saved = []

    def load(self) -> SettingsDocument:
        return SettingsDocument(settings=self._settings, profiles=[])

    def save(self, settings, profiles) -> None:
        self.saved.append((settings, profiles))


def app_instance():
    return QApplication.instance() or QApplication(sys.argv)


def run_until(condition, timeout_ms=2000):
    app = app_instance()
    done = [False]
    t = QTimer()
    t.setSingleShot(True)
    t.timeout.connect(lambda: done.__setitem__(0, True))
    t.start(timeout_ms)
    while not condition() and not done[0]:
        app.processEvents()


def test_monitor_timer_exists_and_is_inactive_on_startup():
    app_instance()
    w = MainWindow(MemoryStore(AppSettings(adb_path="adb.exe", language="en")))
    assert hasattr(w, "_monitor_timer")
    assert not w._monitor_timer.isActive()
    w.close()


def test_monitor_timer_starts_when_device_connected_set_true():
    app_instance()
    w = MainWindow(MemoryStore(AppSettings(adb_path="adb.exe", language="en")))
    w.device_connected = True
    w.current_serial = "192.168.1.1:5555"
    w._start_monitor()
    assert w._monitor_timer.isActive()
    w._stop_monitor()
    w.close()


def test_monitor_timer_stops_after_stop_monitor():
    app_instance()
    w = MainWindow(MemoryStore(AppSettings(adb_path="adb.exe", language="en")))
    w._start_monitor()
    w._stop_monitor()
    assert not w._monitor_timer.isActive()
    w.close()
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_main_window_monitor.py -v
```
Expected: `AttributeError` — `_monitor_timer` / `_start_monitor` not defined.

- [ ] **Step 3: Add QTimer to MainWindow**

In `app/ui/main_window.py`, add `QTimer` to the PySide6 imports:

```python
from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal, Slot
```

In `MainWindow.__init__`, after `self._active_workers: set[CommandWorker] = set()`:

```python
self._monitor_timer = QTimer(self)
self._monitor_timer.setInterval(30_000)
self._monitor_timer.timeout.connect(self._monitor_tick)
self._monitoring_tick = False
```

Add these three methods to `MainWindow`:

```python
def _start_monitor(self) -> None:
    if not self._monitor_timer.isActive():
        self._monitor_timer.start()

def _stop_monitor(self) -> None:
    self._monitor_timer.stop()

def _monitor_tick(self) -> None:
    if self.operation_running or not self.current_serial:
        return
    self._monitoring_tick = True
    self._run_worker(
        lambda: self._adb_runner().devices(),
        self._after_monitor_tick,
        "monitor tick",
    )

def _after_monitor_tick(self, result) -> None:
    self._monitoring_tick = False
    self._update_devices_from_result(result)
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_main_window_monitor.py -v
```
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```
git add app/ui/main_window.py tests/test_main_window_monitor.py
git commit -m "feat: add QTimer connection monitor with silent tick"
```

---

## Task 7: Connect monitor and logcat to device lifecycle

**Files:**
- Modify: `app/ui/main_window.py`

- [ ] **Step 1: Start monitor and logcat after successful connect**

In `_after_connect`, after the block that sets `self.device_connected = True` and before `self._apply_enabled_state()`:

```python
if connected:
    # (existing lines)
    self.current_serial = serial
    self.device_connected = True
    profile = self._current_profile()
    if profile:
        profile.last_serial = serial
        self._save()
    self.device_status.set_status(self._status("connected"), serial)
    self._start_monitor()
    self.logcat_widget.start(self.settings.adb_path, serial)  # ADD THIS
```

- [ ] **Step 2: Stop monitor and logcat on disconnect**

In `_after_disconnect`, after `self.device_connected = False`:

```python
self._stop_monitor()
self.logcat_widget.stop()
```

- [ ] **Step 3: Stop monitor and logcat on state change to non-device in `_update_devices_from_result`**

In `_update_devices_from_result`, in the `elif` / `else` branches that set `device_connected = False`:

```python
elif self.current_serial and states.get(self.current_serial) == "offline":
    self.device_connected = False
    self._stop_monitor()
    self.logcat_widget.stop()
    self.device_status.set_status(self._status("offline"), self.current_serial)
elif self.current_serial and states.get(self.current_serial) == "unauthorized":
    self.device_connected = False
    self._stop_monitor()
    self.logcat_widget.stop()
    self.device_status.set_status(self._status("unauthorized"), self.current_serial)
else:
    self.device_connected = False
    self._stop_monitor()
    self.logcat_widget.stop()
    self.device_status.set_status(self._status("ready"), self.current_serial)
```

- [ ] **Step 4: Suppress log widget output during monitor tick**

In `_run_worker`, the `on_finished` callback is already routed through `_finish_worker`. The monitor tick uses `_after_monitor_tick` which calls `_update_devices_from_result` — this does NOT call `log_widget.show_result`, so command log is already quiet.

Verify by checking that `_after_monitor_tick` never calls `self._show_result` or `self._show_many_results`. It does not — no change needed.

- [ ] **Step 5: Run full test suite**

```
pytest tests/ -v
```
Expected: all tests PASS.

- [ ] **Step 6: Commit**

```
git add app/ui/main_window.py
git commit -m "feat: wire connection monitor and logcat to device connect/disconnect lifecycle"
```

---

## Task 8: Handle monitor tick errors silently

**Files:**
- Modify: `app/ui/main_window.py`

- [ ] **Step 1: Override error handling for monitor ticks**

Currently `_fail_worker` shows a `QMessageBox.critical` popup. Monitor tick failures (device dropped mid-poll) should be silent.

Add a `_monitoring_tick` guard in `_fail_worker`. Replace the current method:

```python
def _fail_worker(self, worker: CommandWorker, message: str) -> None:
    self.operation_running = False
    self._operation_text = ""
    self._active_workers.discard(worker)
    self.operation_label.setText(self._t("failed"))
    if self._monitoring_tick:
        self._monitoring_tick = False
        self._stop_monitor()
        self.logcat_widget.stop()
        self.device_connected = False
        self.device_status.set_status(self._status("offline"), self.current_serial)
        self._apply_enabled_state()
        return
    self._apply_enabled_state()
    QMessageBox.critical(self, "Error", message)
```

- [ ] **Step 2: Run full test suite**

```
pytest tests/ -v
```
Expected: all tests PASS.

- [ ] **Step 3: Commit**

```
git add app/ui/main_window.py
git commit -m "fix: silence monitor tick errors, set offline status on poll failure"
```

---

## Task 9: Tag filter wired to language and final polish

**Files:**
- Modify: `app/ui/main_window.py`

- [ ] **Step 1: Pass language to LogcatWidget on language change**

In `_apply_language`, the line added in Task 5 already calls `self.logcat_widget.set_language(self.settings.language)`. Verify it is present:

```python
self.logcat_group.setTitle(self._t("logcat"))
self.logcat_widget.set_language(self.settings.language)
```

If missing, add it.

- [ ] **Step 2: Handle closeEvent — stop monitor and logcat cleanly**

The existing `closeEvent` waits for workers with `self.thread_pool.waitForDone(5000)`. Add logcat and monitor cleanup before `super().closeEvent(event)`:

```python
def closeEvent(self, event) -> None:
    self._stop_monitor()
    self.logcat_widget.stop()
    if self._active_workers:
        self.thread_pool.waitForDone(5000)
        self._active_workers.clear()
    super().closeEvent(event)
```

- [ ] **Step 3: Run full test suite**

```
pytest tests/ -v
```
Expected: all tests PASS.

- [ ] **Step 4: Final commit**

```
git add app/ui/main_window.py
git commit -m "fix: clean up monitor and logcat on window close"
```

---

## Self-Review Checklist

- [x] **Spec: QTimer monitor** — Tasks 6, 7, 8 cover timer creation, lifecycle, silent errors
- [x] **Spec: LogcatWidget with QProcess** — Tasks 1–3 cover widget, colors, start/stop
- [x] **Spec: Auto-start on connect, stop on drop** — Task 7
- [x] **Spec: No log spam from ticks** — `_after_monitor_tick` never calls `show_result`
- [x] **Spec: Reconnected separator** — Task 3 (`start` checks `_process is not None`)
- [x] **Spec: Remove stub logcat button** — Task 5
- [x] **Spec: EN/RU translations** — Tasks 4, 9
- [x] **Spec: Buffer limit 2000 lines** — Task 2, `_append_line`
- [x] **Spec: closeEvent cleanup** — Task 9
- [x] **Type consistency** — `_stop_process` called in `start`/`stop`; `_monitoring_tick` flag reset in both `_after_monitor_tick` and `_fail_worker`
