# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run_app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('./venv/Lib/site-packages/py_mini_racer/mini_racer.dll', '.'),
        ('./venv/Lib/site-packages/py_mini_racer/icudtl.dat', '.'), 
        ('./venv/Lib/site-packages/py_mini_racer/snapshot_blob.bin', '.'),
        ('./venv/Lib/site-packages/akshare/file_fold/calendar.json', './akshare/file_fold/'),
        ('src', 'src')
    ],
    hiddenimports=['requests', 'pymongo', 'akshare', 'logging', 'logging.handlers'],
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
