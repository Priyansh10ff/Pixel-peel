"""
PixelPeel — Background Processor
=================================
Core AI engine for removing image backgrounds using the rembg library.
Runs entirely offline — models are cached locally after the first download.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Optional, Tuple

from PIL import Image


class BackgroundProcessor:
    """
    Wraps rembg to provide background removal with model management,
    progress callbacks, and multiple output formats.
    """

    MODELS: dict[str, str] = {
        "u2net":              "Standard — Best balance of speed & quality",
        "u2net_human_seg":    "Portrait — Optimised for people & selfies",
        "isnet-general-use":  "Precision — High-detail objects & edges",
        "birefnet-general":   "Ultra — Finest quality (slower, more VRAM)",
    }

    def __init__(self, default_model: str = "u2net") -> None:
        self._session: object | None = None
        self._loaded_model: str | None = None
        self.default_model = default_model

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def _get_session(self, model_name: str) -> object:
        """Lazily load (and cache) the rembg inference session."""
        if self._session is None or self._loaded_model != model_name:
            from rembg import new_session
            self._session = new_session(model_name)
            self._loaded_model = model_name
        return self._session

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def remove_background(
        self,
        input_path: str,
        output_path: str,
        *,
        model_name: Optional[str] = None,
        bg_color: Optional[Tuple[int, int, int]] = None,
        output_format: str = "PNG",
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bool:
        """
        Remove the background from *input_path* and write the result to
        *output_path*.

        Parameters
        ----------
        input_path:        Path to the source image.
        output_path:       Where the processed image is written.
        model_name:        rembg model to use (falls back to ``default_model``).
        bg_color:          Optional (R, G, B) tuple to fill the background.
                           ``None`` keeps it transparent.
        output_format:     "PNG" | "JPEG" | "WEBP"
        progress_callback: Called with (0.0–1.0, status_message).

        Returns
        -------
        True on success, raises RuntimeError on failure.
        """
        from rembg import remove as rembg_remove

        def _cb(frac: float, msg: str) -> None:
            if progress_callback:
                progress_callback(frac, msg)

        try:
            _cb(0.05, "Loading image…")
            input_image = Image.open(input_path).convert("RGBA")

            _cb(0.15, "Initialising AI model…")
            session = self._get_session(model_name or self.default_model)

            _cb(0.30, "Removing background…")
            output_image: Image.Image = rembg_remove(input_image, session=session)

            _cb(0.85, "Compositing output…")
            output_image = self._apply_bg(output_image, bg_color, output_format)

            _cb(0.92, "Writing file…")
            self._save(output_image, output_path, output_format)

            _cb(1.00, "Done!")
            return True

        except Exception as exc:
            raise RuntimeError(f"Processing failed: {exc}") from exc

    def get_preview(
        self,
        input_path: str,
        model_name: Optional[str] = None,
    ) -> Image.Image:
        """Return the background-removed image without saving to disk."""
        from rembg import remove as rembg_remove

        session = self._get_session(model_name or self.default_model)
        return rembg_remove(Image.open(input_path).convert("RGBA"), session=session)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_bg(
        image: Image.Image,
        bg_color: Optional[Tuple[int, int, int]],
        fmt: str,
    ) -> Image.Image:
        """Apply a background colour if requested, or handle JPEG opacity."""
        needs_flat = fmt.upper() in ("JPEG", "JPG")

        if bg_color is not None:
            background = Image.new("RGBA", image.size, bg_color + (255,))
            background.paste(image, mask=image.split()[3])
            return background.convert("RGB") if needs_flat else background

        if needs_flat:
            # White background for JPEG (no transparency support)
            background = Image.new("RGBA", image.size, (255, 255, 255, 255))
            background.paste(image, mask=image.split()[3])
            return background.convert("RGB")

        return image

    @staticmethod
    def _save(image: Image.Image, path: str, fmt: str) -> None:
        """Save *image* to *path* in the requested format."""
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)

        fmt_upper = fmt.upper()
        if fmt_upper == "PNG":
            image.save(str(out), "PNG", optimize=True)
        elif fmt_upper in ("JPEG", "JPG"):
            img = image.convert("RGB") if image.mode == "RGBA" else image
            img.save(str(out), "JPEG", quality=95, optimize=True)
        elif fmt_upper == "WEBP":
            image.save(str(out), "WEBP", quality=95, method=6)
        else:
            image.save(str(out))
