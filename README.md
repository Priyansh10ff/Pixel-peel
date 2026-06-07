<div align="center">

```
██████╗ ██╗██╗  ██╗███████╗██╗     ██████╗ ███████╗███████╗██╗
██╔══██╗██║╚██╗██╔╝██╔════╝██║     ██╔══██╗██╔════╝██╔════╝██║
██████╔╝██║ ╚███╔╝ █████╗  ██║     ██████╔╝█████╗  █████╗  ██║
██╔═══╝ ██║ ██╔██╗ ██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══╝  ██║
██║     ██║██╔╝ ██╗███████╗███████╗██║     ███████╗███████╗███████╗
╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚══════╝╚══════╝
```

### ◆ Professional background removal. No cloud. No AI. No compromise.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/Powered%20by-OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)](https://opencv.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-7C6FF7?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4ECDC4?style=flat-square)](README.md)
[![No AI](https://img.shields.io/badge/AI-Free-success?style=flat-square)](README.md)

<br/>

**[🚀 Quick Install](#-installation) · [✨ Features](#-features) · [🧠 How It Works](#-how-it-works) · [🖥️ Screenshots](#%EF%B8%8F-screenshots) · [🤝 Contributing](#-contributing)**

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

**🔒 Fully Private**
Your images never leave your machine. No API calls,
no telemetry, no network connection needed — ever.

**🧠 Zero AI / Zero Downloads**
Powered by OpenCV's GrabCut algorithm — pure classical
computer vision. No ONNX models, no neural nets to download.

**📦 Batch Processing**
Drop an entire folder and process all images in one click.
Progress tracking per file with real-time status badges.

**🎨 4 Removal Algorithms**
Switch between GrabCut, GrabCut HD, Edge Refine, and
Color Range — each tuned for a different type of subject.

</td>
<td width="50%">

**🖼️ Before / After Split View**
Drag the divider left and right to compare the original
and processed image side-by-side in real time.

**🌓 Dark & Light Themes**
Frost (light) and Midnight (dark) palettes — toggle
instantly from the sidebar.

**📸 Multi-Format Output**
Save as PNG (transparent), JPEG (white or custom BG),
or WebP — with optional custom background colour.

**🖥️ One-Click Desktop App**
A single install script wires up a native desktop shortcut.
Double-click to open. No terminal, no scripts, ever again.

</td>
</tr>
</table>

---

## 🖥️ Screenshots

> _Launch the app and go — the interface is self-explanatory._

```
┌─────────────────────┬──────────────────────────────────────────────┐
│  ◆  PixelPeel       │  [ Single Image ]  [ Batch ]                 │
│                     │                                               │
│  ── CV ALGORITHM ── │  ┌────────────────────────────────────────┐  │
│  ◉ GrabCut          │  │                                        │  │
│  ○ GrabCut HD       │  │       Drop image here  or  Browse      │  │
│  ○ Edge Refine      │  │                                        │  │
│  ○ Color Range      │  │   Before ◀──────────────▶ After        │  │
│                     │  │                                        │  │
│  ── FORMAT ──       │  └────────────────────────────────────────┘  │
│  [PNG] [JPEG][WEBP] │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░  72%           │
│                     │                                               │
│  ── BACKGROUND ──   │  [ Remove Background ]                       │
│  [Transparent]      │                                               │
│  [  White    ]      ├──────────────────────────────────────────────┤
│  [  Custom   ]      │  ●  Ready  │  Mode: grabcut  │  0 processed  │
└─────────────────────┴──────────────────────────────────────────────┘
```

---

## 🚀 Installation

### 🪟 Windows

1. Download or clone this repository
2. Double-click **`install.bat`**

That's it. A **PixelPeel** shortcut appears on your Desktop.
Click it to launch — no terminal, no scripts, no Python PATH juggling.

```batch
:: What install.bat does under the hood:
1. Detects your Python 3.9+ installation
2. Creates an isolated .venv inside the project folder
3. Installs only 4 lightweight packages (OpenCV, Pillow, CustomTkinter, NumPy)
4. Generates a native .ico icon via Pillow
5. Writes a silent VBScript launcher (no console window)
6. Pins a .lnk shortcut to your Desktop via PowerShell
```

### 🍎 macOS

```bash
chmod +x install.sh && ./install.sh
```

A **PixelPeel.app** appears on your Desktop.
Drag it to `/Applications` to keep it permanently.

### 🐧 Linux

```bash
chmod +x install.sh && ./install.sh
```

PixelPeel registers in your application launcher (GNOME / KDE / XFCE)
and drops a `.desktop` shortcut on your Desktop.

---

## 🧠 How It Works

PixelPeel uses **classical computer vision** — no neural networks, no model files, no GPU needed.

### The Algorithms

| Algorithm | Best For | Speed | Quality |
|---|---|---|---|
| **GrabCut** | General subjects, portraits, products | ⚡ Fast | ★★★★☆ |
| **GrabCut HD** | Complex edges — hair, fur, foliage | 🐢 Slower | ★★★★★ |
| **Edge Refine** | Geometric objects with sharp outlines | ⚡ Fast | ★★★★☆ |
| **Color Range** | Solid or gradient backgrounds | ⚡⚡ Fastest | ★★★☆☆ |

### GrabCut — the core algorithm

```
1.  Seed the algorithm with a rectangle covering the centre ~82%
    of the image as "probable foreground".

2.  Model foreground and background as separate Gaussian Mixture
    Models (GMMs) in colour space.

3.  Build a Markov Random Field (MRF) graph: every pixel is a node;
    edges carry both colour and spatial smoothness costs.

4.  Solve with min-cut / max-flow to label each pixel FG or BG.

5.  Re-estimate GMMs from the new labels and repeat (5 iterations
    for Standard, 12 for HD).

6.  Optionally re-run with a trimap derived from the rough mask to
    sharpen transition pixels (GrabCut HD only).

7.  Apply a 2-pixel Gaussian blur to the alpha mask for soft edges.
```

**Why no AI?** GrabCut runs in pure C++ inside OpenCV — zero Python ML
frameworks, zero downloads after `pip install opencv-python`, and deterministic
results that are reproducible across every machine.

---

## 🗂️ Project Structure

```
pixelpeel/
│
├── main.py                   Entry point — version + dep checks, then launches UI
├── install.bat               Windows: one-click installer + Desktop shortcut
├── install.sh                macOS/Linux: one-click installer + .app / .desktop
├── requirements.txt          4 dependencies (opencv, pillow, customtkinter, numpy)
├── pyproject.toml            Build metadata & tool config (ruff, black, pytest)
│
├── assets/
│   └── create_icon.py        Generates pixelpeel.ico / .png from code (no asset files)
│
├── src/
│   ├── __init__.py
│   ├── processor.py          ◀ Core CV engine — GrabCut, Edge Refine, Color Range
│   └── ui/
│       ├── __init__.py
│       ├── app.py            CustomTkinter GUI — sidebar, tabs, split preview, batch
│       └── themes.py         Frost (light) + Midnight (dark) colour palettes
│
└── tests/
    ├── __init__.py
    └── test_processor.py     Unit tests — real CV on synthetic images, no mocks
```

---

## 🔧 Manual / Developer Setup

If you prefer to manage the environment yourself:

```bash
# Clone
git clone https://github.com/yourusername/pixelpeel.git
cd pixelpeel

# Create venv
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install
pip install -r requirements.txt

# Run
python main.py
```

### Running the Tests

```bash
pip install pytest pytest-cov
pytest                             # all tests
pytest -v tests/test_processor.py # verbose
pytest --cov=src                   # with coverage
```

### Optional: GPU-accelerated OpenCV

```bash
# Replace the CPU build with the CUDA variant (requires CUDA toolkit)
pip uninstall opencv-python
pip install opencv-contrib-python  # or build from source with CUDA
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `opencv-python` | ≥ 4.8 | GrabCut, Canny edge, morphology |
| `Pillow` | ≥ 10.3 | Image I/O, compositing, icon generation |
| `customtkinter` | ≥ 5.2.2 | Modern Tk-based GUI widgets |
| `numpy` | ≥ 1.26 | Array operations for mask processing |

That's it — **four packages**, all pure Python wheels. No ONNX Runtime, no TensorFlow, no PyTorch.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feat/my-feature`
3. **Commit** with clear messages: `git commit -m "feat: add watershed algorithm"`
4. **Test** your changes: `pytest`
5. **Open** a Pull Request — fill in the template

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

### Ideas & Roadmap

- [ ] Trimap painting tool (manual foreground/background hints)
- [ ] Watershed segmentation algorithm
- [ ] Hair / fine-detail matting refinement pass
- [ ] Drag-and-drop support via `tkinterdnd2`
- [ ] Export preset presets (e-commerce, profile photo, etc.)
- [ ] CLI mode: `pixelpeel input.jpg output.png`

---

## 📄 License

MIT © 2024 PixelPeel — see [LICENSE](LICENSE) for full text.

---

<div align="center">

**Made with ♥ and OpenCV — zero cloud, zero compromise.**

*If PixelPeel saved you time, give it a ⭐*

</div>
