"""
PixelPeel — Background Processor
=================================
Core engine for removing image backgrounds using classical computer vision.
No AI, no neural networks, no ONNX models — runs entirely offline with
zero model downloads. Uses OpenCV GrabCut and related algorithms.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import cv2
import numpy as np
from PIL import Image


class BackgroundProcessor:
    """
    Provides background removal using classical CV techniques:
    GrabCut segmentation, edge-refined masking, and colour-range isolation.
    All methods run 100% locally — no internet or AI runtime needed.
    """

    MODELS: dict[str, str] = {
        "grabcut":        "GrabCut — Best balance of speed & quality",
        "grabcut_detail": "GrabCut HD — Finer edges, more iterations",
        "edge_refined":   "Edge Refine — Canny edge + morphology blend",
        "color_range":    "Color Range — Best for solid/gradient backgrounds",
    }

    def __init__(self, default_model: str = "grabcut") -> None:
        self.default_model = default_model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def remove_background(
        self,
        input_path: str,
        output_path: str,
        *,
        model_name: str | None = None,
        bg_color: tuple[int, int, int] | None = None,
        output_format: str = "PNG",
        progress_callback: Callable[[float, str], None] | None = None,
    ) -> bool:
        """
        Remove the background from *input_path* and write the result to
        *output_path*.

        Parameters
        ----------
        input_path:        Path to the source image.
        output_path:       Where the processed image is written.
        model_name:        Algorithm to use (falls back to ``default_model``).
        bg_color:          Optional (R, G, B) tuple to fill the background.
                           ``None`` keeps it transparent.
        output_format:     "PNG" | "JPEG" | "WEBP"
        progress_callback: Called with (0.0–1.0, status_message).

        Returns
        -------
        True on success, raises RuntimeError on failure.
        """
        def _cb(frac: float, msg: str) -> None:
            if progress_callback:
                progress_callback(frac, msg)

        try:
            _cb(0.05, "Loading image…")
            bgr = cv2.imread(input_path)
            if bgr is None:
                raise RuntimeError(f"Cannot open image: {input_path}")

            _cb(0.15, "Segmenting foreground…")
            model = model_name or self.default_model
            alpha_mask = self._segment(bgr, model, _cb)

            _cb(0.82, "Compositing output…")
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            result = Image.fromarray(rgb).convert("RGBA")
            result.putalpha(Image.fromarray(alpha_mask, "L"))
            result = self._apply_bg(result, bg_color, output_format)

            _cb(0.92, "Writing file…")
            self._save(result, output_path, output_format)

            _cb(1.00, "Done!")
            return True

        except Exception as exc:
            raise RuntimeError(f"Processing failed: {exc}") from exc

    def get_preview(
        self,
        input_path: str,
        model_name: str | None = None,
    ) -> Image.Image:
        """Return the background-removed image without saving to disk."""
        bgr = cv2.imread(input_path)
        if bgr is None:
            raise RuntimeError(f"Cannot open image: {input_path}")
        alpha = self._segment(bgr, model_name or self.default_model, lambda *_: None)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        result = Image.fromarray(rgb).convert("RGBA")
        result.putalpha(Image.fromarray(alpha, "L"))
        return result

    # ------------------------------------------------------------------
    # Algorithm router
    # ------------------------------------------------------------------

    def _segment(
        self,
        bgr: np.ndarray,
        model: str,
        cb: Callable[[float, str], None],
    ) -> np.ndarray:
        """Route to the appropriate segmentation method."""
        if model == "grabcut_detail":
            return self._grabcut(bgr, iterations=12, refine_edges=True, cb=cb)
        elif model == "edge_refined":
            return self._edge_refined(bgr, cb=cb)
        elif model == "color_range":
            return self._color_range(bgr, cb=cb)
        else:  # "grabcut" (default)
            return self._grabcut(bgr, iterations=5, refine_edges=False, cb=cb)

    # ------------------------------------------------------------------
    # Segmentation algorithms
    # ------------------------------------------------------------------

    def _grabcut(
        self,
        bgr: np.ndarray,
        iterations: int = 5,
        refine_edges: bool = False,
        cb: Callable[[float, str], None] = lambda *_: None,
    ) -> np.ndarray:
        """
        Iterative graph-cut segmentation (Rother et al., 2004).
        Models FG/BG as Gaussian Mixture Models — handles textures & gradients
        far better than simple thresholding, with no neural network needed.
        """
        h, w = bgr.shape[:2]
        mask = np.zeros((h, w), np.uint8)

        # Seed the algorithm: treat the centre 82 % of the image as
        # probable foreground; outer 9 % border as probable background.
        mx = max(1, int(w * 0.09))
        my = max(1, int(h * 0.09))
        rect = (mx, my, w - 2 * mx, h - 2 * my)

        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        cb(0.25, "Running GrabCut…")
        cv2.grabCut(bgr, mask, rect, bgd_model, fgd_model,
                    iterations, cv2.GC_INIT_WITH_RECT)

        # 0 = definite BG | 1 = definite FG | 2 = probable BG | 3 = probable FG
        alpha = np.where((mask == 2) | (mask == 0), 0, 255).astype(np.uint8)

        if refine_edges:
            cb(0.55, "Refining edges…")
            alpha = self._trimap_refine(bgr, alpha, bgd_model, fgd_model)

        cb(0.72, "Smoothing mask…")
        return _smooth_alpha(alpha)

    def _edge_refined(
        self,
        bgr: np.ndarray,
        cb: Callable[[float, str], None] = lambda *_: None,
    ) -> np.ndarray:
        """
        GrabCut combined with Canny edge detection for sharper object outlines.
        Ideal for geometric subjects with clearly defined boundaries.
        """
        cb(0.20, "Detecting edges…")
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 120)

        cb(0.30, "Running GrabCut…")
        alpha_gc = self._grabcut(bgr, iterations=7,
                                 refine_edges=False, cb=lambda *_: None)

        cb(0.60, "Blending edge map…")
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        edge_band = cv2.dilate(edges, kernel, iterations=2)

        alpha_f = alpha_gc.astype(np.float32)
        edge_weight = (edge_band > 0).astype(np.float32)
        sharp = (alpha_gc > 64).astype(np.float32) * 255.0

        blended = alpha_f * (1.0 - edge_weight * 0.65) + sharp * (edge_weight * 0.65)
        alpha = np.clip(blended, 0, 255).astype(np.uint8)

        cb(0.72, "Smoothing mask…")
        return _smooth_alpha(alpha)

    def _color_range(
        self,
        bgr: np.ndarray,
        cb: Callable[[float, str], None] = lambda *_: None,
    ) -> np.ndarray:
        """
        Sample the image corners to estimate background colour, then compute
        perceptual (Lab) distance from every pixel.  Works best when the
        background is a fairly uniform colour or gentle gradient.
        """
        h, w = bgr.shape[:2]
        cb(0.20, "Sampling background colour…")

        margin = max(2, min(h, w) // 20)
        # Collect corner samples
        samples = np.vstack([
            bgr[:margin, :margin].reshape(-1, 3),
            bgr[:margin, -margin:].reshape(-1, 3),
            bgr[-margin:, :margin].reshape(-1, 3),
            bgr[-margin:, -margin:].reshape(-1, 3),
        ])
        bg_bgr = np.median(samples, axis=0).astype(np.uint8)

        cb(0.35, "Building Lab distance map…")
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2Lab).astype(np.float32)
        bg_lab = cv2.cvtColor(
            bg_bgr.reshape(1, 1, 3), cv2.COLOR_BGR2Lab
        ).astype(np.float32).reshape(3)

        diff = lab - bg_lab
        dist = np.sqrt((diff ** 2).sum(axis=2))

        cb(0.55, "Thresholding…")
        thresh = max(18.0, float(np.percentile(dist, 20)) * 2.8)
        alpha = np.clip(
            (dist - thresh * 0.4) / (thresh * 1.2) * 255, 0, 255
        ).astype(np.uint8)

        cb(0.65, "Cleaning mask…")
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel)
        alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel)

        # Fallback: if result is < 5% foreground, GrabCut likely does better
        fg_ratio = (alpha > 127).sum() / alpha.size
        if fg_ratio < 0.05:
            return self._grabcut(bgr, iterations=5, cb=cb)

        cb(0.72, "Smoothing mask…")
        return _smooth_alpha(alpha)

    # ------------------------------------------------------------------
    # Mask refinement helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _trimap_refine(
        bgr: np.ndarray,
        alpha: np.ndarray,
        bgd_model: np.ndarray,
        fgd_model: np.ndarray,
    ) -> np.ndarray:
        """
        Re-run GrabCut with a trimap (certain FG / certain BG / unknown border)
        derived from the existing alpha mask, to sharpen transition regions.
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        fg_sure = cv2.erode(alpha, kernel, iterations=2)
        bg_sure = cv2.erode(255 - alpha, kernel, iterations=2)

        mask = np.full(alpha.shape, cv2.GC_PR_BGD, dtype=np.uint8)
        mask[fg_sure > 127] = cv2.GC_FGD
        mask[bg_sure > 127] = cv2.GC_BGD

        # Need at least some definite pixels in both classes
        if (mask == cv2.GC_FGD).sum() == 0 or (mask == cv2.GC_BGD).sum() == 0:
            return alpha

        try:
            cv2.grabCut(bgr, mask, None, bgd_model, fgd_model,
                        3, cv2.GC_INIT_WITH_MASK)
        except cv2.error:
            return alpha

        return np.where((mask == 2) | (mask == 0), 0, 255).astype(np.uint8)

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_bg(
        image: Image.Image,
        bg_color: tuple[int, int, int] | None,
        fmt: str,
    ) -> Image.Image:
        """Apply a background colour if requested, or handle JPEG opacity."""
        needs_flat = fmt.upper() in ("JPEG", "JPG")

        if bg_color is not None:
            background = Image.new("RGBA", image.size, bg_color + (255,))
            background.paste(image, mask=image.split()[3])
            return background.convert("RGB") if needs_flat else background

        if needs_flat:
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


# ------------------------------------------------------------------
# Module-level helper
# ------------------------------------------------------------------

def _smooth_alpha(alpha: np.ndarray, radius: int = 2) -> np.ndarray:
    """Apply a mild Gaussian blur to soften mask edges."""
    k = 2 * radius + 1
    return cv2.GaussianBlur(alpha, (k, k), 0)
