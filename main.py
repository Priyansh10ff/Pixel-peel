#!/usr/bin/env python3
"""
PixelPeel — Local Background Remover
======================================
Runs 100% on your machine using classical computer vision.
No AI, no neural networks, no cloud uploads.

Usage:
    python main.py
"""

import sys


def check_dependencies():
    """Verify all required packages are installed (without importing them)."""
    import importlib.util

    required = {
        "cv2": "opencv-python>=4.8.0",
        "customtkinter": "customtkinter>=5.2.2",
        "PIL": "Pillow>=10.0.0",
        "numpy": "numpy>=1.26.0",
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
    check_dependencies()

    from src.ui.app import PixelPeelApp

    app = PixelPeelApp()
    app.run()


if __name__ == "__main__":
    main()
