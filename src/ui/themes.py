"""
PixelPeel — Theme Definitions
==============================
Colours are stored as (light_value, dark_value) tuples so CustomTkinter
can swap them automatically when the appearance mode changes.

Palettes
--------
Frost   — clean arctic whites with violet/teal accents  (light mode)
Midnight — deep-space darks with electric violet/mint    (dark  mode)
"""

from __future__ import annotations

import customtkinter as ctk

# ─────────────────────────────────────────────────────────────────────────────
# Colour palette  (light, dark)
# ─────────────────────────────────────────────────────────────────────────────
COLORS: dict[str, tuple[str, str]] = {
    # ── surfaces ──────────────────────────────────────────────────────────
    "bg": ("#F0F3FA", "#0D0D0F"),
    "sidebar": ("#E4E8F2", "#111116"),
    "surface": ("#E4E8F2", "#111116"),
    "card": ("#FFFFFF", "#1A1A22"),
    "border": ("#D6DBE8", "#2D2D3A"),
    # ── accent — violet ────────────────────────────────────────────────────
    "accent": ("#6C5CE7", "#7C6FF7"),
    "accent_hover": ("#5A4DD0", "#9D98F9"),
    # ── accent2 — mint / teal ──────────────────────────────────────────────
    "accent2": ("#00B894", "#4ECDC4"),
    # ── typography ────────────────────────────────────────────────────────
    "text": ("#1A1A2E", "#F2F2F7"),
    "subtext": ("#6C7488", "#8E8EA0"),
    # ── state colours ─────────────────────────────────────────────────────
    "success": ("#00B894", "#4ECDC4"),
    "error": ("#E74C3C", "#FF6B6B"),
    "warning": ("#E67E22", "#FFD166"),
}

# ─────────────────────────────────────────────────────────────────────────────
# Canvas helpers  (non-CTk widgets need a raw hex string)
# ─────────────────────────────────────────────────────────────────────────────


def current(key: str) -> str:
    """Return the hex colour for *key* matching the active appearance mode."""
    mode = ctk.get_appearance_mode().lower()
    idx = 0 if mode == "light" else 1
    return COLORS[key][idx]


def set_theme(mode: str) -> None:
    """Switch global appearance mode ('dark' | 'light')."""
    ctk.set_appearance_mode(mode)
