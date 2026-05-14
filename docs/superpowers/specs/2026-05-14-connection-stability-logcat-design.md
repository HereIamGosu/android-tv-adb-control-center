# Connection Stability & Logcat — Design Spec

**Date:** 2026-05-14  
**Project:** ADB TV Control Center (PySide6 / Python)  
**Scope:** Two features — auto-connection monitoring and always-on Logcat widget

---

## Problem

1. `device_connected` is set to `True` after a successful connect and never updated unless the user manually triggers a command. If the device drops off the network, the UI shows "Connected" and device action buttons remain enabled — commands then silently fail or hang until timeout.

2. The Logcat button is a stub (`QMessageBox.information` with a placeholder string). There is no way to read device logs from within the app.

---

## Approach

**QTimer-based polling + QProcess Logcat** — minimal architectural change, fits existing patterns.

- `QTimer` (30 s interval) runs `adb devices -l` silently in the background when a device is connected.
- `QProcess` streams `adb logcat -v threadtime` output into a new `LogcatWidget` in the main window.
- Both are tied to the same `device_connected` lifecycle: start on connect, stop on disconnect/offline.

---

## Part 1: Connection Monitor

### Implementation

- In `MainWindow.__init__`: create `self._monitor_timer = QTimer(self)` with `timeout` connected to `self._monitor_tick`.
- `_monitor_tick`: skip if `operation_running` is `True`. Otherwise call `_run_worker` with a `_monitoring_tick=True` flag to suppress command log output.
- `_monitor_tick` result is processed by `_update_devices_from_result` (already exists).
- Timer starts: after `_after_connect` sets `device_connected = True`.
- Timer stops: in `_after_disconnect`, in `_update_devices_from_result` when state transitions away from `"device"`.

### Behavior on state change

| New state   | Action                                      |
|-------------|---------------------------------------------|
| `device`    | Stay connected, no UI change                |
| `offline`   | `device_connected = False`, status = Offline, stop timer, stop logcat |
| `unauthorized` | `device_connected = False`, status = Unauthorized, stop timer, stop logcat |
| not listed  | `device_connected = False`, status = Ready, stop timer, stop logcat |

### Error handling

- If the tick itself fails (timeout / OSError): set status to Offline silently, stop timer. No popup — this is a background check.

### No log spam

- Add `_monitoring_tick: bool` parameter to the internal worker path. When `True`, skip `log_widget.show_result()`.

---

## Part 2: Logcat Widget

### New file: `app/ui/widgets/logcat_widget.py`

**Class `LogcatWidget(QWidget)`:**

- `QPlainTextEdit` (read-only) for streaming output.
- `QLineEdit` tag filter — filters incoming lines before appending (case-insensitive substring match on the TAG field).
- Buffer limit: 2000 lines. When exceeded, remove oldest 200 lines in one operation.
- Uses `QProcess` — not `subprocess`. Signal `readyReadStandardOutput` → `_on_data`.

**Methods:**
- `start(adb_path: str, serial: str)` — launches `adb -s <serial> logcat -v threadtime`. Clears nothing, appends separator `--- started ---`.
- `stop()` — calls `process.terminate()`, waits 1 s, then `process.kill()`. Appends `--- stopped ---`.
- `_on_data()` — reads all available lines, applies tag filter, applies color formatting, appends.
- `_on_process_finished(exit_code, exit_status)` — appends `--- logcat disconnected ---`.

**Color formatting (per line):**
- Level `E` → red (`#cc0000`)
- Level `W` → orange (`#cc6600`)
- Level `I` → default color
- Level `D` / `V` → gray (`#888888`)

Level is parsed from position 4 of the space-split logcat line (threadtime format: `date time pid tid level tag: msg`).

**Language support:** title and placeholder text in EN/RU via `set_language(lang)`.

### Integration in `main_window.py`

- Add `LogcatWidget` to the right column, below the command log group.
- `_after_connect` → call `self.logcat_widget.start(adb_path, serial)` after `device_connected = True`.
- `_update_devices_from_result` when stopping → call `self.logcat_widget.stop()`.
- Pass `adb_path` from `self.settings.adb_path`.

### Reconnect behavior

- On reconnect (new successful connect after a drop): `start()` is called again. Output is **not cleared** — a `--- reconnected ---` separator is appended instead.

### Logcat button removal

- Remove `self.logcat_button` from `_build_device_actions_group` and all references (`_apply_enabled_state`, `_apply_language`).

---

## Translations

Add keys to `TRANSLATIONS` in `main_window.py`:

| Key              | EN                        | RU                      |
|------------------|---------------------------|-------------------------|
| `logcat`         | `"Logcat"`                | `"Logcat"`              |
| `logcat_filter`  | `"Filter by tag"`         | `"Фильтр по тегу"`      |
| `logcat_no_device` | `"No device connected"` | `"Устройство не подключено"` |

---

## Files Changed

| File | Change |
|------|--------|
| `app/ui/main_window.py` | Add `QTimer`, monitor logic, `LogcatWidget` integration, remove logcat stub button |
| `app/ui/widgets/logcat_widget.py` | New file |
| `app/ui/widgets/__init__.py` | Export `LogcatWidget` |
| `TRANSLATIONS` dict | Add 3 keys |

---

## Out of Scope

- `adb track-devices` protocol (Approach 2) — not used.
- Logcat file export / save.
- Logcat pause/resume controls.
- Any changes to `ADBRunner`, `CommandResult`, or test files (no behavioral change to existing APIs).

---

## Testing

Existing tests are unaffected — no changes to `core/`. Manual testing:

1. Connect device → verify timer starts, logcat starts, separator appears.
2. Pull device network → within 30 s status changes to Offline, buttons disabled.
3. Reconnect → logcat resumes with `--- reconnected ---` separator.
4. Tag filter → only matching lines appear in logcat output.
5. 2000+ lines → old lines removed, UI stays responsive.
