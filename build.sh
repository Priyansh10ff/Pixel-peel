#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  PixelPeel — macOS / Linux Build Script
#
#  macOS  →  dist/PixelPeel.app  →  dist/PixelPeel-macOS.zip
#  Linux  →  dist/PixelPeel/     →  dist/PixelPeel-Linux.tar.gz
#
#  Usage:
#    chmod +x build.sh && ./build.sh
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"
OS_TYPE="$(uname -s)"

GREEN="\033[0;32m"; YELLOW="\033[0;33m"; RED="\033[0;31m"; RESET="\033[0m"
ok()   { echo -e "  ${GREEN}[✓]${RESET}  $*"; }
warn() { echo -e "  ${YELLOW}[!]${RESET}  $*"; }
err()  { echo -e "  ${RED}[✗]${RESET}  $*" >&2; exit 1; }

echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
if [[ "$OS_TYPE" == "Darwin" ]]; then
echo "  ║         PixelPeel — macOS Build Script                  ║"
echo "  ║   Output: dist/PixelPeel.app                            ║"
else
echo "  ║         PixelPeel — Linux Build Script                  ║"
echo "  ║   Output: dist/PixelPeel/PixelPeel                      ║"
fi
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""

# ── Ensure venv ───────────────────────────────────────────────
if [[ ! -x "$VENV/bin/python" ]]; then
    echo "  [setup]  No .venv found — running installer first..."
    chmod +x "$SCRIPT_DIR/install.sh"
    "$SCRIPT_DIR/install.sh"
fi

# ── Install PyInstaller ───────────────────────────────────────
echo "  [1/4]  Installing PyInstaller..."
"$VENV/bin/pip" install pyinstaller --upgrade --quiet
ok "PyInstaller ready."

# ── Generate icon ─────────────────────────────────────────────
echo "  [2/4]  Generating icon..."
mkdir -p "$SCRIPT_DIR/assets"
"$VENV/bin/python" "$SCRIPT_DIR/assets/create_icon.py" \
    "$SCRIPT_DIR/assets/pixelpeel.png" 2>/dev/null \
    && ok "Icon generated." \
    || warn "Icon generation skipped (non-fatal)."

# ── Build with PyInstaller ────────────────────────────────────
echo "  [3/4]  Building with PyInstaller (1–4 minutes)..."
"$VENV/bin/pyinstaller" "$SCRIPT_DIR/pixelpeel.spec" \
    --distpath "$SCRIPT_DIR/dist" \
    --workpath "$SCRIPT_DIR/build" \
    --noconfirm
ok "Build complete."

# ── Package ───────────────────────────────────────────────────
echo "  [4/4]  Creating release archive..."
cd "$SCRIPT_DIR/dist"

if [[ "$OS_TYPE" == "Darwin" ]]; then
    rm -f PixelPeel-macOS.zip
    zip -r --quiet PixelPeel-macOS.zip PixelPeel.app
    ok "dist/PixelPeel-macOS.zip created."
    ARCHIVE="PixelPeel-macOS.zip"
    BINARY="dist/PixelPeel.app"
else
    rm -f PixelPeel-Linux.tar.gz
    tar -czf PixelPeel-Linux.tar.gz PixelPeel/
    ok "dist/PixelPeel-Linux.tar.gz created."
    ARCHIVE="PixelPeel-Linux.tar.gz"
    BINARY="dist/PixelPeel/PixelPeel"
fi

cd "$SCRIPT_DIR"

# ── Done ──────────────────────────────────────────────────────
echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║   Build complete!                                       ║"
echo "  ║                                                         ║"
echo "  ║   Test  :  $BINARY"
echo "  ║   Upload:  dist/$ARCHIVE"
echo "  ║            → GitHub Releases (tag: v1.0.0)             ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""
