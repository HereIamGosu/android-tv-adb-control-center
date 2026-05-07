<div align="center">

# Android TV ADB Control Center

**A Windows desktop GUI for Android TV / Google TV ADB pairing, wireless connect, scrcpy launch, APK install, screenshots, remote control, shell commands, and human-readable ADB diagnostics.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython-6/)
[![Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D4?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![ADB](https://img.shields.io/badge/ADB-Platform%20Tools-3DDC84?logo=android&logoColor=white)](https://developer.android.com/tools/adb)
[![scrcpy](https://img.shields.io/badge/scrcpy-supported-111111)](https://github.com/Genymobile/scrcpy)
[![Languages](https://img.shields.io/badge/UI-English%20%7C%20Russian-6A5ACD)](#features)

**Android TV ADB GUI** · **Google TV Wireless Debugging Tool** · **scrcpy launcher for TV** · **APK installer for Android TV**

</div>

---

## Why this project exists

Wireless ADB on Android TV is powerful, but the daily workflow is still too manual:

```powershell
adb pair <ip>:<pair-port>
adb connect <ip>:<connect-port>
adb devices -l
scrcpy -s <serial>
adb -s <serial> install app.apk
adb -s <serial> exec-out screencap -p
```

`Android TV ADB Control Center` turns that workflow into a transparent desktop tool. It does not hide the command line. It shows the exact command, exit code, stdout, stderr, and a readable explanation of common ADB errors.

The project is built for people who manage or debug:

- Xiaomi TV Stick / Xiaomi TV Stick 4K
- Chromecast with Google TV
- Google TV Streamer
- Android TV boxes
- Android TV televisions
- developer devices using ADB wireless debugging

## Highlights

- **Wireless ADB pairing** with separate pair-port and connect-port fields.
- **ADB connect / disconnect / reset** without opening PowerShell.
- **Device list parser** for `adb devices -l` with serial and state detection.
- **scrcpy launcher** that always uses `-s <serial>` for predictable multi-device behavior.
- **APK installer** with file picker, confirmation dialog, and install error explanations.
- **Screenshot capture** using `exec-out screencap -p` without shell redirection.
- **Remote control buttons** for DPAD, OK, Back, Home, Menu, Volume, and Power.
- **Simple ADB shell window** with warnings for potentially destructive commands.
- **Human-readable diagnostics** for `protocol fault`, `failed to connect`, `unauthorized`, `device offline`, `more than one device/emulator`, and APK install failures.
- **Local-first design**: settings and device profiles are stored as local JSON.
- **Bilingual UI**: switch between English and Russian from the main window.

## Screenshot

The first public screenshot should be captured from a normal Windows GUI session after a successful `adb devices -l` refresh.

Recommended image path for the repository:

```text
docs/assets/android-tv-adb-control-center-main.png
```

Suggested alt text:

```text
Android TV ADB Control Center main window showing ADB status, device profile, connection actions, remote control buttons, and command log.
```

## Table of Contents

- [Quick Start](#quick-start)
- [Requirements](#requirements)
- [Core Workflow](#core-workflow)
- [Features](#features)
- [Troubleshooting](#troubleshooting)
- [Security Model](#security-model)
- [Project Structure](#project-structure)
- [Development](#development)
- [SEO Topics](#seo-topics)
- [Roadmap](#roadmap)
- [Star History](#star-history)
- [Credits](#credits)

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
| ADB | `adb.exe` from Android SDK Platform Tools |
| Mirroring | `scrcpy.exe` |
| Device | Android TV / Google TV with Developer Options and Wireless Debugging |

For Android TV / Wear OS wireless debugging, Android documentation notes that Wireless Debugging requires Android 13 / API 33+ for TV and Wear OS devices. The workstation and device must be on the same network, and current Platform Tools are recommended.

## Core Workflow

### 1. Configure tools

Open `Settings` and select:

- `adb.exe`
- `scrcpy.exe`
- default screenshot folder

Then run `Check tools`.

### 2. Create a device profile

Create a profile with:

- device name
- IP address or hostname
- pair-port
- connect-port
- custom scrcpy arguments
- screenshot folder

Pair-port and connect-port are intentionally separate. On modern Android wireless debugging flows, they are often different.

### 3. Pair

Use the pair-port from the Android TV screen:

```powershell
adb pair <ip>:<pair-port>
```

The pairing code is passed to the process stdin and is not stored in the command log.

### 4. Connect

Use the connect-port from the Wireless Debugging screen:

```powershell
adb connect <ip>:<connect-port>
```

After connecting, the app runs:

```powershell
adb devices -l
```

Device actions are enabled only when the selected serial is confirmed as `device`.

### 5. Launch scrcpy

```powershell
scrcpy -s <serial> <extra-args>
```

The app always passes `-s <serial>`, which avoids ambiguous behavior when ADB sees multiple devices.

## Features

### ADB tool checks

- `adb version`
- `scrcpy --version`
- clear success/error output in the command log

### Device profiles

Profiles are saved locally in:

```text
%APPDATA%\ADBTVControlCenter\settings.json
```

If the JSON file is corrupted, the app backs it up and creates a fresh settings file.

### APK install

The app runs:

```powershell
adb -s <serial> install <path-to-apk>
```

Known install errors are explained:

| Error | Explanation |
|---|---|
| `INSTALL_FAILED_VERSION_DOWNGRADE` | Installed app is newer than the selected APK |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | Package is already installed with a different signature |
| `INSTALL_PARSE_FAILED_NO_CERTIFICATES` | APK is damaged or incorrectly signed |

### Screenshots

The app runs:

```powershell
adb -s <serial> exec-out screencap -p
```

It reads PNG bytes from stdout and writes them to:

```text
screenshot_YYYY-MM-DD_HH-mm-ss.png
```

No shell redirection is used.

### Remote control

Supported key events:

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

### Shell window

The MVP shell window runs one command at a time:

```powershell
adb -s <serial> shell <command>
```

Potentially destructive patterns trigger a warning:

- `pm uninstall`
- `cmd package uninstall`
- `settings put`
- `reboot bootloader`
- `reboot recovery`
- `wipe`
- `rm -rf`
- `dd`
- `su`

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

Then open a new pairing-code screen on the TV and repeat pairing with the new pair-port.

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

Restart the ADB server, toggle Wireless Debugging on the TV, and connect again.

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

The app shows the real command it runs. Pairing codes are intentionally not written to the log.

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
README.md
requirements.txt
```

## Development

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Compile-check Python modules:

```powershell
python -m compileall app
```

Construct the main window without opening a normal GUI session:

```powershell
$env:QT_QPA_PLATFORM='offscreen'
python -c "from PySide6.QtWidgets import QApplication; from app.ui.main_window import MainWindow; import sys; app=QApplication(sys.argv); w=MainWindow(); print('main window constructed')"
```

## SEO Topics

Recommended GitHub repository topics:

```text
android-tv
google-tv
adb
adb-gui
scrcpy
scrcpy-gui
wireless-debugging
android-debug-bridge
apk-installer
android-tv-remote
google-tv-remote
pyside6
python
windows
desktop-app
```

Recommended repository description:

```text
Windows GUI for Android TV / Google TV ADB pairing, wireless connect, scrcpy, APK install, screenshots, remote control, shell, and diagnostics.
```

Search phrases this project is designed to match:

- Android TV ADB GUI
- Google TV ADB wireless debugging
- Android TV scrcpy GUI
- ADB pair connect GUI Windows
- APK installer for Android TV
- Android TV remote control from PC
- Xiaomi TV Stick ADB tool

## Roadmap

- Streaming `adb logcat` window with start/stop and save-to-file.
- First-run setup wizard.
- Device profile import/export.
- Packaged Windows build.
- Screenshot preview.
- Better multi-device selector.
- Optional dark theme.
- Packaged smoke-check workflow for Windows builds.

## Star History

<a href="https://star-history.com/#HereIamGosu/android-tv-adb-control-center&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HereIamGosu/android-tv-adb-control-center&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HereIamGosu/android-tv-adb-control-center&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HereIamGosu/android-tv-adb-control-center&type=Date" />
 </picture>
</a>

## Credits

This project builds on the official Android tooling ecosystem:

- [Android Debug Bridge documentation](https://developer.android.com/tools/adb)
- [Android wireless debugging documentation](https://developer.android.google.cn/tools/adb?hl=en)
- [scrcpy](https://github.com/Genymobile/scrcpy)

The goal is not to replace ADB or scrcpy. The goal is to make the Android TV / Google TV workflow easier, safer, and more diagnosable on Windows.

## Support the project

If this project saves you from repeating ADB commands by hand, consider starring the repository. Stars help other Android TV and Google TV users find the tool faster.
