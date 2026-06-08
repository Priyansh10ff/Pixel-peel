"""
PixelPeel — Test Suite
=======================
Tests for BackgroundProcessor without a display or GPU.
All OpenCV calls use real algorithms on synthetic images —
no mocking needed because GrabCut works on tiny arrays.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processor import BackgroundProcessor, _smooth_alpha

# ─────────────────────────────────────────────────────────────────────────────
#  Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture()
def proc() -> BackgroundProcessor:
    return BackgroundProcessor()


@pytest.fixture()
def rgb_image(tmp_path: Path) -> Path:
    """100×100 red JPEG."""
    p = tmp_path / "red.jpg"
    Image.new("RGB", (100, 100), (220, 60, 60)).save(str(p), "JPEG")
    return p


@pytest.fixture()
def rgba_image(tmp_path: Path) -> Path:
    """100×100 semi-transparent PNG."""
    p = tmp_path / "semi.png"
    Image.new("RGBA", (100, 100), (0, 128, 255, 180)).save(str(p), "PNG")
    return p


@pytest.fixture()
def gradient_image(tmp_path: Path) -> Path:
    """100×100 image: white border, red centre — ideal for GrabCut."""
    arr = np.ones((100, 100, 3), dtype=np.uint8) * 240  # light grey BG
    arr[20:80, 20:80] = [200, 50, 50]  # red FG
    p = tmp_path / "grad.png"
    cv2.imwrite(str(p), arr)
    return p


# ─────────────────────────────────────────────────────────────────────────────
#  MODELS dict
# ─────────────────────────────────────────────────────────────────────────────


class TestModels:
    def test_four_models(self, proc):
        assert len(proc.MODELS) == 4

    def test_expected_keys(self, proc):
        assert set(proc.MODELS) == {
            "grabcut",
            "grabcut_detail",
            "edge_refined",
            "color_range",
        }

    def test_descriptions_non_empty(self, proc):
        for v in proc.MODELS.values():
            assert len(v) > 0


# ─────────────────────────────────────────────────────────────────────────────
#  _apply_bg
# ─────────────────────────────────────────────────────────────────────────────


class TestApplyBg:
    def _rgba(self) -> Image.Image:
        return Image.new("RGBA", (20, 20), (100, 150, 200, 180))

    def test_transparent_png_stays_rgba(self):
        out = BackgroundProcessor._apply_bg(self._rgba(), None, "PNG")
        assert out.mode == "RGBA"

    def test_jpeg_no_bg_becomes_rgb(self):
        out = BackgroundProcessor._apply_bg(self._rgba(), None, "JPEG")
        assert out.mode == "RGB"

    def test_custom_bg_applied_png(self):
        out = BackgroundProcessor._apply_bg(self._rgba(), (0, 255, 0), "PNG")
        assert out.mode == "RGBA"

    def test_custom_bg_jpeg_is_rgb(self):
        out = BackgroundProcessor._apply_bg(self._rgba(), (255, 255, 255), "JPEG")
        assert out.mode == "RGB"

    def test_webp_transparent_stays_rgba(self):
        out = BackgroundProcessor._apply_bg(self._rgba(), None, "WEBP")
        assert out.mode == "RGBA"


# ─────────────────────────────────────────────────────────────────────────────
#  _save
# ─────────────────────────────────────────────────────────────────────────────


class TestSave:
    def test_saves_png(self, tmp_path):
        p = tmp_path / "out.png"
        BackgroundProcessor._save(Image.new("RGBA", (20, 20)), str(p), "PNG")
        assert p.exists()

    def test_saves_jpeg(self, tmp_path):
        p = tmp_path / "out.jpg"
        BackgroundProcessor._save(Image.new("RGB", (20, 20)), str(p), "JPEG")
        assert p.exists()
        assert Image.open(p).mode == "RGB"

    def test_saves_webp(self, tmp_path):
        p = tmp_path / "out.webp"
        BackgroundProcessor._save(Image.new("RGBA", (20, 20)), str(p), "WEBP")
        assert p.exists()

    def test_creates_parent_dirs(self, tmp_path):
        deep = tmp_path / "a" / "b" / "out.png"
        BackgroundProcessor._save(Image.new("RGBA", (10, 10)), str(deep), "PNG")
        assert deep.exists()


# ─────────────────────────────────────────────────────────────────────────────
#  remove_background — real CV (no mocks)
# ─────────────────────────────────────────────────────────────────────────────


class TestRemoveBackground:
    def test_png_output_created(self, proc, gradient_image, tmp_path):
        out = tmp_path / "result.png"
        ok = proc.remove_background(str(gradient_image), str(out), output_format="PNG")
        assert ok is True
        assert out.exists()

    def test_jpeg_output_created(self, proc, gradient_image, tmp_path):
        out = tmp_path / "result.jpg"
        ok = proc.remove_background(
            str(gradient_image),
            str(out),
            output_format="JPEG",
            bg_color=(255, 255, 255),
        )
        assert ok is True
        assert out.exists()

    def test_webp_output_created(self, proc, gradient_image, tmp_path):
        out = tmp_path / "result.webp"
        ok = proc.remove_background(str(gradient_image), str(out), output_format="WEBP")
        assert ok is True
        assert out.exists()

    def test_progress_callback(self, proc, gradient_image, tmp_path):
        calls: list[tuple[float, str]] = []
        proc.remove_background(
            str(gradient_image),
            str(tmp_path / "out.png"),
            progress_callback=lambda f, m: calls.append((f, m)),
        )
        assert len(calls) >= 3
        assert calls[-1][0] == 1.0

    def test_raises_on_missing_file(self, proc, tmp_path):
        with pytest.raises(RuntimeError):
            proc.remove_background(
                str(tmp_path / "nope.png"),
                str(tmp_path / "out.png"),
            )

    def test_grabcut_detail_model(self, proc, gradient_image, tmp_path):
        out = tmp_path / "hd.png"
        ok = proc.remove_background(
            str(gradient_image), str(out), model_name="grabcut_detail"
        )
        assert ok is True

    def test_edge_refined_model(self, proc, gradient_image, tmp_path):
        out = tmp_path / "edge.png"
        ok = proc.remove_background(
            str(gradient_image), str(out), model_name="edge_refined"
        )
        assert ok is True

    def test_color_range_model(self, proc, gradient_image, tmp_path):
        out = tmp_path / "color.png"
        ok = proc.remove_background(
            str(gradient_image), str(out), model_name="color_range"
        )
        assert ok is True


# ─────────────────────────────────────────────────────────────────────────────
#  get_preview
# ─────────────────────────────────────────────────────────────────────────────


class TestGetPreview:
    def test_returns_rgba_image(self, proc, gradient_image):
        result = proc.get_preview(str(gradient_image))
        assert isinstance(result, Image.Image)
        assert result.mode == "RGBA"

    def test_raises_on_missing_file(self, proc, tmp_path):
        with pytest.raises(RuntimeError):
            proc.get_preview(str(tmp_path / "ghost.png"))


# ─────────────────────────────────────────────────────────────────────────────
#  _smooth_alpha
# ─────────────────────────────────────────────────────────────────────────────


class TestSmoothAlpha:
    def test_output_same_shape(self):
        alpha = np.zeros((50, 50), dtype=np.uint8)
        alpha[15:35, 15:35] = 255
        out = _smooth_alpha(alpha)
        assert out.shape == alpha.shape

    def test_output_dtype_uint8(self):
        alpha = (np.random.rand(30, 30) * 255).astype(np.uint8)
        assert _smooth_alpha(alpha).dtype == np.uint8

    def test_edges_are_blurred(self):
        # Sharp step should become softer after smoothing
        alpha = np.zeros((20, 20), dtype=np.uint8)
        alpha[:, 10:] = 255
        out = _smooth_alpha(alpha, radius=2)
        # Pixels right at the edge should be between 0 and 255
        mid_col = out[:, 9]
        assert (mid_col > 0).any()


# ─────────────────────────────────────────────────────────────────────────────
#  _fmt_size UI helper
# ─────────────────────────────────────────────────────────────────────────────


class TestFmtSize:
    """Import the helper directly from app — keep it isolated from the display."""

    def test_bytes(self):
        from src.ui.app import PixelPeelApp

        assert "B" in PixelPeelApp._fmt_size(512)

    def test_kilobytes(self):
        from src.ui.app import PixelPeelApp

        assert "KB" in PixelPeelApp._fmt_size(2048)

    def test_megabytes(self):
        from src.ui.app import PixelPeelApp

        assert "MB" in PixelPeelApp._fmt_size(3 * 1024 * 1024)
