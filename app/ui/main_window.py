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


TRANSLATIONS = {
    "en": {
        "window_title": "ADB TV Control Center",
        "tool_status": "Tool status",
        "settings": "Settings",
        "check_tools": "Check tools",
        "current_operation": "Current operation",
        "language": "Language",
        "idle": "Idle",
        "failed": "Failed",
        "device_profile": "Device profile",
        "profile": "Profile",
        "add_profile": "Add profile",
        "edit_profile": "Edit profile",
        "ip": "IP / hostname",
        "pair_port": "Pair port",
        "connect_port": "Connect port",
        "serial": "Serial",
        "status": "Status",
        "serial_hint": "Filled after Refresh devices. Must be in state device.",
        "how_to_connect": "How to connect",
        "connect_help": (
            "IP: enter only the address part, for example 192.168.1.113.\n"
            "Pair port: take it from 'Pair device with pairing code'. Enter the 6-digit code after pressing Pair.\n"
            "Connect port: take it from the main Wireless Debugging screen. It is usually different from pair-port.\n"
            "scrcpy TCP/IP can start with --tcpip=IP:ConnectPort even before Refresh devices confirms a serial.\n"
            "Actions unlock only when adb devices -l reports the selected serial as device."
        ),
        "connection_actions": "Connection actions",
        "pair": "Pair",
        "connect": "Connect",
        "disconnect": "Disconnect",
        "reset_adb": "Reset ADB",
        "refresh_devices": "Refresh devices",
        "device_actions": "Device actions",
        "launch_scrcpy": "scrcpy serial",
        "launch_scrcpy_auto": "scrcpy auto",
        "launch_scrcpy_tcpip": "scrcpy TCP/IP",
        "install_apk": "Install APK",
        "screenshot": "Screenshot",
        "device_info": "Device Info",
        "open_shell": "Open Shell",
        "start_logcat": "Start Logcat",
        "remote_control": "Remote control",
        "command_log": "Command log",
        "running": "Running: {operation}",
        "pairing_code_title": "Pairing code",
        "pairing_code_prompt": "Enter the 6-digit pairing code from the TV screen:",
        "invalid_connection": "Invalid connection data",
        "same_ports_warning": "Pair-port and connect-port are the same. Usually adb pair and adb connect use different ports. Continue?",
        "pair_connect_ports": "Pair/connect ports",
        "profile_missing": "Create a profile first.",
        "device_not_connected_title": "Device not connected",
        "device_not_connected_text": (
            "adb connect finished, but adb devices -l did not report the expected serial as device.\n\n"
            "Check that Connect port is from the main Wireless Debugging screen, not from the pairing-code dialog."
        ),
        "install_confirm": "Install APK on the selected device?\n{path}",
        "logcat_stub": "Logcat is still a stub button in this MVP build.",
        "ready": "Ready",
        "connected": "Connected",
        "offline": "Offline",
        "unauthorized": "Unauthorized",
        "error": "Error",
    },
    "ru": {
        "window_title": "ADB TV Control Center",
        "tool_status": "Инструменты",
        "settings": "Настройки",
        "check_tools": "Проверить",
        "current_operation": "Текущая операция",
        "language": "Язык",
        "idle": "Ожидание",
        "failed": "Ошибка",
        "device_profile": "Профиль устройства",
        "profile": "Профиль",
        "add_profile": "Добавить",
        "edit_profile": "Изменить",
        "ip": "IP / hostname",
        "pair_port": "Pair port",
        "connect_port": "Connect port",
        "serial": "Serial",
        "status": "Статус",
        "serial_hint": "Заполняется после Refresh devices. Состояние должно быть device.",
        "how_to_connect": "Как подключиться",
        "connect_help": (
            "IP: вводи только адрес, например 192.168.1.113.\n"
            "Pair port: бери из окна 'Pair device with pairing code'. 6-значный код вводится после нажатия Pair.\n"
            "Connect port: бери с главного экрана Wireless Debugging. Обычно он отличается от pair-port.\n"
            "scrcpy TCP/IP запускает --tcpip=IP:ConnectPort даже до подтверждения serial через Refresh devices.\n"
            "Действия станут доступны только когда adb devices -l покажет выбранный serial в состоянии device."
        ),
        "connection_actions": "Подключение",
        "pair": "Pair",
        "connect": "Connect",
        "disconnect": "Отключить",
        "reset_adb": "Сброс ADB",
        "refresh_devices": "Обновить devices",
        "device_actions": "Действия",
        "launch_scrcpy": "scrcpy serial",
        "launch_scrcpy_auto": "scrcpy auto",
        "launch_scrcpy_tcpip": "scrcpy TCP/IP",
        "install_apk": "Установить APK",
        "screenshot": "Скриншот",
        "device_info": "Информация",
        "open_shell": "Shell",
        "start_logcat": "Logcat",
        "remote_control": "Пульт",
        "command_log": "Лог команд",
        "running": "Выполняется: {operation}",
        "pairing_code_title": "Код сопряжения",
        "pairing_code_prompt": "Введи 6-значный pairing code с экрана TV:",
        "invalid_connection": "Некорректные данные подключения",
        "same_ports_warning": "Pair-port и connect-port совпадают. Обычно adb pair и adb connect используют разные порты. Продолжить?",
        "pair_connect_ports": "Pair/connect ports",
        "profile_missing": "Сначала создай профиль.",
        "device_not_connected_title": "Устройство не подключено",
        "device_not_connected_text": (
            "adb connect завершился, но adb devices -l не показал ожидаемый serial в состоянии device.\n\n"
            "Проверь, что Connect port взят с главного экрана Wireless Debugging, а не из окна pairing-code."
        ),
        "install_confirm": "Установить APK на выбранное устройство?\n{path}",
        "logcat_stub": "Logcat пока оставлен stub-кнопкой в MVP.",
        "ready": "Готово",
        "connected": "Подключено",
        "offline": "Offline",
        "unauthorized": "Unauthorized",
        "error": "Ошибка",
    },
}


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
        self._operation_text = ""

        self._build_ui()
        self._apply_language()
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
        self.remote_widget = RemoteControlWidget(self.settings.language)
        self.remote_widget.keyevent_requested.connect(self._send_keyevent)
        self.remote_group = QGroupBox()
        remote_layout = QVBoxLayout(self.remote_group)
        remote_layout.addWidget(self.remote_widget)
        right_column.addWidget(self.remote_group)
        self.log_widget = CommandLogWidget(self.settings.language)
        self.log_group = QGroupBox()
        log_layout = QVBoxLayout(self.log_group)
        log_layout.addWidget(self.log_widget)
        right_column.addWidget(self.log_group, 1)

    def _build_tool_status_group(self) -> QGroupBox:
        self.tool_status_group = QGroupBox()
        layout = QFormLayout(self.tool_status_group)
        self.adb_path_label = QLabel(self.settings.adb_path or "-")
        self.scrcpy_path_label = QLabel(self.settings.scrcpy_path or "-")
        self.operation_label = QLabel()
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Русский", "ru")
        language_index = self.language_combo.findData(self.settings.language)
        self.language_combo.setCurrentIndex(max(language_index, 0))
        self.language_combo.currentIndexChanged.connect(self._language_changed)
        self.settings_button = QPushButton()
        self.settings_button.clicked.connect(self._open_settings)
        self.check_tools_button = QPushButton()
        self.check_tools_button.clicked.connect(self._check_tools)
        row = QHBoxLayout()
        row.addWidget(self.settings_button)
        row.addWidget(self.check_tools_button)
        row.addStretch()
        self.tool_form = layout
        self.operation_title_label = QLabel()
        self.language_title_label = QLabel()
        layout.addRow("adb.exe", self.adb_path_label)
        layout.addRow("scrcpy.exe", self.scrcpy_path_label)
        layout.addRow(self.operation_title_label, self.operation_label)
        layout.addRow(self.language_title_label, self.language_combo)
        layout.addRow(row)
        return self.tool_status_group

    def _build_profile_group(self) -> QGroupBox:
        self.profile_group = QGroupBox()
        layout = QFormLayout(self.profile_group)
        self.profile_form = layout
        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self._profile_changed)
        self.serial_combo = QComboBox()
        self.serial_combo.currentTextChanged.connect(self._serial_changed)
        self.add_profile_button = QPushButton()
        self.add_profile_button.clicked.connect(self._add_profile)
        self.edit_profile_button = QPushButton()
        self.edit_profile_button.clicked.connect(self._edit_profile)
        buttons = QHBoxLayout()
        buttons.addWidget(self.add_profile_button)
        buttons.addWidget(self.edit_profile_button)
        buttons.addStretch()
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("Example: 192.168.1.113")
        self.pair_port_edit = QLineEdit()
        self.pair_port_edit.setPlaceholderText("Example: 39631")
        self.connect_port_edit = QLineEdit()
        self.connect_port_edit.setPlaceholderText("Usually different from pair-port")
        self.device_status = DeviceStatusWidget(self.settings.language)
        self.profile_title_label = QLabel()
        self.ip_title_label = QLabel()
        self.pair_port_title_label = QLabel()
        self.connect_port_title_label = QLabel()
        self.serial_title_label = QLabel()
        self.status_title_label = QLabel()
        layout.addRow(self.profile_title_label, self.profile_combo)
        layout.addRow(buttons)
        layout.addRow(self.ip_title_label, self.ip_edit)
        layout.addRow(self.pair_port_title_label, self.pair_port_edit)
        layout.addRow(self.connect_port_title_label, self.connect_port_edit)
        self.serial_hint_label = QLabel()
        self.serial_hint_label.setWordWrap(True)
        layout.addRow(
            self.serial_title_label,
            self._field_with_hint(
                self.serial_combo,
                self.serial_hint_label,
            ),
        )
        layout.addRow(self.status_title_label, self.device_status)
        return self.profile_group

    def _build_connection_help_group(self) -> QGroupBox:
        self.connection_help_group = QGroupBox()
        layout = QVBoxLayout(self.connection_help_group)
        self.connection_help_label = QLabel()
        self.connection_help_label.setWordWrap(True)
        layout.addWidget(self.connection_help_label)
        return self.connection_help_group

    def _build_connection_group(self) -> QGroupBox:
        self.connection_group = QGroupBox()
        layout = QHBoxLayout(self.connection_group)
        self.pair_button = QPushButton()
        self.connect_button = QPushButton()
        self.disconnect_button = QPushButton()
        self.reset_adb_button = QPushButton()
        self.refresh_devices_button = QPushButton()
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
        return self.connection_group

    def _build_device_actions_group(self) -> QGroupBox:
        self.device_actions_group = QGroupBox()
        layout = QHBoxLayout(self.device_actions_group)
        self.scrcpy_button = QPushButton()
        self.scrcpy_auto_button = QPushButton()
        self.scrcpy_tcpip_button = QPushButton()
        self.install_apk_button = QPushButton()
        self.screenshot_button = QPushButton()
        self.device_info_button = QPushButton()
        self.shell_button = QPushButton()
        self.logcat_button = QPushButton()
        self.scrcpy_button.clicked.connect(self._launch_scrcpy)
        self.scrcpy_auto_button.clicked.connect(self._launch_scrcpy_auto)
        self.scrcpy_tcpip_button.clicked.connect(self._launch_scrcpy_tcpip)
        self.install_apk_button.clicked.connect(self._install_apk)
        self.screenshot_button.clicked.connect(self._screenshot)
        self.device_info_button.clicked.connect(self._device_info)
        self.shell_button.clicked.connect(self._open_shell)
        self.logcat_button.clicked.connect(
            lambda: QMessageBox.information(
                self, "Logcat", self._t("logcat_stub")
            )
        )
        for button in (
            self.scrcpy_button,
            self.scrcpy_auto_button,
            self.scrcpy_tcpip_button,
            self.install_apk_button,
            self.screenshot_button,
            self.device_info_button,
            self.shell_button,
            self.logcat_button,
        ):
            layout.addWidget(button)
        layout.addStretch()
        return self.device_actions_group

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
        self.device_status.set_status(self._status("ready"), self.current_serial)
        self.settings.last_device_profile_id = profile.id
        self._save()
        self._apply_enabled_state()

    def _serial_changed(self, serial: str) -> None:
        self.current_serial = serial or None
        self.device_connected = False
        self._apply_enabled_state()

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self.settings.language, self)
        if dialog.exec():
            previous_last_profile = self.settings.last_device_profile_id
            previous_language = self.settings.language
            self.settings = dialog.settings()
            self.settings.last_device_profile_id = previous_last_profile
            self.settings.language = previous_language
            self.adb_path_label.setText(self.settings.adb_path or "-")
            self.scrcpy_path_label.setText(self.settings.scrcpy_path or "-")
            self._save()
            self._apply_enabled_state()

    def _add_profile(self) -> None:
        dialog = DeviceProfileDialog(language=self.settings.language, parent=self)
        if dialog.exec():
            self.profiles.append(dialog.device_profile())
            self._save()
            self._load_profiles()

    def _edit_profile(self) -> None:
        profile = self._current_profile()
        if not profile:
            QMessageBox.warning(self, self._t("profile"), self._t("profile_missing"))
            return
        dialog = DeviceProfileDialog(profile, self.settings.language, self)
        if dialog.exec():
            self.profiles[self.profile_combo.currentIndex()] = dialog.device_profile()
            self._save()
            self._load_profiles()

    def _adb_runner(self) -> ADBRunner:
        return ADBRunner(Path(self.settings.adb_path), self.settings.language)

    def _scrcpy_runner(self) -> ScrcpyRunner:
        return ScrcpyRunner(Path(self.settings.scrcpy_path), self.settings.language)

    def _check_tools(self) -> None:
        self._run_worker(
            lambda: [self._adb_runner().version(), self._scrcpy_runner().version()],
            self._show_many_results,
            "Checking adb.exe and scrcpy.exe versions",
        )

    def _pair(self) -> None:
        target = self._validated_pair_target()
        if not target:
            return
        ip, pair_port = target
        code, ok = QInputDialog.getText(
            self, self._t("pairing_code_title"), self._t("pairing_code_prompt")
        )
        if not ok or not code.strip():
            return
        self._run_worker(
            lambda: self._adb_runner().pair(ip, pair_port, code.strip()),
            self._show_result,
            f"Pairing {ip}:{pair_port}",
        )

    def _connect(self) -> None:
        target = self._validated_connect_target()
        if not target:
            return
        ip, connect_port = target

        def task() -> list[CommandResult]:
            adb = self._adb_runner()
            connect_result = adb.connect(ip, connect_port)
            devices_result = adb.devices()
            return [connect_result, devices_result]

        self._run_worker(task, self._after_connect, f"Connecting {ip}:{connect_port}")

    def _disconnect(self) -> None:
        serial = self.current_serial
        self._run_worker(
            lambda: self._adb_runner().disconnect(serial), self._after_disconnect, "Disconnecting ADB device"
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

    def _launch_scrcpy_auto(self) -> None:
        profile = self._current_profile()
        extra_args = profile.scrcpy_args if profile else ""
        self._run_worker(
            lambda: self._scrcpy_runner().launch(None, extra_args),
            self._show_result,
            "Launching scrcpy auto-select",
        )

    def _launch_scrcpy_tcpip(self) -> None:
        target = self._validated_connect_target()
        if not target:
            return
        ip, connect_port = target
        profile = self._current_profile()
        extra_args = profile.scrcpy_args if profile else ""
        self._run_worker(
            lambda: self._scrcpy_runner().launch_tcpip(ip, connect_port, extra_args),
            self._show_result,
            f"Launching scrcpy --tcpip={ip}:{connect_port}",
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
            self, self._t("install_apk"), self._t("install_confirm").format(path=path)
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
        window = ShellWindow(self._adb_runner(), serial, self.settings.language, self)
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

    def _validated_pair_target(self) -> tuple[str, int] | None:
        ip = self.ip_edit.text().strip()
        pair_port = self.pair_port_edit.text().strip()
        for is_valid, error in (
            validate_ip_or_host(ip),
            validate_port(pair_port),
        ):
            if not is_valid:
                QMessageBox.warning(self, self._t("invalid_connection"), error)
                return None
        return ip, int(pair_port)

    def _validated_connect_target(self) -> tuple[str, int] | None:
        ip = self.ip_edit.text().strip()
        connect_port = self.connect_port_edit.text().strip()
        for is_valid, error in (
            validate_ip_or_host(ip),
            validate_port(connect_port),
        ):
            if not is_valid:
                QMessageBox.warning(self, self._t("invalid_connection"), error)
                return None
        return ip, int(connect_port)

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
        target = self._validated_connect_target()
        if not target:
            return
        ip, connect_port = target
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
            self.device_status.set_status(self._status("connected"), serial)
        else:
            self.device_connected = False
            self.device_status.set_status(self._status("error"), serial)
            QMessageBox.warning(
                self,
                self._t("device_not_connected_title"),
                self._t("device_not_connected_text"),
            )
        self._apply_enabled_state()

    def _after_disconnect(self, result: CommandResult) -> None:
        self._show_result(result)
        self.device_connected = False
        self.device_status.set_status(self._status("ready"), self.current_serial)
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
            self.device_status.set_status(self._status("connected"), self.current_serial)
        elif self.current_serial and states.get(self.current_serial) == "offline":
            self.device_connected = False
            self.device_status.set_status(self._status("offline"), self.current_serial)
        elif self.current_serial and states.get(self.current_serial) == "unauthorized":
            self.device_connected = False
            self.device_status.set_status(self._status("unauthorized"), self.current_serial)
        else:
            self.device_connected = False
            self.device_status.set_status(self._status("ready"), self.current_serial)
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
        self._operation_text = operation_text
        self.operation_label.setText(self._t("running").format(operation=operation_text))
        self._apply_enabled_state()
        worker.signals.finished.connect(lambda payload: self._finish_worker(payload, on_finished))
        worker.signals.failed.connect(lambda message: self._fail_worker(message))
        self.thread_pool.start(worker)

    def _finish_worker(self, payload: object, on_finished: Callable[[object], None]) -> None:
        self.operation_running = False
        self._operation_text = ""
        self.operation_label.setText(self._t("idle"))
        on_finished(payload)
        self._apply_enabled_state()

    def _fail_worker(self, message: str) -> None:
        self.operation_running = False
        self._operation_text = ""
        self.operation_label.setText(self._t("failed"))
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
        self.scrcpy_button.setEnabled(scrcpy_ready and bool(self.current_serial) and not self.operation_running)
        self.scrcpy_auto_button.setEnabled(scrcpy_ready and not self.operation_running)
        self.scrcpy_tcpip_button.setEnabled(scrcpy_ready and bool(self.ip_edit.text().strip()) and not self.operation_running)
        self.remote_widget.set_controls_enabled(adb_ready and can_use_device and not self.operation_running)

    def _save(self) -> None:
        self.store.save(self.settings, self.profiles)

    def _t(self, key: str) -> str:
        language = self.settings.language if self.settings.language in TRANSLATIONS else "en"
        return TRANSLATIONS[language].get(key, TRANSLATIONS["en"][key])

    def _language_changed(self) -> None:
        language = self.language_combo.currentData() or "en"
        self.settings.language = str(language)
        self._apply_language()
        self._save()

    def _apply_language(self) -> None:
        self.setWindowTitle(self._t("window_title"))
        self.tool_status_group.setTitle(self._t("tool_status"))
        self.settings_button.setText(self._t("settings"))
        self.check_tools_button.setText(self._t("check_tools"))
        self.operation_title_label.setText(self._t("current_operation"))
        self.language_title_label.setText(self._t("language"))
        self.operation_label.setText(
            self._t("running").format(operation=self._operation_text)
            if self.operation_running
            else self._t("idle")
        )

        self.connection_help_group.setTitle(self._t("how_to_connect"))
        self.connection_help_label.setText(self._t("connect_help"))

        self.profile_group.setTitle(self._t("device_profile"))
        self.profile_title_label.setText(self._t("profile"))
        self.add_profile_button.setText(self._t("add_profile"))
        self.edit_profile_button.setText(self._t("edit_profile"))
        self.ip_title_label.setText(self._t("ip"))
        self.pair_port_title_label.setText(self._t("pair_port"))
        self.connect_port_title_label.setText(self._t("connect_port"))
        self.serial_title_label.setText(self._t("serial"))
        self.status_title_label.setText(self._t("status"))
        self.serial_hint_label.setText(self._t("serial_hint"))

        self.connection_group.setTitle(self._t("connection_actions"))
        self.pair_button.setText(self._t("pair"))
        self.connect_button.setText(self._t("connect"))
        self.disconnect_button.setText(self._t("disconnect"))
        self.reset_adb_button.setText(self._t("reset_adb"))
        self.refresh_devices_button.setText(self._t("refresh_devices"))

        self.device_actions_group.setTitle(self._t("device_actions"))
        self.scrcpy_button.setText(self._t("launch_scrcpy"))
        self.scrcpy_auto_button.setText(self._t("launch_scrcpy_auto"))
        self.scrcpy_tcpip_button.setText(self._t("launch_scrcpy_tcpip"))
        self.install_apk_button.setText(self._t("install_apk"))
        self.screenshot_button.setText(self._t("screenshot"))
        self.device_info_button.setText(self._t("device_info"))
        self.shell_button.setText(self._t("open_shell"))
        self.logcat_button.setText(self._t("start_logcat"))

        self.remote_widget.set_language(self.settings.language)
        self.remote_group.setTitle(self._t("remote_control"))
        self.device_status.set_language(self.settings.language)
        self.log_widget.set_language(self.settings.language)
        self.log_group.setTitle(self._t("command_log"))

    def _status(self, key: str) -> str:
        return self._t(key)

    def _field_with_hint(self, field: QWidget, hint: QLabel | str) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.addWidget(field)
        label = hint if isinstance(hint, QLabel) else QLabel(hint)
        label.setWordWrap(True)
        label.setMaximumHeight(36)
        label.setStyleSheet("color: #555;")
        layout.addWidget(label)
        return container
