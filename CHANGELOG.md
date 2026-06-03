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
- Export preset profiles (save your model + format + bg combos)
- CLI mode for headless / scripting usage

---

## [1.0.0] — 2024-01-01

### Added
- **Single-Image Mode** — drag-and-drop or browse, process with one click
- **Interactive split-preview** — drag the divider to compare before/after
- **Batch Mode** — queue unlimited images or a whole folder and process all at once
- **Four AI models**
  - `u2net` — Standard (best balance of speed and quality)
  - `u2net_human_seg` — Portrait (optimised for people and selfies)
  - `isnet-general-use` — Precision (high-detail objects and edges)
  - `birefnet-general` — Ultra (finest quality, slower)
- **Three output formats** — PNG (with transparency), JPEG, WEBP
- **Background fill options** — Transparent, White, or any custom RGB colour
- **Dual themes** — Midnight (dark) and Frost (light), toggle live
- **Status bar** — real-time model name, processed count, app version
- **Animated progress bar** — per-image progress with percentage readout
- **Batch status indicators** — per-row ○ / ✓ / ✗ icons in the queue
- **One-click installers** — `install_and_run.bat` (Windows) and `install_and_run.sh` (macOS/Linux)
- **Full test suite** — 20+ unit tests covering processor, save logic, session caching
- **GitHub Actions CI** — lint (ruff + black), test matrix (Python 3.9–3.12, Win/Mac/Linux), auto-release on tag

### Security
- Zero network calls after the one-time model download
- Images are never transmitted outside the local machine
- No telemetry, analytics, or crash reporting

---

[Unreleased]: https://github.com/yourusername/pixelpeel/compare/v1.0.0...HEAD
[1.0.0]:      https://github.com/yourusername/pixelpeel/releases/tag/v1.0.0
