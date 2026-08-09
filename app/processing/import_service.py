"""Load artwork into a normalised RGB NumPy array.

Responsibilities (all headless, no Qt):

* open via Pillow and raise a clear error on non-image input;
* honour EXIF orientation (phone photos, etc.);
* **flatten alpha over white** — transparent anime art is the common case and
  silently becomes solid black if composited over the default black;
* guard against pathologically large images by downscaling above a max dimension.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

# Above this longest-edge size we downscale to keep tracing responsive.
MAX_DIMENSION = 4000
# Background used when flattening transparency.
WHITE = (255, 255, 255)


class ImageImportError(ValueError):
    """Raised when a file cannot be read as an image."""


@dataclass(frozen=True, slots=True)
class ImportedImage:
    """A loaded image as an HxWx3 uint8 RGB array plus metadata."""

    rgb: np.ndarray
    source_path: str | None
    downscaled: bool

    @property
    def height(self) -> int:
        return int(self.rgb.shape[0])

    @property
    def width(self) -> int:
        return int(self.rgb.shape[1])


def _flatten_alpha(img: Image.Image) -> Image.Image:
    """Composite any transparency over a white background, returning RGB."""
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (*WHITE, 255))
        return Image.alpha_composite(background, rgba).convert("RGB")
    return img.convert("RGB")


def _maybe_downscale(img: Image.Image) -> tuple[Image.Image, bool]:
    w, h = img.size
    longest = max(w, h)
    if longest <= MAX_DIMENSION:
        return img, False
    factor = MAX_DIMENSION / longest
    new_size = (max(1, round(w * factor)), max(1, round(h * factor)))
    return img.resize(new_size, Image.LANCZOS), True


def load_image(path: str | Path) -> ImportedImage:
    """Load ``path`` into an :class:`ImportedImage` (RGB, EXIF-corrected, flattened)."""
    p = Path(path)
    if not p.is_file():
        raise ImageImportError(f"not a file: {p}")
    try:
        with Image.open(p) as raw:
            raw.load()
            # EXIF orientation first, so width/height reflect the displayed image.
            oriented = ImageOps.exif_transpose(raw)
            flattened = _flatten_alpha(oriented)
            scaled, downscaled = _maybe_downscale(flattened)
            rgb = np.ascontiguousarray(np.asarray(scaled, dtype=np.uint8))
    except UnidentifiedImageError as exc:
        raise ImageImportError(f"not a recognised image: {p}") from exc
    except OSError as exc:
        raise ImageImportError(f"could not read image: {p} ({exc})") from exc

    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ImageImportError(f"unexpected image shape after load: {rgb.shape}")

    return ImportedImage(rgb=rgb, source_path=str(p), downscaled=downscaled)


def image_from_array(rgb: np.ndarray, source_path: str | None = None) -> ImportedImage:
    """Wrap an existing HxWx3 uint8 RGB array (used by tests/fixtures)."""
    arr = np.ascontiguousarray(rgb.astype(np.uint8))
    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ImageImportError(f"expected HxWx3 RGB array, got shape {arr.shape}")
    return ImportedImage(rgb=arr, source_path=source_path, downscaled=False)
