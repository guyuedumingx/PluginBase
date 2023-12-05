# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/fonts/LXGWWenKai-Regular.ttf', 'assets/fonts')
    ],
    hiddenimports=['pandas', 'numpy', 'openpyxl', 'fastapi', 'requests', 'uvicorn'],
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
    a.binaries,
    a.datas,
    [],
    name='tools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='tools.app',
    icon='assets/icons/icon.ico',
    bundle_identifier=None,
)