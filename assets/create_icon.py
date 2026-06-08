#!/usr/bin/env python3
"""
PixelPeel — Icon Generator
===========================
Creates a .ico (Windows) and .png (Linux/macOS) app icon using Pillow only.
No external assets needed — called automatically by the installers.

Usage:
    python assets/create_icon.py [output_path]
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

# ── Brand colours ──────────────────────────────────────────────────────────────
BG_DARK = (13, 13, 15)  # #0D0D0F  — Midnight background
ACCENT = (124, 111, 247)  # #7C6FF7  — Electric violet
ACCENT2 = (78, 205, 196)  # #4ECDC4  — Mint teal
WHITE = (242, 242, 247)  # #F2F2F7


def _make_base(size: int) -> Image.Image:
    """Draw a single PixelPeel icon at *size* × *size* pixels."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = int(size * 0.06)
    cx = size // 2
    cy = size // 2

    # ── Rounded-square background ─────────────────────────────────────────────
    r = int(size * 0.22)
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=r,
        fill=BG_DARK,
    )

    # ── Diamond (◆) — violet fill, mint inner glow ───────────────────────────
    d = int(size * 0.35)
    diamond = [
        (cx, cy - d),  # top
        (cx + d, cy),  # right
        (cx, cy + d),  # bottom
        (cx - d, cy),  # left
    ]
    draw.polygon(diamond, fill=ACCENT)

    # Inner diamond (cut-out / highlight)
    di = int(d * 0.45)
    inner = [
        (cx, cy - di),
        (cx + di, cy),
        (cx, cy + di),
        (cx - di, cy),
    ]
    draw.polygon(inner, fill=ACCENT2)

    # Centre pixel dot — white
    dot = max(2, int(size * 0.055))
    draw.ellipse([cx - dot, cy - dot, cx + dot, cy + dot], fill=WHITE)

    return img


def create_icons(out_path: str | Path) -> None:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Build multi-resolution .ico
    sizes = [16, 24, 32, 48, 64, 128, 256]
    frames = [_make_base(s) for s in sizes]

    suffix = out.suffix.lower()

    if suffix == ".ico":
        frames[0].save(
            str(out),
            format="ICO",
            sizes=[(s, s) for s in sizes],
            append_images=frames[1:],
        )
    elif suffix == ".icns":
        # macOS — save a 512px PNG that macOS can use as a generic icon
        png_path = out.with_suffix(".png")
        _make_base(512).save(str(png_path), "PNG")
        out = png_path
    else:
        # .png (Linux)
        _make_base(256).save(str(out), "PNG")

    print(f"  [OK]  Icon written -> {out}")


if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else "assets/pixelpeel.ico"
    create_icons(dest)
