#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  PixelPeel — macOS / Linux Setup & Launch Script
#  Usage:  chmod +x install_and_run.sh && ./install_and_run.sh
# ─────────────────────────────────────────────────────────────
set -e

echo ""
echo "  ╔═══════════════════════════════════════════╗"
echo "  ║          PixelPeel  v1.0.0                ║"
echo "  ║   AI Background Remover — 100% Local     ║"
echo "  ╚═══════════════════════════════════════════╝"
echo ""

# ── Check Python ──────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "  [ERROR]  python3 not found."
    echo "           macOS:   brew install python"
    echo "           Ubuntu:  sudo apt install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "  Python $PYTHON_VERSION detected."

# ── Virtual environment ───────────────────────────────────────
if [ ! -d ".venv" ]; then
    echo "  [1/3]  Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# ── Dependencies ──────────────────────────────────────────────
echo "  [2/3]  Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# ── Launch ────────────────────────────────────────────────────
echo "  [3/3]  Launching PixelPeel..."
echo ""
python main.py
