from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.adb_runner import ADBRunner, parse_adb_devices
from app.core.apk_install_service import APKInstallService
from app.core.command_result import CommandResult
from app.core.device_info_service import DeviceInfoService
from app.core.device_profile import AppSettings, DeviceProfile
from app.core.scrcpy_runner import ScrcpyRunner
from app.core.screenshot_service import ScreenshotService
from app.core.settings_store import SettingsStore
from app.core.validators import validate_ip_or_host, validate_port, validate_serial
from app.ui.dialogs.device_profile_dialog import DeviceProfileDialog
from app.ui.dialogs.settings_dialog import SettingsDialog
from app.ui.dialogs.shell_window import ShellWindow
from app.ui.widgets.command_log_widget import CommandLogWidget
from app.ui.widgets.device_status_widget import DeviceStatusWidget
from app.ui.widgets.remote_control_widget import RemoteControlWidget


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class CommandWorker(QRunnable):
    def __init__(self, callback: Callable[[], object]):
        super().__init__()
        self.callback = callback
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            self.signals.finished.emit(self.callback())
        except Exception as exc:
            self.signals.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self, store: SettingsStore | None = None):
        super().__init__()
        self.setWindowTitle("ADB TV Control Center")
        self.resize(1280, 760)
        self.store = store or SettingsStore()
        document = self.store.load()
        self.settings = document.settings
        self.profiles = document.profiles
        self.thread_pool = QThreadPool.globalInstance()
        self.current_serial: str | None = None
        self.device_connected = False
        self.operation_running = False
        self.shell_windows: list[ShellWindow] = []

        self._build_ui()
        self._load_profiles()
        self._apply_enabled_state()
        if document.warning:
            QMessageBox.warning(self, "Settings warning", document.warning)

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)

        left_column = QVBoxLayout()
        right_column = QVBoxLayout()
        root_layout.addLayout(left_column, 1)
        root_layout.addLayout(right_column, 1)

        left_column.addWidget(self._build_tool_status_group())
        left_column.addWidget(self._build_connection_help_group())
        left_column.addWidget(self._build_profile_group())
        left_column.addWidget(self._build_connection_group())
        left_column.addStretch()

        right_column.addWidget(self._build_device_actions_group())
        self.remote_widget = RemoteControlWidget()
        self.remote_widget.keyevent_requested.connect(self._send_keyevent)
        remote_group = QGroupBox("Remote control")
        remote_layout = QVBoxLayout(remote_group)
        remote_layout.addWidget(self.remote_widget)
        right_column.addWidget(remote_group)
        self.log_widget = CommandLogWidget()
        log_group = QGroupBox("Command log")
        log_layout = QVBoxLayout(log_group)
        log_layout.addWidget(self.log_widget)
        right_column.addWidget(log_group, 1)

    def _build_tool_status_group(self) -> QGroupBox:
        group = QGroupBox("Tool status")
        layout = QFormLayout(group)
        self.adb_path_label = QLabel(self.settings.adb_path or "-")
        self.scrcpy_path_label = QLabel(self.settings.scrcpy_path or "-")
        self.operation_label = QLabel("Idle")
        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self._open_settings)
        check_tools_button = QPushButton("Check tools")
        check_tools_button.clicked.connect(self._check_tools)
        row = QHBoxLayout()
        row.addWidget(settings_button)
        row.addWidget(check_tools_button)
        row.addStretch()
        layout.addRow("adb.exe", self.adb_path_label)
        layout.addRow("scrcpy.exe", self.scrcpy_path_label)
        layout.addRow("Current operation", self.operation_label)
        layout.addRow(row)
        return group

    def _build_profile_group(self) -> QGroupBox:
        group = QGroupBox("Device profile")
        layout = QFormLayout(group)
        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self._profile_changed)
        self.serial_combo = QComboBox()
        self.serial_combo.currentTextChanged.connect(self._serial_changed)
        add_button = QPushButton("Add profile")
        add_button.clicked.connect(self._add_profile)
        edit_button = QPushButton("Edit profile")
        edit_button.clicked.connect(self._edit_profile)
        buttons = QHBoxLayout()
        buttons.addWidget(add_button)
        buttons.addWidget(edit_button)
        buttons.addStretch()
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("Example: 192.168.1.113")
        self.pair_port_edit = QLineEdit()
        self.pair_port_edit.setPlaceholderText("Example: 39631")
        self.connect_port_edit = QLineEdit()
        self.connect_port_edit.setPlaceholderText("Usually different from pair-port")
        self.device_status = DeviceStatusWidget()
        layout.addRow("Profile", self.profile_combo)
        layout.addRow(buttons)
        layout.addRow("IP / hostname", self.ip_edit)
        layout.addRow("Pair port", self.pair_port_edit)
        layout.addRow("Connect port", self.connect_port_edit)
        layout.addRow(
            "Serial",
            self._field_with_hint(
                self.serial_combo,
                "Filled after Refresh devices. Must be in state device.",
            ),
        )
        layout.addRow("Status", self.device_status)
        return group

    def _build_connection_help_group(self) -> QGroupBox:
        group = QGroupBox("How to connect")
        layout = QVBoxLayout(group)
        help_text = QLabel(
            "IP: enter only the address part, for example 192.168.1.113.\n"
            "Pair port: take it from 'Pair device with pairing code'. Enter the 6-digit code after pressing Pair.\n"
            "Connect port: take it from the main Wireless Debugging screen. It is usually different from pair-port.\n"
            "Actions unlock only when adb devices -l reports the selected serial as device."
        )
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        return group

    def _build_connection_group(self) -> QGroupBox:
        group = QGroupBox("Connection actions")
        layout = QHBoxLayout(group)
        self.pair_button = QPushButton("Pair")
        self.connect_button = QPushButton("Connect")
        self.disconnect_button = QPushButton("Disconnect")
        self.reset_adb_button = QPushButton("Reset ADB")
        self.refresh_devices_button = QPushButton("Refresh devices")
        self.pair_button.clicked.connect(self._pair)
        self.connect_button.clicked.connect(self._connect)
        self.disconnect_button.clicked.connect(self._disconnect)
        self.reset_adb_button.clicked.connect(self._reset_adb)
        self.refresh_devices_button.clicked.connect(self._refresh_devices)
        for button in (
            self.pair_button,
            self.connect_button,
            self.disconnect_button,
            self.reset_adb_button,
            self.refresh_devices_button,
        ):
            layout.addWidget(button)
        layout.addStretch()
        return group

    def _build_device_actions_group(self) -> QGroupBox:
        group = QGroupBox("Device actions")
        layout = QHBoxLayout(group)
        self.scrcpy_button = QPushButton("Launch scrcpy")
        self.install_apk_button = QPushButton("Install APK")
        self.screenshot_button = QPushButton("Screenshot")
        self.device_info_button = QPushButton("Device Info")
        self.shell_button = QPushButton("Open Shell")
        self.logcat_button = QPushButton("Start Logcat")
        self.scrcpy_button.clicked.connect(self._launch_scrcpy)
        self.install_apk_button.clicked.connect(self._install_apk)
        self.screenshot_button.clicked.connect(self._screenshot)
        self.device_info_button.clicked.connect(self._device_info)
        self.shell_button.clicked.connect(self._open_shell)
        self.logcat_button.clicked.connect(
            lambda: QMessageBox.information(
                self, "Logcat", "Logcat оставлен stub-кнопкой в первом каркасе MVP."
            )
        )
        for button in (
            self.scrcpy_button,
            self.install_apk_button,
            self.screenshot_button,
            self.device_info_button,
            self.shell_button,
            self.logcat_button,
        ):
            layout.addWidget(button)
        layout.addStretch()
        return group

    def _load_profiles(self) -> None:
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for profile in self.profiles:
            self.profile_combo.addItem(profile.name, profile.id)
        self.profile_combo.blockSignals(False)
        if self.profiles:
            index = 0
            if self.settings.last_device_profile_id:
                for row, profile in enumerate(self.profiles):
                    if profile.id == self.settings.last_device_profile_id:
                        index = row
                        break
            self.profile_combo.setCurrentIndex(index)
            self._profile_changed(index)

    def _current_profile(self) -> DeviceProfile | None:
        index = self.profile_combo.currentIndex()
        if index < 0 or index >= len(self.profiles):
            return None
        return self.profiles[index]

    def _profile_changed(self, index: int) -> None:
        profile = self._current_profile()
        if not profile:
            return
        self.ip_edit.setText(profile.ip)
        self.pair_port_edit.setText(str(profile.pair_port or ""))
        self.connect_port_edit.setText(str(profile.connect_port or ""))
        self.current_serial = profile.last_serial
        self.device_connected = False
        self.serial_combo.clear()
        if profile.last_serial:
            self.serial_combo.addItem(profile.last_serial)
        self.device_status.set_status("Ready", self.current_serial)
        self.settings.last_device_profile_id = profile.id
        self._save()
        self._apply_enabled_state()

    def _serial_changed(self, serial: str) -> None:
        self.current_serial = serial or None
        self.device_connected = False
        self._apply_enabled_state()

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            previous_last_profile = self.settings.last_device_profile_id
            self.settings = dialog.settings()
            self.settings.last_device_profile_id = previous_last_profile
            self.adb_path_label.setText(self.settings.adb_path or "-")
            self.scrcpy_path_label.setText(self.settings.scrcpy_path or "-")
            self._save()
            self._apply_enabled_state()

    def _add_profile(self) -> None:
        dialog = DeviceProfileDialog(parent=self)
        if dialog.exec():
            self.profiles.append(dialog.device_profile())
            self._save()
            self._load_profiles()

    def _edit_profile(self) -> None:
        profile = self._current_profile()
        if not profile:
            QMessageBox.warning(self, "Profile", "Сначала создайте профиль.")
            return
        dialog = DeviceProfileDialog(profile, self)
        if dialog.exec():
            self.profiles[self.profile_combo.currentIndex()] = dialog.device_profile()
            self._save()
            self._load_profiles()

    def _adb_runner(self) -> ADBRunner:
        return ADBRunner(Path(self.settings.adb_path))

    def _scrcpy_runner(self) -> ScrcpyRunner:
        return ScrcpyRunner(Path(self.settings.scrcpy_path))

    def _check_tools(self) -> None:
        self._run_worker(
            lambda: [self._adb_runner().version(), self._scrcpy_runner().version()],
            self._show_many_results,
            "Checking adb.exe and scrcpy.exe versions",
        )

    def _pair(self) -> None:
        connection = self._validated_connection(require_pair=True)
        if not connection:
            return
        ip, pair_port, _ = connection
        code, ok = QInputDialog.getText(
            self, "Pairing code", "Введите pairing code с экрана TV:"
        )
        if not ok or not code.strip():
            return
        self._run_worker(
            lambda: self._adb_runner().pair(ip, pair_port, code.strip()),
            self._show_result,
            f"Pairing {ip}:{pair_port}",
        )

    def _connect(self) -> None:
        connection = self._validated_connection()
        if not connection:
            return
        ip, _, connect_port = connection

        def task() -> list[CommandResult]:
            adb = self._adb_runner()
            connect_result = adb.connect(ip, connect_port)
            devices_result = adb.devices()
            return [connect_result, devices_result]

        self._run_worker(task, self._after_connect, f"Connecting {ip}:{connect_port}")

    def _disconnect(self) -> None:
        self._run_worker(
            lambda: self._adb_runner().disconnect(), self._after_disconnect, "Disconnecting ADB devices"
        )

    def _reset_adb(self) -> None:
        def task() -> list[CommandResult]:
            adb = self._adb_runner()
            return [
                adb.disconnect(),
                adb.kill_server(),
                adb.start_server(),
                adb.devices(),
            ]

        self._run_worker(task, self._show_many_results, "Resetting ADB server")

    def _refresh_devices(self) -> None:
        self._run_worker(lambda: self._adb_runner().devices(), self._after_devices, "Refreshing adb devices -l")

    def _launch_scrcpy(self) -> None:
        serial = self._validated_serial()
        profile = self._current_profile()
        if not serial or not profile:
            return
        self._run_worker(
            lambda: self._scrcpy_runner().launch(serial, profile.scrcpy_args),
            self._show_result,
            f"Launching scrcpy for {serial}",
        )

    def _install_apk(self) -> None:
        serial = self._validated_serial()
        if not serial:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Select APK", "", "Android package (*.apk)"
        )
        if not path:
            return
        answer = QMessageBox.question(
            self, "Install APK", f"Установить APK на выбранное устройство?\n{path}"
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._run_worker(
            lambda: APKInstallService(self._adb_runner()).install(serial, Path(path)),
            self._show_result,
            f"Installing APK to {serial}",
        )

    def _screenshot(self) -> None:
        serial = self._validated_serial()
        profile = self._current_profile()
        if not serial or not profile:
            return
        self._run_worker(
            lambda: ScreenshotService(self._adb_runner()).capture(
                serial, Path(profile.screenshot_dir)
            )[0],
            self._show_result,
            f"Taking screenshot from {serial}",
        )

    def _device_info(self) -> None:
        serial = self._validated_serial()
        if not serial:
            return

        def task() -> tuple[dict[str, str], list[CommandResult]]:
            return DeviceInfoService(self._adb_runner()).read(serial)

        self._run_worker(task, self._show_device_info, f"Reading device info from {serial}")

    def _open_shell(self) -> None:
        serial = self._validated_serial()
        if not serial:
            return
        window = ShellWindow(self._adb_runner(), serial, self)
        self.shell_windows.append(window)
        window.resize(760, 420)
        window.show()

    def _send_keyevent(self, keycode: str) -> None:
        serial = self._validated_serial(show_message=False)
        if not serial:
            return
        self._run_worker(
            lambda: self._adb_runner().keyevent(serial, keycode), self._show_result, f"Sending {keycode}"
        )

    def _validated_connection(
        self, require_pair: bool = False
    ) -> tuple[str, int, int] | None:
        ip = self.ip_edit.text().strip()
        pair_port = self.pair_port_edit.text().strip()
        connect_port = self.connect_port_edit.text().strip()
        for is_valid, error in (
            validate_ip_or_host(ip),
            validate_port(pair_port),
            validate_port(connect_port),
        ):
            if not is_valid:
                QMessageBox.warning(self, "Invalid connection data", error)
                return None
        if require_pair and pair_port == connect_port:
            answer = QMessageBox.warning(
                self,
                "Pair/connect ports",
                "Pair-port и connect-port совпадают. Обычно для adb pair и adb connect нужны разные порты. Продолжить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return None
        return ip, int(pair_port), int(connect_port)

    def _validated_serial(self, show_message: bool = True) -> str | None:
        serial = self.current_serial or self.serial_combo.currentText().strip()
        is_valid, error = validate_serial(serial)
        if not is_valid:
            if show_message:
                QMessageBox.warning(self, "Serial", error)
            return None
        return serial

    def _after_connect(self, results: list[CommandResult]) -> None:
        self._show_many_results(results)
        devices_result = results[-1]
        self._update_devices_from_result(devices_result)
        connection = self._validated_connection()
        if not connection:
            return
        ip, _, connect_port = connection
        serial = f"{ip}:{connect_port}"
        entries = parse_adb_devices(devices_result.stdout)
        connected = any(
            entry.serial == serial and entry.state == "device" for entry in entries
        )
        if connected:
            self.current_serial = serial
            self.device_connected = True
            profile = self._current_profile()
            if profile:
                profile.last_serial = serial
                self._save()
            self.device_status.set_status("Connected", serial)
        else:
            self.device_connected = False
            self.device_status.set_status("Error", serial)
            QMessageBox.warning(
                self,
                "Device not connected",
                "adb connect finished, but adb devices -l did not report the expected serial as device.\n\n"
                "Check that Connect port is from the main Wireless Debugging screen, not from the pairing-code dialog.",
            )
        self._apply_enabled_state()

    def _after_disconnect(self, result: CommandResult) -> None:
        self._show_result(result)
        self.device_connected = False
        self.device_status.set_status("Ready", self.current_serial)
        self._apply_enabled_state()

    def _after_devices(self, result: CommandResult) -> None:
        self._show_result(result)
        self._update_devices_from_result(result)

    def _update_devices_from_result(self, result: CommandResult) -> None:
        entries = parse_adb_devices(result.stdout)
        current = self.current_serial
        self.serial_combo.blockSignals(True)
        self.serial_combo.clear()
        for entry in entries:
            self.serial_combo.addItem(entry.serial)
        if current:
            row = self.serial_combo.findText(current)
            if row >= 0:
                self.serial_combo.setCurrentIndex(row)
        self.serial_combo.blockSignals(False)
        selected = self.serial_combo.currentText().strip()
        self.current_serial = selected or current
        states = {entry.serial: entry.state for entry in entries}
        if self.current_serial and states.get(self.current_serial) == "device":
            self.device_connected = True
            self.device_status.set_status("Connected", self.current_serial)
        elif self.current_serial and states.get(self.current_serial) == "offline":
            self.device_connected = False
            self.device_status.set_status("Offline", self.current_serial)
        elif self.current_serial and states.get(self.current_serial) == "unauthorized":
            self.device_connected = False
            self.device_status.set_status("Unauthorized", self.current_serial)
        else:
            self.device_connected = False
            self.device_status.set_status("Ready", self.current_serial)
        self._apply_enabled_state()

    def _show_device_info(
        self, payload: tuple[dict[str, str], list[CommandResult]]
    ) -> None:
        info, results = payload
        self._show_many_results(results)
        text = "\n".join(
            [
                f"Manufacturer: {info.get('manufacturer', '')}",
                f"Model: {info.get('model', '')}",
                f"Android version: {info.get('android_version', '')}",
                f"SDK: {info.get('sdk', '')}",
            ]
        )
        QMessageBox.information(self, "Device Info", text)

    def _show_many_results(self, results: list[CommandResult]) -> None:
        if results:
            self._show_result(results[-1])

    def _show_result(self, result: CommandResult) -> None:
        self.log_widget.show_result(result)

    def _run_worker(
        self,
        task: Callable[[], object],
        on_finished: Callable[[object], None],
        operation_text: str,
    ) -> None:
        worker = CommandWorker(task)
        self.operation_running = True
        self.operation_label.setText(f"Running: {operation_text}")
        self._apply_enabled_state()
        worker.signals.finished.connect(lambda payload: self._finish_worker(payload, on_finished))
        worker.signals.failed.connect(lambda message: self._fail_worker(message))
        self.thread_pool.start(worker)

    def _finish_worker(self, payload: object, on_finished: Callable[[object], None]) -> None:
        self.operation_running = False
        self.operation_label.setText("Idle")
        on_finished(payload)
        self._apply_enabled_state()

    def _fail_worker(self, message: str) -> None:
        self.operation_running = False
        self.operation_label.setText("Failed")
        self._apply_enabled_state()
        QMessageBox.critical(self, "Error", message)

    def _apply_enabled_state(self) -> None:
        adb_ready = bool(self.settings.adb_path)
        scrcpy_ready = bool(self.settings.scrcpy_path)
        can_use_device = bool(self.current_serial and self.device_connected)
        for button in (
            self.pair_button,
            self.connect_button,
            self.disconnect_button,
            self.reset_adb_button,
            self.refresh_devices_button,
        ):
            button.setEnabled(adb_ready and not self.operation_running)
        for button in (
            self.install_apk_button,
            self.screenshot_button,
            self.device_info_button,
            self.shell_button,
            self.logcat_button,
        ):
            button.setEnabled(adb_ready and can_use_device and not self.operation_running)
        self.scrcpy_button.setEnabled(scrcpy_ready and can_use_device and not self.operation_running)
        self.remote_widget.set_controls_enabled(adb_ready and can_use_device and not self.operation_running)

    def _save(self) -> None:
        self.store.save(self.settings, self.profiles)

    def _field_with_hint(self, field: QWidget, hint: str) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.addWidget(field)
        label = QLabel(hint)
        label.setWordWrap(True)
        label.setMaximumHeight(36)
        label.setStyleSheet("color: #555;")
        layout.addWidget(label)
        return container
