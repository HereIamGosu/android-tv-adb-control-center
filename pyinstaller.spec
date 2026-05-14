# pyinstaller.spec
block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['PySide6.QtSvg', 'PySide6.QtXml'],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'unittest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='AndroidTVADBControlCenter',
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon=None,
)
