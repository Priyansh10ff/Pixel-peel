# -*- mode: python ; coding: utf-8 -*-
"""
PixelPeel — PyInstaller Spec
=============================
Builds a self-contained desktop application that requires no Python
installation from the end user.

  Windows  →  dist/PixelPeel/PixelPeel.exe
  macOS    →  dist/PixelPeel.app
  Linux    →  dist/PixelPeel/PixelPeel

Run via the build scripts:
  Windows :  build.bat
  macOS / Linux:  ./build.sh

Or directly:
  pyinstaller pixelpeel.spec --noconfirm
"""
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(SPECPATH)  # noqa: F821 — SPECPATH is injected by PyInstaller

# ── Data files ────────────────────────────────────────────────────────────────
# customtkinter ships theme JSON files, fonts, and images that must travel
# alongside the binary — PyInstaller won't discover them automatically.
datas = collect_data_files("customtkinter")

# Include the assets folder (icon PNG used at runtime if needed)
assets_src = ROOT / "assets"
if assets_src.exists():
    datas += [(str(assets_src), "assets")]

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # OpenCV loads its C extensions dynamically
        "cv2",
        # Pillow Tk bridge
        "PIL._tkinter_finder",
        # Ensure src package tree is walked
        "src",
        "src.processor",
        "src.ui",
        "src.ui.app",
        "src.ui.themes",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Trim fat we don't use — reduces binary size ~15–20 MB
    excludes=[
        "tkinter.test",
        "unittest",
        "email",
        "xml",
        "html",
        "http",
        "urllib",
        "multiprocessing",
        "concurrent",
        "asyncio",
        "sqlite3",
        "distutils",
        "pydoc",
        "doctest",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)  # noqa: F821

# ── Platform icon ─────────────────────────────────────────────────────────────
if sys.platform == "win32":
    _icon = str(ROOT / "assets" / "pixelpeel.ico")
else:
    _icon = str(ROOT / "assets" / "pixelpeel.png")

_icon = _icon if Path(_icon).exists() else None

# ── Executable ────────────────────────────────────────────────────────────────
exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PixelPeel",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,        # ← no terminal window when double-clicked
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
)

# ── Collect (one-dir mode — faster startup than --onefile) ────────────────────
coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PixelPeel",
)

# ── macOS: wrap in a proper .app bundle ───────────────────────────────────────
if sys.platform == "darwin":
    app = BUNDLE(  # noqa: F821
        coll,
        name="PixelPeel.app",
        icon=_icon,
        bundle_identifier="com.pixelpeel.app",
        info_plist={
            "CFBundleShortVersionString": "1.0.0",
            "CFBundleVersion": "1.0.0",
            "NSHighResolutionCapable": True,
            "NSRequiresAquaSystemAppearance": False,  # allow dark mode
        },
    )
