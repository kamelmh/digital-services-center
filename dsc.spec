# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for DSC Desktop App.
Build command: pyinstaller dsc.spec
"""

block_cipher = None

a = Analysis(
    ['desktop_app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('pages', 'pages'),
        ('brand', 'brand'),
        ('assets', 'assets'),
        ('feasibility', 'feasibility'),
        ('feasibility/sectors', 'feasibility/sectors'),
        ('gallery', 'gallery'),
    ],
    hiddenimports=[
        'violit',
        'reportlab',
        'arabic_reshaper',
        'bidi',
        'requests',
        'pydantic',
        'fastapi',
        'uvicorn',
        'json',
        'dataclasses',
        'datetime',
        'typing',
        'pathlib',
        'offline_templates',
        'financial_calculators',
        'nesda_calculator',
        'policy_constants',
        'dsc_utils',
        'feasibility_generator',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DSC_Digital_Services_Center',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='brand/assets/dsc-icon.ico',  # Uncomment when icon is ready
)
