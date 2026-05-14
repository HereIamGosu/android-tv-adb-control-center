from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)

from app.core.adb_runner import ADBRunner
from app.core.settings_store import SettingsStore


class _Signals(QObject):
    finished = Signal(str)
    failed = Signal(str)


class _CheckWorker(QRunnable):
    def __init__(self, fn):
        super().__init__()
        self.setAutoDelete(False)
        self.fn = fn
        self.signals = _Signals()

    @Slot()
    def run(self) -> None:
        try:
            result = self.fn()
            self.signals.finished.emit(result.stdout or result.stderr or "OK")
        except Exception as exc:
            self.signals.failed.emit(str(exc))


class _AdbPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 1: ADB path")
        self.setSubTitle("Select adb.exe from Android SDK Platform Tools.")
        self._worker: _CheckWorker | None = None

        self._field = QLineEdit()
        self._field.setPlaceholderText("Path to adb.exe")
        self._field.textChanged.connect(self.completeChanged)
        browse = QPushButton("Browse...")
        browse.clicked.connect(self._browse)
        self._check = QPushButton("Check")
        self._check.clicked.connect(self._run_check)
        self._result_label = QLabel()
        self._result_label.setWordWrap(True)

        row = QHBoxLayout()
        row.addWidget(self._field, 1)
        row.addWidget(browse)
        row.addWidget(self._check)
        layout = QVBoxLayout(self)
        layout.addLayout(row)
        layout.addWidget(self._result_label)

        self.registerField("adb_path*", self._field)

    def isComplete(self) -> bool:
        return bool(self._field.text().strip())

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select adb.exe", "", "Executable (*.exe)")
        if path:
            self._field.setText(path)

    def _run_check(self) -> None:
        adb_path = self._field.text().strip()
        if not adb_path:
            return
        self._check.setEnabled(False)
        self._result_label.setText("Checking...")
        runner = ADBRunner(Path(adb_path))
        self._worker = _CheckWorker(runner.version)
        self._worker.signals.finished.connect(self._on_done)
        self._worker.signals.failed.connect(self._on_failed)
        QThreadPool.globalInstance().start(self._worker)

    def _on_done(self, text: str) -> None:
        self._check.setEnabled(True)
        self._result_label.setText(text.strip()[:200])

    def _on_failed(self, text: str) -> None:
        self._check.setEnabled(True)
        self._result_label.setText(f"Error: {text}")


class _ScrcpyPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 2: scrcpy path")
        self.setSubTitle("Select scrcpy.exe, or check 'I don't use scrcpy' to skip.")
        self._worker: _CheckWorker | None = None

        self._skip_cb = QCheckBox("I don't use scrcpy")
        self._skip_cb.toggled.connect(self._toggle_skip)

        self._field = QLineEdit()
        self._field.setPlaceholderText("Path to scrcpy.exe (optional)")
        self._browse_btn = QPushButton("Browse...")
        self._browse_btn.clicked.connect(self._browse)
        self._check_btn = QPushButton("Check")
        self._check_btn.clicked.connect(self._run_check)
        self._result_label = QLabel()
        self._result_label.setWordWrap(True)

        row = QHBoxLayout()
        row.addWidget(self._field, 1)
        row.addWidget(self._browse_btn)
        row.addWidget(self._check_btn)
        layout = QVBoxLayout(self)
        layout.addWidget(self._skip_cb)
        layout.addLayout(row)
        layout.addWidget(self._result_label)

        self.registerField("scrcpy_path", self._field)

    def _toggle_skip(self, checked: bool) -> None:
        self._field.setEnabled(not checked)
        self._browse_btn.setEnabled(not checked)
        self._check_btn.setEnabled(not checked)
        if checked:
            self._field.clear()

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select scrcpy.exe", "", "Executable (*.exe)")
        if path:
            self._field.setText(path)

    def _run_check(self) -> None:
        from app.core.scrcpy_runner import ScrcpyRunner
        scrcpy_path = self._field.text().strip()
        if not scrcpy_path:
            return
        self._check_btn.setEnabled(False)
        self._result_label.setText("Checking...")
        runner = ScrcpyRunner(Path(scrcpy_path))
        self._worker = _CheckWorker(runner.version)
        self._worker.signals.finished.connect(self._on_done)
        self._worker.signals.failed.connect(self._on_failed)
        QThreadPool.globalInstance().start(self._worker)

    def _on_done(self, text: str) -> None:
        self._check_btn.setEnabled(True)
        self._result_label.setText(text.strip()[:200])

    def _on_failed(self, text: str) -> None:
        self._check_btn.setEnabled(True)
        self._result_label.setText(f"Error: {text}")


class _FolderPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 3: Screenshot folder")
        self.setSubTitle("Choose where screenshots will be saved.")

        default = str(Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Pictures" / "ADBScreenshots")
        self._field = QLineEdit(default)
        browse = QPushButton("Browse...")
        browse.clicked.connect(self._browse)

        row = QHBoxLayout()
        row.addWidget(self._field, 1)
        row.addWidget(browse)
        layout = QVBoxLayout(self)
        layout.addLayout(row)

        self.registerField("screenshot_folder", self._field)

    def _browse(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select screenshot folder")
        if folder:
            self._field.setText(folder)


class SetupWizard(QWizard):
    def __init__(self, store: SettingsStore, parent=None):
        super().__init__(parent)
        self._store = store
        self.setWindowTitle("First-time Setup")
        self.setMinimumSize(520, 320)

        self.addPage(_AdbPage(self))
        self.addPage(_ScrcpyPage(self))
        self.addPage(_FolderPage(self))

        self.finished.connect(self._on_finish)

    def _on_finish(self, result: int) -> None:
        if result != QWizard.DialogCode.Accepted:
            return
        doc = self._store.load()
        settings = doc.settings
        settings.adb_path = self.field("adb_path") or ""
        settings.scrcpy_path = self.field("scrcpy_path") or ""
        settings.default_screenshot_dir = self.field("screenshot_folder") or ""
        self._store.save(settings, doc.profiles)
