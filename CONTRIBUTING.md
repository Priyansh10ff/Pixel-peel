# Contributing to PixelPeel

Thank you for investing your time in PixelPeel! Every contribution — whether a bug
report, a documentation fix, or a pull request — is genuinely appreciated.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [Running Tests](#running-tests)
6. [Code Style](#code-style)
7. [Submitting a Pull Request](#submitting-a-pull-request)
8. [Reporting Bugs](#reporting-bugs)
9. [Suggesting Features](#suggesting-features)

---

## Code of Conduct

This project follows a simple rule: **be respectful**. Harassment, personal attacks,
and discriminatory language will not be tolerated.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/pixelpeel.git
   cd pixelpeel
   ```
3. **Create a branch** for your work:
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/issue-123
   ```

---

## Development Setup

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows

# Install runtime + dev dependencies
pip install -r requirements.txt
pip install ruff black pytest pytest-cov
```

---

## Project Structure

```
pixelpeel/
├── main.py                  # Entry point — dependency check + launch
├── src/
│   ├── processor.py         # AI engine (rembg wrapper)
│   └── ui/
│       ├── app.py           # Main window — all UI logic
│       └── themes.py        # Colour palette — Midnight & Frost
├── tests/
│   └── test_processor.py    # Unit tests (no GUI required)
├── output/                  # Default save directory (.gitkeep tracked)
├── .github/
│   ├── workflows/ci.yml     # GitHub Actions CI
│   ├── ISSUE_TEMPLATE/      # Bug / feature templates
│   └── PULL_REQUEST_TEMPLATE.md
├── requirements.txt
├── pyproject.toml
├── install_and_run.bat      # Windows quick-start
└── install_and_run.sh       # macOS / Linux quick-start
```

---

## Running Tests

```bash
# Run the full suite
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=term-missing

# Run a single test class
pytest tests/test_processor.py::TestApplyBg -v
```

All tests mock `rembg` so no GPU or model download is required.

---

## Code Style

PixelPeel uses **ruff** for linting and **black** for formatting.

```bash
# Format
black .

# Lint
ruff check .

# Lint + auto-fix safe issues
ruff check . --fix
```

CI will block merges that fail either check. Keep line length ≤ 90 characters.

---

## Submitting a Pull Request

1. Make sure **all tests pass** locally: `pytest tests/ -v`
2. Make sure the code is **formatted and linted**: `black . && ruff check .`
3. **Update `CHANGELOG.md`** under `[Unreleased]` with a brief summary of your change.
4. Push your branch and open a PR against `main`.
5. Fill in the **pull request template** completely — screenshots are welcome for UI changes.
6. One of the maintainers will review and merge or request changes.

---

## Reporting Bugs

Use the **Bug Report** issue template. Please include:

- PixelPeel version
- OS and Python version
- Steps to reproduce (be precise)
- Full error output / stack trace

---

## Suggesting Features

Use the **Feature Request** issue template. Describe the problem you're trying to
solve, not just the solution — it helps us understand the use case and explore
alternatives.
