# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

# Add this to your .spec file
py_mini_racer_data = collect_data_files('py_mini_racer', include_py_files=True, subdir='_dll')


a = Analysis(
    ['run_app.py'],
    pathex=['.'],
    binaries=[(r'C:\aqua\firestone-lab\venv\Lib\site-packages\py_mini_racer\mini_racer.dll', '_dll')],
    datas=[('src', 'src'), *py_mini_racer_data],
    hiddenimports=['requests', 'pymongo', 'akshare'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='run_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
