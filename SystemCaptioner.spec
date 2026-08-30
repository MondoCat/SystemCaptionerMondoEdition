# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('icon.ico', '.'), ('cat.ico', '.'), ('border.png', '.'), ('cat.png', '.'), ('transcriber.py', '.'), ('recorder.py', '.'), ('console.py', '.'), ('C:\\Users\\caitnonwiggly\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\faster_whisper\\assets', 'faster_whisper/assets')]
binaries = []
hiddenimports = ['queue', 'gui', 'configparser', 'customtkinter', 'setupGUI', 'torch', 'whisper', 'numpy', 'pyaudio', 'threading', 'transcriber', 'recorder', 'console', 'sounddevice', 'wave', 'scipy', 'faster_whisper', 'ctypes', 'win32gui']
tmp_ret = collect_all('whisper')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('torch')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('faster_whisper')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='SystemCaptioner',
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
    icon=['F:\\Z_Unsorted\\SystemCaptioner\\SC\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SystemCaptioner',
)
