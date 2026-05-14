import os
import struct
import zlib

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton, QLabel

_app = QApplication.instance() or QApplication([])

from app.ui.dialogs.screenshot_preview_dialog import ScreenshotPreviewDialog


def _minimal_png() -> bytes:
    """1×1 white PNG."""
    def _chunk(name: bytes, data: bytes) -> bytes:
        c = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", c)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    raw = b"\x00\xff\xff\xff"
    compressed = zlib.compress(raw)
    idat = _chunk(b"IDAT", compressed)
    iend = _chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


def test_dialog_constructs_with_valid_png(tmp_path):
    png = _minimal_png()
    path = str(tmp_path / "screenshot_2026-05-14_12-00-00.png")
    dlg = ScreenshotPreviewDialog(png, path, None)
    assert dlg is not None


def test_dialog_constructs_with_empty_bytes(tmp_path):
    path = str(tmp_path / "screenshot_2026-05-14_12-00-00.png")
    dlg = ScreenshotPreviewDialog(b"", path, None)
    labels = dlg.findChildren(QLabel)
    texts = [lbl.text() for lbl in labels]
    assert any("unavailable" in t.lower() or "Preview" in t for t in texts)


def test_open_folder_button_exists(tmp_path):
    path = str(tmp_path / "screenshot_2026-05-14_12-00-00.png")
    dlg = ScreenshotPreviewDialog(b"", path, None)
    buttons = dlg.findChildren(QPushButton)
    texts = [b.text() for b in buttons]
    assert any("folder" in t.lower() or "папк" in t.lower() for t in texts)


def test_open_folder_button_is_enabled(tmp_path):
    path = str(tmp_path / "screenshot_2026-05-14_12-00-00.png")
    dlg = ScreenshotPreviewDialog(b"", path, None)
    buttons = dlg.findChildren(QPushButton)
    folder_btns = [b for b in buttons if "folder" in b.text().lower() or "папк" in b.text().lower()]
    assert folder_btns
    assert folder_btns[0].isEnabled()
