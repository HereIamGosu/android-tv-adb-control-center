<div align="center">

# Android TV ADB Control Center

**A Windows desktop GUI for Android TV / Google TV ADB pairing, wireless connect, scrcpy launch, APK install, screenshots, remote control, shell commands, and readable ADB diagnostics.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython-6/)
[![Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D4?logo=windows)](https://www.microsoft.com/windows)
[![ADB](https://img.shields.io/badge/ADB-Platform%20Tools-3DDC84?logo=android&logoColor=white)](https://developer.android.com/tools/adb)
[![scrcpy](https://img.shields.io/badge/scrcpy-supported-111111)](https://github.com/Genymobile/scrcpy)
[![Tests](https://img.shields.io/badge/tests-pytest-0A7BBB)](#development)
[![Download](https://img.shields.io/github/downloads/HereIamGosu/android-tv-adb-control-center/latest/total?label=Download%20.exe&color=brightgreen)](https://github.com/HereIamGosu/android-tv-adb-control-center/releases/download/latest/AndroidTVADBControlCenter.exe)

**Android TV ADB GUI** · **Google TV Wireless Debugging Tool** · **scrcpy launcher for TV** · **APK installer for Android TV**

</div>

---

## Why This Exists

Wireless ADB on Android TV is useful, but the normal workflow is still repetitive:

```powershell
adb pair <ip>:<pair-port>
adb connect <ip>:<connect-port>
adb devices -l
scrcpy -s <serial>
adb -s <serial> install app.apk
adb -s <serial> exec-out screencap -p
```

`Android TV ADB Control Center` turns that workflow into a transparent desktop tool. It does not replace ADB or scrcpy, and it does not hide the command line. It shows the command, exit code, stdout, stderr, and a practical explanation for common ADB failures.

Built for:

- Xiaomi TV Stick / Xiaomi TV Stick 4K
- Chromecast with Google TV
- Google TV Streamer
- Android TV boxes and televisions
- developer devices using Wireless Debugging

## Highlights

- **Wireless ADB pairing** with separate pair-port and connect-port fields.
- **ADB connect / disconnect / reset** without opening PowerShell.
- **Device list parser** for `adb devices -l`, including `device`, `offline`, `unauthorized`, and `unknown`.
- **scrcpy launcher** with `-s <serial>` for predictable multi-device behavior.
- **APK installer** with validation and install error explanations.
- **Screenshot capture** using `exec-out screencap -p` without shell redirection.
- **Remote control buttons** for DPAD, OK, Back, Home, Menu, Volume, and Power.
- **Simple ADB shell window** with warnings for potentially destructive commands.
- **Human-readable diagnostics** for common ADB and APK failures.
- **Operation timeouts** so short commands, pairing, screenshots, shell commands, and APK installs do not hang forever.
- **Auto connection monitor** — polls `adb devices -l` every 30 s; updates status and disables buttons silently when the device drops.
- **Live Logcat** — streams `adb logcat -v threadtime` directly in the main window with color-coded severity and tag filter.
- **Local-first settings** stored as JSON under `%APPDATA%`.
- **Bilingual UI**: English and Russian.

## Table of Contents

- [Quick Start](#quick-start)
- [Requirements](#requirements)
- [Core Workflow](#core-workflow)
- [Features](#features)
- [Troubleshooting](#troubleshooting)
- [Security Model](#security-model)
- [Project Structure](#project-structure)
- [Development](#development)
- [Roadmap](#roadmap)
- [Credits](#credits)

## Download

> **[⬇ Download AndroidTVADBControlCenter.exe](https://github.com/HereIamGosu/android-tv-adb-control-center/releases/download/latest/AndroidTVADBControlCenter.exe)**
>
> Windows 10 / 11 · No installation required · Built automatically from the latest commit

---

## Quick Start

Clone the repository:

```powershell
git clone https://github.com/HereIamGosu/android-tv-adb-control-center.git
cd android-tv-adb-control-center
```

Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the app:

```powershell
python -m app.main
```

## Requirements

| Requirement | Version / Notes |
|---|---|
| OS | Windows 10 or Windows 11 |
| Python | Python 3.11+ |
| GUI | PySide6 |
| Tests | pytest |
| ADB | `adb.exe` from Android SDK Platform Tools |
| Mirroring | `scrcpy.exe` |
| Device | Android TV / Google TV with Developer Options and Wireless Debugging |

For Android TV / Wear OS wireless debugging, Android documentation notes that Wireless Debugging requires Android 13 / API 33+ for TV and Wear OS devices. The workstation and device must be on the same network, and current Platform Tools are recommended.

## Core Workflow

### 1. Configure Tools

Open `Settings` and select:

- `adb.exe`
- `scrcpy.exe`
- default screenshot folder

Then run `Check tools`. The app calls:

```powershell
adb version
scrcpy --version
```

### 2. Create a Device Profile

Create a profile with:

- device name
- IP address or hostname
- pair-port
- connect-port
- last known serial
- custom scrcpy arguments
- screenshot folder

Settings and profiles are saved locally:

```text
%APPDATA%\ADBTVControlCenter\settings.json
```

If the JSON file is corrupted, the app backs it up and creates a fresh settings file instead of crashing at startup.

### 3. Pair

Use the pair-port from the Android TV pairing-code screen:

```powershell
adb pair <ip>:<pair-port>
```

The pairing code is passed through stdin and is not written to the command log.

Pair-port and connect-port are not interchangeable. Pair-port belongs to the current pairing-code session and can change the next time the TV opens that screen. If the TV shows a new pair-port, update it before pressing `Pair`.

### 4. Connect

Use the connect-port from the main Wireless Debugging screen:

```powershell
adb connect <ip>:<connect-port>
```

After connecting, the app runs:

```powershell
adb devices -l
```

Device actions are enabled only when the selected serial is confirmed as `device`.

### 5. Launch scrcpy

Recommended mode:

```powershell
scrcpy -s <serial>
```

The app exposes:

- `scrcpy serial`: runs `scrcpy -s <serial>` for the selected ADB serial.
- `scrcpy auto`: runs `scrcpy` without a selector, useful only when exactly one device is connected.
- `scrcpy TCP/IP`: runs `scrcpy --tcpip=<ip>:<connect-port>`.

## Features

### ADB Commands

All device-specific actions use `-s <serial>`:

```powershell
adb -s <serial> install <path-to-apk>
adb -s <serial> exec-out screencap -p
adb -s <serial> shell input keyevent KEYCODE_HOME
adb -s <serial> shell getprop ro.product.model
```

### APK Install

The app validates that the selected file exists and has an `.apk` extension, then runs:

```powershell
adb -s <serial> install <path-to-apk>
```

Known install errors are explained:

| Error | Meaning |
|---|---|
| `INSTALL_FAILED_VERSION_DOWNGRADE` | Installed app is newer than the selected APK |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | Package is already installed with a different signature |
| `INSTALL_PARSE_FAILED_NO_CERTIFICATES` | APK is damaged or incorrectly signed |

### Screenshots

The app captures PNG bytes directly:

```powershell
adb -s <serial> exec-out screencap -p
```

It writes stdout bytes to:

```text
screenshot_YYYY-MM-DD_HH-mm-ss.png
```

No shell redirection is used, and PNG output is not decoded as text.

### Remote Control

| Button | Android keycode |
|---|---|
| Up | `KEYCODE_DPAD_UP` |
| Down | `KEYCODE_DPAD_DOWN` |
| Left | `KEYCODE_DPAD_LEFT` |
| Right | `KEYCODE_DPAD_RIGHT` |
| OK | `KEYCODE_DPAD_CENTER` |
| Back | `KEYCODE_BACK` |
| Home | `KEYCODE_HOME` |
| Menu | `KEYCODE_MENU` |
| Volume Up | `KEYCODE_VOLUME_UP` |
| Volume Down | `KEYCODE_VOLUME_DOWN` |
| Power | `KEYCODE_POWER` |

### Connection Monitor

The app polls `adb devices -l` every 30 seconds while a device is connected. If the device drops off the network, the status updates to `Offline` and all device action buttons are disabled automatically — no popup, no hanging commands.

### Live Logcat

A Logcat panel in the main window streams `adb logcat -v threadtime` continuously while connected:

- Lines are color-coded by severity: red (Error), orange (Warning), gray (Debug/Verbose).
- A tag filter field hides irrelevant lines in real time.
- The buffer is capped at 2 000 lines to keep memory use stable.
- Logcat restarts automatically on reconnect, appending a `--- reconnected ---` separator.

### Shell Window

The MVP shell window runs one command at a time:

```powershell
adb -s <serial> shell <command>
```

Potentially destructive commands require confirmation:

- `pm uninstall`
- `cmd package uninstall`
- `settings put`
- `reboot bootloader`
- `reboot recovery`
- `wipe`
- `rm -rf`
- `dd`
- `su`

### Human Timeouts

Finite commands have explicit limits:

| Operation | Timeout |
|---|---:|
| Fast checks: `version`, `devices`, `getprop`, `keyevent`, ADB server commands | 10 seconds |
| `adb pair` / `adb connect` | 30 seconds |
| One-shot `adb shell <command>` | 45 seconds |
| Screenshot | 20 seconds |
| APK install | 180 seconds |
| `scrcpy --version` | 10 seconds |

Long-running scrcpy sessions are started as separate processes and are not treated as finite commands.

## Troubleshooting

### `protocol fault`

Likely causes:

- pair-port and connect-port were mixed up;
- pairing session expired;
- ADB server is stuck;
- Android TV regenerated the pairing port.

Recommended action:

```powershell
adb kill-server
adb start-server
```

Then open a new pairing-code screen on the TV, update the pair-port, and repeat pairing.

### `failed to connect`

Check:

- IP address;
- connect-port;
- same Wi-Fi / LAN;
- Wireless Debugging state;
- firewall rules;
- whether the TV went to sleep.

### `more than one device/emulator`

ADB sees more than one device. Select the target serial and run commands with:

```powershell
adb -s <serial> ...
```

This app uses `-s` for device-specific actions.

### `unauthorized`

Look at the TV screen and confirm the debugging authorization prompt. If needed, reset ADB authorizations in Developer Options.

### `device offline`

Restart the ADB server, toggle Wireless Debugging on the TV, then connect again.

## Security Model

This project is a transparent GUI wrapper over official command-line tools:

- no custom ADB protocol implementation;
- no hidden device control;
- no root automation;
- no DRM, subscription, region, or paid-access bypass features;
- no APK downloads;
- no built-in app store;
- no telemetry;
- no cloud sync;
- settings stay local.

Implementation rules:

- ADB and scrcpy commands are passed as argument lists.
- `shell=True` is not used for ADB/scrcpy commands.
- User input is never concatenated into a shell command line.
- Pairing codes are passed via stdin and are not logged.
- Screenshot output is handled as bytes.
- Potentially destructive shell commands require explicit confirmation.

## Project Structure

```text
app/
  main.py
  core/
    adb_runner.py
    scrcpy_runner.py
    command_result.py
    command_interpreter.py
    device_profile.py
    settings_store.py
    validators.py
    screenshot_service.py
    apk_install_service.py
    device_info_service.py
  ui/
    main_window.py
    dialogs/
    widgets/
tests/
README.md
requirements.txt
AUDIT.md
```

## Development

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run tests:

```powershell
python -m pytest
```

Compile-check Python modules:

```powershell
python -m compileall app tests
```

Construct the main window without opening a normal GUI session:

```powershell
$env:QT_QPA_PLATFORM='offscreen'
python -c "from PySide6.QtWidgets import QApplication; from app.ui.main_window import MainWindow; import sys; app=QApplication(sys.argv); w=MainWindow(); print('main window constructed')"
```

Current automated tests cover validators, command interpretation, settings storage, `adb devices -l` parsing, ADB/scrcpy command formation, screenshot bytes handling, worker lifecycle, operation timeouts, dangerous shell pattern detection, logcat widget behavior, and connection monitor timer lifecycle. They do not require a real Android TV device.

## Roadmap

- Logcat save-to-file.
- First-run setup wizard.
- Device profile import/export.
- Packaged Windows build.
- Screenshot preview.
- Better multi-device selector.
- Optional dark theme.
- Packaged smoke-check workflow for Windows builds.

## Credits

This project builds on the official Android tooling ecosystem:

- [Android Debug Bridge documentation](https://developer.android.com/tools/adb)
- [Android logcat documentation](https://developer.android.com/tools/logcat)
- [scrcpy](https://github.com/Genymobile/scrcpy)
- [Qt for Python / PySide6](https://doc.qt.io/qtforpython-6/)

The goal is not to replace ADB or scrcpy. The goal is to make the Android TV / Google TV workflow easier, safer, and more diagnosable on Windows.

## Support the Project

If this project saves you from repeating ADB commands by hand, consider starring the repository. Stars help other Android TV and Google TV users find the tool faster.
