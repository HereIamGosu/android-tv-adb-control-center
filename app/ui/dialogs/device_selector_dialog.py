from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.core.adb_runner import ADBRunner, parse_adb_devices
from app.core.device_profile import DeviceProfile


class _WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class _Worker(QRunnable):
    def __init__(self, fn):
        super().__init__()
        self.setAutoDelete(False)
        self.fn = fn
        self.signals = _WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            self.signals.finished.emit(self.fn())
        except Exception as exc:
            self.signals.failed.emit(str(exc))


class DeviceSelectorDialog(QDialog):
    def __init__(
        self,
        profiles: list[DeviceProfile],
        connected_serials: list[tuple[str, str]],
        adb_runner: ADBRunner,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Select Device")
        self.resize(640, 320)
        self._profiles = profiles
        self._adb_runner = adb_runner
        self._worker: _Worker | None = None
        self.selected_serial: str | None = None

        self._build_ui()
        self._populate(connected_serials)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Profile Name", "Serial", "IP", "Status"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        self._refresh_button = QPushButton("Refresh")
        self._refresh_button.clicked.connect(self._refresh)
        self._select_button = QPushButton("Select")
        self._select_button.clicked.connect(self._select)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(self._refresh_button)
        buttons.addStretch()
        buttons.addWidget(self._select_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)

    def _populate(self, devices: list[tuple[str, str]]) -> None:
        serial_to_name: dict[str, str] = {}
        for profile in self._profiles:
            if profile.last_serial:
                serial_to_name[profile.last_serial] = profile.name
            if profile.ip and profile.connect_port:
                serial_to_name[f"{profile.ip}:{profile.connect_port}"] = profile.name

        self.table.setRowCount(len(devices))
        for row, (serial, state) in enumerate(devices):
            name = serial_to_name.get(serial, "—")
            ip = serial.split(":")[0] if ":" in serial else serial
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(serial))
            self.table.setItem(row, 2, QTableWidgetItem(ip))
            self.table.setItem(row, 3, QTableWidgetItem(state))

    def _refresh(self) -> None:
        self._refresh_button.setEnabled(False)
        self._worker = _Worker(self._adb_runner.devices)
        self._worker.signals.finished.connect(self._on_refresh_done)
        self._worker.signals.failed.connect(self._on_refresh_failed)
        QThreadPool.globalInstance().start(self._worker)

    def _on_refresh_done(self, result) -> None:
        self._refresh_button.setEnabled(True)
        entries = parse_adb_devices(result.stdout)
        devices = [(e.serial, e.state) for e in entries]
        self._populate(devices)

    def _on_refresh_failed(self, _message: str) -> None:
        self._refresh_button.setEnabled(True)

    def _select(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            item = self.table.item(row, 1)
            if item:
                self.selected_serial = item.text()
        self.accept()
