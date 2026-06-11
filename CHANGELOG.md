# Changelog

All notable changes to **PixelPeel** are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Keyboard shortcuts (Space to process, Ctrl+S to save, Ctrl+O to open)
- Custom colour presets for background fill
- HEIC / AVIF input format support
- Export preset profiles (save your algorithm + format + bg combos)
- CLI mode for headless / scripting usage

---

## [1.0.0] — 2026-06-08

### Added
- **Single-Image Mode** — drag-and-drop or browse, process with one click
- **Interactive split-preview** — drag the divider to compare before/after
- **Batch Mode** — queue unlimited images or a whole folder and process all at once
- **Four CV algorithms** — all run 100% locally with no model downloads
  - `grabcut` — Standard (best balance of speed and quality)
  - `grabcut_detail` — GrabCut HD (finer edges, more iterations)
  - `edge_refined` — Edge Refine (Canny edges + morphology blend)
  - `color_range` — Color Range (best for solid/gradient backgrounds)
- **Three output formats** — PNG (with transparency), JPEG, WEBP
- **Background fill options** — Transparent, White, or any custom RGB colour
- **Dual themes** — Midnight (dark) and Frost (light), toggle live
- **Status bar** — real-time algorithm name, processed count, app version
- **Animated progress bar** — per-image progress with percentage readout
- **Batch status indicators** — per-row ○ / ✓ / ✗ icons in the queue
- **One-click installers** — `install.bat` (Windows) and `install.sh` (macOS/Linux)
- **PyInstaller build scripts** — `build.bat` / `build.sh` produce a standalone binary
- **Full test suite** — unit tests covering all 4 algorithms, save logic, and helpers
- **GitHub Actions CI** — lint (ruff + black), test matrix (Python 3.9–3.12, Win/Mac/Linux)
- **GitHub Actions Release** — auto-builds native binaries for all 3 platforms on tag push

### Security
- Zero network calls — ever
- No model downloads required
- Images never leave the local machine
- No telemetry, analytics, or crash reporting

---

[Unreleased]: https://github.com/Priyansh10ff/pixelpeel/compare/v1.0.0...HEAD
[1.0.0]:      https://github.com/Priyansh10ff/pixelpeel/releases/tag/v1.0.0
