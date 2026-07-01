# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_data_files

mysql_datas, mysql_binaries, mysql_hiddenimports = collect_all('mysql.connector')

datas = [('.env', '.')]
datas += collect_data_files('certifi')
datas += mysql_datas


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=mysql_binaries,
    datas=datas,
    hiddenimports=mysql_hiddenimports + ['openpyxl'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['streamlit', 'pandas', 'plotly'],
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
    name='transit-tracker',
    icon='assets/ez-track-icon.ico',
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
