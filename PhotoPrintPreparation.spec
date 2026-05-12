# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import sys


project_root = Path.cwd().resolve()
src_root = project_root / "src"
sys.path.insert(0, str(src_root))

python_dll_name = f"python{sys.version_info.major}{sys.version_info.minor}.dll"
python_dll_path = Path(sys.base_prefix) / python_dll_name
bundled_binaries = []
if python_dll_path.exists():
    bundled_binaries.append((str(python_dll_path), "."))

from photo_processor.bootstrap.build_embedded_oauth import build_embedded_oauth_module


embedded_oauth_module = build_embedded_oauth_module()
if not embedded_oauth_module.exists():
    raise RuntimeError(
        "Portable build requires embedded Google OAuth credentials. "
        "Generate src/photo_processor/config/cloud_oauth_embedded.py before packaging."
    )


a = Analysis(
    ["src\\photo_processor\\api\\gui_app.py"],
    pathex=["src"],
    binaries=bundled_binaries,
    datas=[("src/photo_processor/gui/assets", "photo_processor/gui/assets")],
    hiddenimports=["photo_processor.config.cloud_oauth_embedded"],
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
    name="PhotoPrintPreparation",
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PhotoPrintPreparation",
)
