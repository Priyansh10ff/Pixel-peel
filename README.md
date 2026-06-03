<div align="center">

<br/>

```
██████╗ ██╗██╗  ██╗███████╗██╗     ██████╗ ███████╗███████╗██╗
██╔══██╗██║╚██╗██╔╝██╔════╝██║     ██╔══██╗██╔════╝██╔════╝██║
██████╔╝██║ ╚███╔╝ █████╗  ██║     ██████╔╝█████╗  █████╗  ██║
██╔═══╝ ██║ ██╔██╗ ██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══╝  ██║
██║     ██║██╔╝ ██╗███████╗███████╗██║     ███████╗███████╗███████╗
╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚══════╝╚══════╝
```

### AI-Powered Background Remover — 100% Local · Zero Cloud · Zero Compromise

<br/>

[![CI](https://github.com/yourusername/pixelpeel/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/pixelpeel/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?logo=windows&logoColor=white)](https://github.com/yourusername/pixelpeel)
[![License: MIT](https://img.shields.io/badge/License-MIT-6C5CE7.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

<br/>

> **Your images stay on your machine. Always.**
>
> PixelPeel removes backgrounds using state-of-the-art deep learning — entirely offline,
> with no API keys, no subscriptions, and no data ever leaving your PC.

<br/>

</div>

---

## Table of Contents

- [Why PixelPeel?](#-why-pixelpeel)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [AI Models](#-ai-models)
- [Themes](#-themes)
- [Project Structure](#-project-structure)
- [Running Tests](#-running-tests)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## ✦ Why PixelPeel?

Most background-removal tools send your images to a remote server for processing.
This is a problem when working with sensitive, proprietary, or personal imagery.

PixelPeel solves this completely. After a one-time model download (~170 MB),
**every single operation runs on your own CPU or GPU**, with zero network traffic.

| | PixelPeel | Cloud tools |
|---|---|---|
| **Privacy** | ✅ 100% local — images never leave your machine | ❌ Uploaded to remote servers |
| **Cost** | ✅ Free forever, no account needed | ❌ Subscription or per-image fees |
| **Offline** | ✅ Works without internet after setup | ❌ Requires connectivity |
| **Speed** | ✅ No upload/download latency | ❌ Dependent on network speed |
| **Batch** | ✅ Unlimited images, no rate limits | ❌ Often capped per plan |

---

## ✦ Features

### Core
- **Single-image mode** — process one image at a time with a live before/after preview
- **Batch mode** — queue individual files or entire folders; per-row status tracking
- **Interactive split-preview** — drag the slider to compare original and result side by side
- **Four AI models** — choose the right engine for your use case (see [AI Models](#-ai-models))
- **Three output formats** — `PNG` (transparent), `JPEG`, `WEBP`
- **Background fill** — keep it transparent, fill with white, or pick any custom colour

### UI / UX
- **Dual themes** — toggle between **Midnight** (dark) and **Frost** (light) instantly
- **Animated progress bar** — real-time percentage feedback during processing
- **Status bar** — active model name, total processed count, app version
- **Drag-and-drop** *(requires `tkinterdnd2`)* — drop files directly onto the window
- **Responsive layout** — resizes gracefully from 900×580 to full screen

### Developer
- **Full test suite** — 20+ unit tests covering the processor, save logic, and session caching
- **GitHub Actions CI** — lint + test matrix across Python 3.9–3.12 on Windows, macOS, Linux
- **Type-annotated source** — fully typed with `from __future__ import annotations`
- **Zero vendor lock-in** — built on open-source libraries with no proprietary dependencies

---

## ✦ Quick Start

### Windows

```batch
git clone https://github.com/Priyansh10ff/Pixel-peel
cd pixelpeel
install_and_run.bat
```

### macOS / Linux

```bash
git clone https://github.com/Priyansh10ff/Pixel-peel
cd pixelpeel
chmod +x install_and_run.sh && ./install_and_run.sh
```

> **First launch:** The selected AI model (~170 MB) downloads once and is cached at
> `~/.u2net/`. All subsequent launches are fully offline.

---

## ✦ Installation

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.9 or newer |
| pip | latest recommended |
| OS | Windows 10/11, macOS 12+, Ubuntu 20.04+ |

### Step-by-step

```bash
# 1. Clone the repository
git clone https://github.com/Priyansh10ff/Pixel-peel
cd pixelpeel

# 2. (Recommended) Create a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch PixelPeel
python main.py
```

### Optional: GPU Acceleration

If you have an NVIDIA GPU with CUDA, replace `onnxruntime` with the GPU variant for
significantly faster inference:

```bash
pip uninstall onnxruntime -y
pip install onnxruntime-gpu
```

### Optional: Native Drag-and-Drop

```bash
pip install tkinterdnd2
```

---

## ✦ Usage Guide

### Single Image

1. Launch PixelPeel — the **Single Image** tab is active by default.
2. **Click the drop zone** (or drag a file onto it if `tkinterdnd2` is installed).
3. Select your AI model and output settings in the left sidebar.
4. Click **▶ Remove Background**.
5. Drag the **split-preview slider** to compare the original and result.
6. Click **💾 Save Result** to export to a custom location, or find the auto-saved
   file in your configured output folder.

### Batch Processing

1. Switch to the **Batch Process** tab.
2. Click **＋ Add Images** to select individual files, or **📁 Add Folder** to enqueue
   an entire directory.
3. Verify the output folder in the sidebar.
4. Click **▶ Process All** — each row updates with ✓ (success) or ✗ (error) in real time.

### Sidebar Controls

| Control | Description |
|---|---|
| **AI Model** | Choose between Standard, Portrait, Precision, or Ultra |
| **Output Format** | PNG (transparent) · JPEG · WEBP |
| **Background** | Transparent · White · Custom colour picker |
| **Output Folder** | Click 📁 to browse, or type a path directly |
| **☀ / 🌙 button** | Toggle Frost / Midnight theme |

---

## ✦ AI Models

PixelPeel exposes four inference models via [rembg](https://github.com/danielgatis/rembg).
All models are downloaded once and cached locally.

| Model | Name in UI | Best For | Speed | Quality |
|---|---|---|---|---|
| `u2net` | **Standard** | General images, products, animals | ⚡⚡⚡ Fast | ★★★★ |
| `u2net_human_seg` | **Portrait** | Selfies, portraits, people | ⚡⚡⚡ Fast | ★★★★ |
| `isnet-general-use` | **Precision** | Complex edges, hair, fur, fine detail | ⚡⚡ Medium | ★★★★★ |
| `birefnet-general` | **Ultra** | Maximum fidelity, professional use | ⚡ Slower | ★★★★★ |

> **Tip:** Start with **Standard**. Switch to **Precision** or **Ultra** only when
> edges need extra sharpness — they produce exceptional results but take longer,
> especially on CPU.

---

## ✦ Themes

PixelPeel ships with two hand-crafted colour palettes toggled instantly with the
`☀ / 🌙` button in the top-right corner of the sidebar.

### 🌙 Midnight (Dark)
Deep-space background (`#0D0D0F`) with electric violet (`#7C6FF7`) and mint (`#4ECDC4`)
accents. Easy on the eyes during long sessions.

### ☀ Frost (Light)
Arctic white surfaces (`#F0F3FA`) with violet (`#6C5CE7`) and teal (`#00B894`) accents.
Clean and airy for bright environments.

Both themes adapt every surface — sidebar, cards, canvas, status bar, progress bars,
labels, and buttons — without requiring an app restart.

---

## ✦ Project Structure

```
pixelpeel/
│
├── main.py                         # Entry point: version check → launch
│
├── src/
│   ├── __init__.py
│   ├── processor.py                # AI engine — rembg wrapper + model management
│   └── ui/
│       ├── __init__.py
│       ├── app.py                  # PixelPeelApp — full UI (single + batch + preview)
│       └── themes.py               # Colour palette (Midnight / Frost) + helpers
│
├── tests/
│   ├── __init__.py
│   └── test_processor.py           # 20+ unit tests — no GPU required (rembg mocked)
│
├── output/                         # Default output directory
│   └── .gitkeep
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml                  # CI: lint → test matrix (3 OS × 4 Python versions)
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   └── feature_request.yml
│   └── PULL_REQUEST_TEMPLATE.md
│
├── install_and_run.bat             # Windows one-click installer + launcher
├── install_and_run.sh              # macOS / Linux one-click installer + launcher
├── requirements.txt                # Runtime dependencies
├── pyproject.toml                  # Build metadata, tool config (black, ruff, pytest)
├── CHANGELOG.md                    # Version history (Keep a Changelog format)
├── CONTRIBUTING.md                 # Contributor guide
└── LICENSE                         # MIT
```

---

## ✦ Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=term-missing

# Run a specific class
pytest tests/test_processor.py::TestApplyBg -v

# Run a specific test
pytest tests/test_processor.py::TestSave::test_saves_png -v
```

All tests mock `rembg` and `onnxruntime` — no GPU, no model download, no internet
required. Safe to run in any CI environment.

---

## ✦ Contributing

Contributions are warmly welcomed! Please read [CONTRIBUTING.md](CONTRIBUTING.md)
for the full guide, including:

- Development environment setup
- Code style requirements (`ruff` + `black`)
- How to run tests
- PR checklist

To get started quickly:

```bash
git clone https://github.com/Priyansh10ff/Pixel-peel
cd pixelpeel
pip install -r requirements.txt ruff black pytest pytest-cov
git checkout -b feat/your-feature
```

---

## ✦ Roadmap

The following improvements are planned for future releases:

- [ ] **CLI mode** — headless usage via `pixelpeel --input img.jpg --output out.png`
- [ ] **Keyboard shortcuts** — `Space` to process, `Ctrl+S` to save, `Ctrl+O` to open
- [ ] **Export presets** — save and reuse model + format + background combinations
- [ ] **HEIC / AVIF input** — support for Apple and modern web formats
- [ ] **Custom background image** — composite the subject onto any background photo
- [ ] **Zoom & pan** in the preview panel
- [ ] **Undo / Redo** stack

Want to work on one of these? Check [open issues](https://github.com/yourusername/pixelpeel/issues)
or open a new feature request.

---

## ✦ License

PixelPeel is released under the **MIT License**. See [LICENSE](LICENSE) for the full text.

This project builds on excellent open-source work:

| Library | License |
|---|---|
| [rembg](https://github.com/danielgatis/rembg) | MIT |
| [ONNX Runtime](https://github.com/microsoft/onnxruntime) | MIT |
| [Pillow](https://github.com/python-pillow/Pillow) | HPND |
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | MIT |
| [NumPy](https://numpy.org) | BSD-3-Clause |

---

<div align="center">

Built with Python · Runs locally · Zero compromise on privacy

**[⭐ Star this repo](https://github.com/yourusername/pixelpeel)** if PixelPeel saved you time!

</div>
