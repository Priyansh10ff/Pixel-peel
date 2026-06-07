#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  PixelPeel — macOS / Linux One-Click Installer
#  Run once; launch from your desktop/app launcher forever.
#
#  Usage:
#    chmod +x install.sh
#    ./install.sh
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_CMD=""

# ── Colours ───────────────────────────────────────────────────
GREEN="\033[0;32m"; YELLOW="\033[0;33m"; RED="\033[0;31m"; RESET="\033[0m"
ok()   { echo -e "  ${GREEN}[✓]${RESET}  $*"; }
warn() { echo -e "  ${YELLOW}[!]${RESET}  $*"; }
err()  { echo -e "  ${RED}[✗]${RESET}  $*" >&2; }

echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║           PixelPeel  v1.0.0  — Installer                ║"
echo "  ║   100% Local Background Remover  |  No Cloud, No AI    ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""

# ── Step 0: Find Python 3.9+ ──────────────────────────────────
for cmd in python3.12 python3.11 python3.10 python3.9 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
        major=${ver%%.*}
        minor=${ver##*.}
        if [[ "$major" -ge 3 && "$minor" -ge 9 ]]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    err "Python 3.9+ not found."
    echo "       macOS : brew install python"
    echo "       Ubuntu: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
ok "Python $ver found  ($PYTHON_CMD)"

# ── Step 1: Virtual environment ───────────────────────────────
if [[ -x "$VENV_DIR/bin/python" ]]; then
    echo "  [1/5]  Virtual environment already exists — skipping."
else
    echo "  [1/5]  Creating virtual environment ..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    ok "Virtual environment created."
fi

# ── Step 2: Dependencies ──────────────────────────────────────
echo "  [2/5]  Installing dependencies (first run may take a moment) ..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" --quiet
ok "Dependencies installed."

# ── Step 3: App icon ──────────────────────────────────────────
echo "  [3/5]  Generating app icon ..."
mkdir -p "$SCRIPT_DIR/assets"
ICON_PNG="$SCRIPT_DIR/assets/pixelpeel.png"
"$VENV_DIR/bin/python" "$SCRIPT_DIR/assets/create_icon.py" "$ICON_PNG" 2>/dev/null \
    && ok "Icon created." \
    || warn "Icon generation skipped (non-fatal)."

# ── Step 4 & 5: Platform-specific desktop integration ─────────
OS_TYPE="$(uname -s)"

# ─── macOS ────────────────────────────────────────────────────
if [[ "$OS_TYPE" == "Darwin" ]]; then
    echo "  [4/5]  Building macOS .app bundle ..."
    APP_DEST="$HOME/Desktop/PixelPeel.app"
    MACOS_BIN="$APP_DEST/Contents/MacOS"
    RESOURCES="$APP_DEST/Contents/Resources"
    mkdir -p "$MACOS_BIN" "$RESOURCES"

    # Executable shell
    cat > "$MACOS_BIN/PixelPeel" << INNER
#!/bin/bash
cd "$SCRIPT_DIR"
exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/main.py" "\$@"
INNER
    chmod +x "$MACOS_BIN/PixelPeel"

    # Info.plist
    cat > "$APP_DEST/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>     <string>PixelPeel</string>
    <key>CFBundleIdentifier</key>     <string>com.pixelpeel.app</string>
    <key>CFBundleName</key>           <string>PixelPeel</string>
    <key>CFBundleDisplayName</key>    <string>PixelPeel</string>
    <key>CFBundleVersion</key>        <string>1.0.0</string>
    <key>CFBundlePackageType</key>    <string>APPL</string>
    <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
PLIST

    # Copy icon if available
    [[ -f "$ICON_PNG" ]] && cp "$ICON_PNG" "$RESOURCES/AppIcon.png"

    ok "PixelPeel.app created on Desktop."

    echo "  [5/5]  Registering with Launchpad ..."
    /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister \
        -f "$APP_DEST" 2>/dev/null && ok "Registered with Launchpad." || warn "Launchpad registration skipped."

# ─── Linux ────────────────────────────────────────────────────
else
    echo "  [4/5]  Creating .desktop launcher ..."
    APPS_DIR="$HOME/.local/share/applications"
    mkdir -p "$APPS_DIR"

    DESKTOP_FILE="$APPS_DIR/pixelpeel.desktop"
    cat > "$DESKTOP_FILE" << DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=PixelPeel
Comment=Local background remover — no AI, no cloud
Exec=$VENV_DIR/bin/python $SCRIPT_DIR/main.py
Icon=$ICON_PNG
Terminal=false
Categories=Graphics;Photography;
Keywords=background;remove;image;
StartupWMClass=pixelpeel
DESKTOP
    chmod +x "$DESKTOP_FILE"
    ok ".desktop file created in $APPS_DIR"

    echo "  [5/5]  Adding Desktop shortcut ..."
    DESKTOP_SHORTCUT="$HOME/Desktop/PixelPeel.desktop"
    if [[ -d "$HOME/Desktop" ]]; then
        cp "$DESKTOP_FILE" "$DESKTOP_SHORTCUT"
        chmod +x "$DESKTOP_SHORTCUT"
        # Trust the desktop file (GNOME)
        gio set "$DESKTOP_SHORTCUT" metadata::trusted true 2>/dev/null || true
        ok "Desktop shortcut created."
    else
        warn "~/Desktop not found — app is in your application launcher."
    fi

    # Update desktop database
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi

# ── Done ──────────────────────────────────────────────────────
echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║   Installation complete!                                ║"
echo "  ║                                                         ║"
if [[ "$OS_TYPE" == "Darwin" ]]; then
echo "  ║   ▶  Open  PixelPeel.app  on your Desktop              ║"
echo "  ║      (or find it in Launchpad)                         ║"
else
echo "  ║   ▶  Click  PixelPeel  in your app launcher            ║"
echo "  ║      or double-click it on your Desktop                ║"
fi
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""
