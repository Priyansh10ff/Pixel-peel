#!/usr/bin/env python3
"""
PixelPeel — AI-Powered Local Background Remover
================================================
Runs 100% on your machine. Your images never leave your PC.

Usage:
    python main.py
"""
# ── MUST be set before ANY other import ───────────────────────────────────────
# rembg depends on pymatting which uses numba for JIT compilation.
# On Python 3.12 (and slow on any version at first launch), this JIT step
# causes a very long hang or an outright crash.
# Setting NUMBA_DISABLE_JIT=1 makes pymatting fall back to pure Python.
# The actual background removal is done by ONNX Runtime — this has zero
# effect on removal quality or speed.
import os
os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
os.environ.setdefault("NUMBA_CACHE_DIR", os.path.join(os.path.expanduser("~"), ".cache", "numba"))

import sys


def check_python_version():
    if sys.version_info < (3, 9):
        print("❌  Python 3.9+ is required.")
        print(f"   You have: Python {sys.version.split()[0]}")
        sys.exit(1)


def check_dependencies():
    """Verify all required packages are installed (without importing them)."""
    import importlib.util

    required = {
        "customtkinter": "customtkinter>=5.2.0",
        "PIL":           "Pillow>=10.0.0",
        "rembg":         "rembg",
        "numpy":         "numpy>=1.24.0",
    }
    missing = []
    for module, package in required.items():
        if importlib.util.find_spec(module) is None:
            missing.append(package)

    if missing:
        print("\n❌  Missing dependencies detected:\n")
        for pkg in missing:
            print(f"   • {pkg}")
        print(f"\n   Run:  pip install {' '.join(p.split('>=')[0] for p in missing)}\n")
        sys.exit(1)


def main():
    check_python_version()
    check_dependencies()

    from src.ui.app import PixelPeelApp

    app = PixelPeelApp()
    app.run()


if __name__ == "__main__":
    main()
