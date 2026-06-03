"""
PixelPeel — Test Suite
=======================
Tests for the BackgroundProcessor without requiring a GPU or real rembg
inference (mocked). Safe to run in any CI environment.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

# Ensure project root is on sys.path when run directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processor import BackgroundProcessor

# ─────────────────────────────────────────────────────────────
#  Fixtures
# ─────────────────────────────────────────────────────────────


@pytest.fixture()
def proc() -> BackgroundProcessor:
    return BackgroundProcessor()


@pytest.fixture()
def rgb_image(tmp_path: Path) -> Path:
    """A 100×100 red JPEG on disk."""
    p = tmp_path / "red.jpg"
    Image.new("RGB", (100, 100), (255, 0, 0)).save(str(p), "JPEG")
    return p


@pytest.fixture()
def rgba_image(tmp_path: Path) -> Path:
    """A 100×100 semi-transparent PNG on disk."""
    p = tmp_path / "semi.png"
    img = Image.new("RGBA", (100, 100), (0, 128, 255, 180))
    img.save(str(p), "PNG")
    return p


def _make_mock_remove(output: Image.Image):
    """Return a mock for rembg.remove that always returns *output*."""
    return MagicMock(return_value=output)


# ─────────────────────────────────────────────────────────────
#  BackgroundProcessor.MODELS
# ─────────────────────────────────────────────────────────────


class TestModels:
    def test_four_models_defined(self, proc):
        assert len(proc.MODELS) == 4

    def test_model_keys_are_strings(self, proc):
        for k in proc.MODELS:
            assert isinstance(k, str)

    def test_model_descriptions_non_empty(self, proc):
        for v in proc.MODELS.values():
            assert len(v) > 0


# ─────────────────────────────────────────────────────────────
#  BackgroundProcessor._apply_bg
# ─────────────────────────────────────────────────────────────


class TestApplyBg:
    def _rgba(self, size=(10, 10)) -> Image.Image:
        img = Image.new("RGBA", size, (100, 150, 200, 200))
        return img

    def test_transparent_png_stays_rgba(self):
        out = BackgroundProcessor._apply_bg(self._rgba(), None, "PNG")
        assert out.mode == "RGBA"

    def test_white_bg_converts_to_rgb_for_jpeg(self):
        out = BackgroundProcessor._apply_bg(self._rgba(), (255, 255, 255), "JPEG")
        assert out.mode == "RGB"

    def test_custom_bg_applied(self):
        bg = (0, 255, 0)
        out = BackgroundProcessor._apply_bg(self._rgba(), bg, "PNG")
        # Output should be RGBA with green background where alpha was < 255
        assert out.mode == "RGBA"

    def test_jpeg_without_bg_still_produces_rgb(self):
        out = BackgroundProcessor._apply_bg(self._rgba(), None, "JPEG")
        assert out.mode == "RGB"

    def test_webp_with_no_bg_stays_rgba(self):
        out = BackgroundProcessor._apply_bg(self._rgba(), None, "WEBP")
        assert out.mode == "RGBA"


# ─────────────────────────────────────────────────────────────
#  BackgroundProcessor._save
# ─────────────────────────────────────────────────────────────


class TestSave:
    def _rgba(self) -> Image.Image:
        return Image.new("RGBA", (20, 20), (10, 20, 30, 255))

    def _rgb(self) -> Image.Image:
        return Image.new("RGB", (20, 20), (10, 20, 30))

    def test_saves_png(self, tmp_path):
        p = tmp_path / "out.png"
        BackgroundProcessor._save(self._rgba(), str(p), "PNG")
        assert p.exists()
        assert Image.open(p).mode == "RGBA"

    def test_saves_jpeg(self, tmp_path):
        p = tmp_path / "out.jpg"
        BackgroundProcessor._save(self._rgb(), str(p), "JPEG")
        assert p.exists()
        img = Image.open(p)
        assert img.mode == "RGB"

    def test_saves_webp(self, tmp_path):
        p = tmp_path / "out.webp"
        BackgroundProcessor._save(self._rgba(), str(p), "WEBP")
        assert p.exists()

    def test_creates_parent_dirs(self, tmp_path):
        deep = tmp_path / "a" / "b" / "c" / "out.png"
        BackgroundProcessor._save(self._rgba(), str(deep), "PNG")
        assert deep.exists()


# ─────────────────────────────────────────────────────────────
#  BackgroundProcessor.remove_background  (mocked rembg)
# ─────────────────────────────────────────────────────────────


class TestRemoveBackground:
    def _mock_session(self):
        return MagicMock()

    def _transparent_result(self) -> Image.Image:
        img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        return img

    @patch("src.processor.BackgroundProcessor._get_session")
    def test_png_output_created(self, mock_sess, proc, rgb_image, tmp_path):
        mock_sess.return_value = self._mock_session()

        with patch("rembg.remove", _make_mock_remove(self._transparent_result())):
            out = tmp_path / "result.png"
            result = proc.remove_background(
                str(rgb_image), str(out), output_format="PNG"
            )

        assert result is True
        assert out.exists()

    @patch("src.processor.BackgroundProcessor._get_session")
    def test_jpeg_output_created(self, mock_sess, proc, rgb_image, tmp_path):
        mock_sess.return_value = self._mock_session()

        with patch("rembg.remove", _make_mock_remove(self._transparent_result())):
            out = tmp_path / "result.jpg"
            result = proc.remove_background(
                str(rgb_image), str(out),
                output_format="JPEG", bg_color=(255, 255, 255),
            )

        assert result is True
        assert out.exists()

    @patch("src.processor.BackgroundProcessor._get_session")
    def test_progress_callback_called(self, mock_sess, proc, rgb_image, tmp_path):
        mock_sess.return_value = self._mock_session()
        calls: list[tuple[float, str]] = []

        with patch("rembg.remove", _make_mock_remove(self._transparent_result())):
            proc.remove_background(
                str(rgb_image),
                str(tmp_path / "out.png"),
                progress_callback=lambda f, m: calls.append((f, m)),
            )

        assert len(calls) > 0
        fracs = [c[0] for c in calls]
        assert fracs[-1] == 1.0  # always ends at 100 %

    @patch("src.processor.BackgroundProcessor._get_session")
    def test_raises_on_bad_input(self, mock_sess, proc, tmp_path):
        mock_sess.return_value = self._mock_session()
        with pytest.raises(RuntimeError):
            proc.remove_background(
                str(tmp_path / "does_not_exist.png"),
                str(tmp_path / "out.png"),
            )


# ─────────────────────────────────────────────────────────────
#  BackgroundProcessor — session caching
# ─────────────────────────────────────────────────────────────


class TestSessionCaching:
    @patch("rembg.new_session")
    def test_session_reused_for_same_model(self, mock_new_session, proc):
        mock_new_session.return_value = MagicMock()

        proc._get_session("u2net")
        proc._get_session("u2net")

        assert mock_new_session.call_count == 1

    @patch("rembg.new_session")
    def test_session_reloaded_for_different_model(self, mock_new_session, proc):
        mock_new_session.return_value = MagicMock()

        proc._get_session("u2net")
        proc._get_session("isnet-general-use")

        assert mock_new_session.call_count == 2


# ─────────────────────────────────────────────────────────────
#  Utility helpers
# ─────────────────────────────────────────────────────────────


class TestFormatSize:
    """Smoke tests for the static _fmt_size helper (tested via direct import)."""

    def test_bytes(self):
        from src.ui.app import PixelPeelApp
        assert "B"  in PixelPeelApp._fmt_size(512)

    def test_kilobytes(self):
        from src.ui.app import PixelPeelApp
        assert "KB" in PixelPeelApp._fmt_size(2048)

    def test_megabytes(self):
        from src.ui.app import PixelPeelApp
        assert "MB" in PixelPeelApp._fmt_size(2 * 1024 * 1024)
