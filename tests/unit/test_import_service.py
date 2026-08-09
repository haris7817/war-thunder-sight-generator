"""Unit tests for image import (M3): alpha flatten, EXIF, downscale, errors."""

from __future__ import annotations

import numpy as np
import pytest
from app.processing.import_service import (
    MAX_DIMENSION,
    ImageImportError,
    _flatten_alpha,
    load_image,
)
from PIL import Image

from tests.fixtures import synthetic


def test_flatten_alpha_composites_over_white():
    rgba = synthetic.alpha_art(128)
    out = np.asarray(_flatten_alpha(Image.fromarray(rgba)))
    # Transparent corner -> white; opaque black centre -> black.
    assert tuple(out[0, 0]) == (255, 255, 255)
    assert tuple(out[64, 64]) == (0, 0, 0)


def test_load_rgba_png_flattens_over_white(tmp_path):
    path = tmp_path / "art.png"
    Image.fromarray(synthetic.alpha_art(64)).save(path)
    img = load_image(path)
    assert img.rgb.shape == (64, 64, 3)
    assert tuple(img.rgb[0, 0]) == (255, 255, 255)  # was transparent


def test_load_applies_exif_orientation(tmp_path):
    # Stored 20x10 wide image tagged orientation=6 -> displayed rotated (dims swap).
    path = tmp_path / "rot.jpg"
    im = Image.new("RGB", (20, 10), (200, 100, 50))
    exif = im.getexif()
    exif[274] = 6  # EXIF Orientation tag
    im.save(path, exif=exif)

    img = load_image(path)
    assert (img.width, img.height) == (10, 20)  # swapped by exif_transpose


def test_large_image_is_downscaled(tmp_path):
    path = tmp_path / "big.png"
    Image.fromarray(np.full((50, 5000, 3), 128, dtype=np.uint8)).save(path)
    img = load_image(path)
    assert img.downscaled is True
    assert max(img.width, img.height) == MAX_DIMENSION


def test_small_image_not_downscaled(tmp_path):
    path = tmp_path / "small.png"
    Image.fromarray(synthetic.line_art(100)).save(path)
    img = load_image(path)
    assert img.downscaled is False
    assert (img.width, img.height) == (100, 100)


def test_non_image_raises(tmp_path):
    path = tmp_path / "notimage.txt"
    path.write_text("this is not an image", encoding="utf-8")
    with pytest.raises(ImageImportError):
        load_image(path)


def test_missing_file_raises(tmp_path):
    with pytest.raises(ImageImportError):
        load_image(tmp_path / "does_not_exist.png")
