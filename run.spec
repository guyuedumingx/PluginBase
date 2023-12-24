# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pandas','numpy','openpyxl','fastapi','requests','uvicorn', 'cx-Oracle'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Users\\11319\\AppData\\Local\\Temp\\d42ab5a8-5702-4d9c-8db6-16da00f39207',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    hiddenimports=a.hiddenimports,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='run',
    icons="assets/icons/BOC.png"
)
