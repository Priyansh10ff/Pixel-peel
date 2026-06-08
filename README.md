<div align="center">

<h1>PixelPeel</h1>

<p>Background removal that runs entirely on your machine.<br/>No cloud. No AI. No subscription.</p>

[![CI](https://github.com/Priyansh10ff/pixelpeel/actions/workflows/ci.yml/badge.svg)](https://github.com/Priyansh10ff/pixelpeel/actions/workflows/ci.yml)
[![Release](https://github.com/Priyansh10ff/pixelpeel/actions/workflows/release.yml/badge.svg)](https://github.com/Priyansh10ff/pixelpeel/releases)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](#installation)

</div>

---

## Overview

PixelPeel is a desktop application for removing image backgrounds using classical computer vision. It runs 100% locally using OpenCV's GrabCut algorithm — no internet connection, no API keys, no model downloads, and no data ever leaves your machine.

The app installs like any other desktop application. On Windows, double-click `install.bat` and a shortcut appears on your Desktop. That's the entire setup.

---

## Features

- **Fully offline** — no network requests at any point
- **No AI or neural networks** — pure OpenCV, deterministic results
- **Four algorithms** — GrabCut, GrabCut HD, Edge Refine, Color Range
- **Batch processing** — process entire folders at once
- **Before / after split view** — drag to compare
- **Multiple output formats** — PNG (transparent), JPEG, WebP
- **Dark and light themes**
- **One-click installer** — creates a native desktop shortcut

---

## Installation

> **No Python required** if you use the pre-built download below.

### Download (recommended)

Go to the [Releases](https://github.com/Priyansh10ff/pixelpeel/releases) page and download the file for your platform:

| Platform | File | Steps |
|---|---|---|
| Windows 10/11 | `PixelPeel-Windows.zip` | Extract → double-click `PixelPeel.exe` |
| macOS 12+ | `PixelPeel-macOS.zip` | Extract → move `PixelPeel.app` to Applications |
| Linux | `PixelPeel-Linux.tar.gz` | Extract → run `./PixelPeel/PixelPeel` |

### From source (requires Python 3.9+)

```bash
git clone https://github.com/Priyansh10ff/pixelpeel.git
cd pixelpeel
```

**Windows**
```
install.bat
```

**macOS / Linux**
```bash
chmod +x install.sh && ./install.sh
```

A desktop shortcut is created automatically. No need to use the terminal again after this.

---

## Algorithms

| Algorithm | Best for | Speed |
|---|---|---|
| GrabCut | General subjects, portraits, products | Fast |
| GrabCut HD | Hair, fur, complex edges | Slow |
| Edge Refine | Geometric objects with hard edges | Fast |
| Color Range | Solid or gradient backgrounds | Fastest |

GrabCut models foreground and background as Gaussian Mixture Models and solves a min-cut graph — no neural network involved. It runs in pure C++ inside OpenCV and produces consistent, reproducible results on every machine.

---

## Development

```bash
# Setup
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run
python main.py

# Test
pip install pytest
pytest

# Lint & format
pip install ruff black
ruff check .
black .
```

### Build a distributable

```bash
# Windows
build.bat

# macOS / Linux
chmod +x build.sh && ./build.sh
```

Output is placed in `dist/` as a zip or tarball ready to upload to GitHub Releases.

---

## Project structure

```
pixelpeel/
├── main.py                 Entry point
├── install.bat             Windows installer
├── install.sh              macOS / Linux installer
├── build.bat               Windows PyInstaller build
├── build.sh                macOS / Linux PyInstaller build
├── pixelpeel.spec          PyInstaller configuration
├── requirements.txt
├── assets/
│   └── create_icon.py      Generates app icon at install/build time
├── src/
│   ├── processor.py        CV engine (GrabCut, Edge Refine, Color Range)
│   └── ui/
│       ├── app.py          CustomTkinter interface
│       └── themes.py       Light and dark colour palettes
└── tests/
    └── test_processor.py
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| opencv-python | ≥ 4.8 | Segmentation algorithms |
| Pillow | ≥ 10.3 | Image I/O and compositing |
| customtkinter | ≥ 5.2.2 | UI framework |
| numpy | ≥ 1.26 | Array operations |

---

## Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m "feat: description"`
4. Push and open a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for more detail.

---

## License

MIT — see [LICENSE](LICENSE) for details.
