# Contributing to PixelPeel

Thank you for your interest in contributing. This document covers everything
you need to get started.

---

## Development setup

```bash
git clone https://github.com/Priyansh10ff/pixelpeel.git
cd pixelpeel

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install pytest pytest-cov ruff black
```

Run the app:
```bash
python main.py
```

---

## Project structure

```
pixelpeel/
├── main.py                  Entry point — dependency check then launches UI
├── install.bat              Windows installer (creates desktop shortcut)
├── install.sh               macOS / Linux installer
├── build.bat                Windows PyInstaller build
├── build.sh                 macOS / Linux PyInstaller build
├── pixelpeel.spec           PyInstaller configuration
├── assets/
│   └── create_icon.py       Generates app icon at install/build time
├── src/
│   ├── processor.py         Core CV engine — GrabCut, Edge Refine, Color Range
│   └── ui/
│       ├── app.py           CustomTkinter GUI
│       └── themes.py        Light and dark colour palettes
└── tests/
    └── test_processor.py    Unit test suite
```

---

## Running tests

```bash
pytest                          # all tests
pytest -v tests/test_processor.py
pytest --cov=src                # with coverage
```

All tests use real OpenCV on synthetic images — no GPU, no model downloads,
no mocking required.

---

## Code style

This project uses **ruff** for linting and **black** for formatting.

```bash
ruff check .
black .
```

Both must pass before a pull request can be merged. The CI enforces this
automatically on every push.

---

## Submitting a pull request

1. Fork the repository
2. Create a branch: `git checkout -b feat/your-feature`
3. Make your changes and add tests where appropriate
4. Run `ruff check . && black . && pytest` — all must pass
5. Commit: `git commit -m "feat: description of change"`
6. Push and open a pull request against `main`

---

## Reporting a bug

Open an issue at [github.com/Priyansh10ff/pixelpeel/issues](https://github.com/Priyansh10ff/pixelpeel/issues).

Include:
- Operating system and version
- Python version (`python --version`)
- Steps to reproduce
- Expected vs actual behaviour
