#!/usr/bin/env python3
"""
PixelPeel — AI-Powered Local Background Remover
================================================
Runs 100% on your machine. Your images never leave your PC.

Usage:
    python main.py
"""
import sys
import os


def check_python_version():
    if sys.version_info < (3, 9):
        print("❌  Python 3.9+ is required.")
        print(f"   You have: Python {sys.version.split()[0]}")
        sys.exit(1)


def check_dependencies():
    """Verify all required packages are installed."""
    required = {
        "customtkinter": "customtkinter>=5.2.0",
        "PIL":           "Pillow>=10.0.0",
        "rembg":         "rembg[gpu]",
        "numpy":         "numpy>=1.24.0",
    }
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        print("\n❌  Missing dependencies detected:\n")
        for pkg in missing:
            print(f"   • {pkg}")
        print(f"\n   Run:  pip install {' '.join(missing)}\n")
        sys.exit(1)


def main():
    check_python_version()
    check_dependencies()

    from src.ui.app import PixelPeelApp

    app = PixelPeelApp()
    app.run()


if __name__ == "__main__":
    main()
