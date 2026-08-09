"""Unit tests for thresholding + preprocessing (M3)."""

from __future__ import annotations

import time

import numpy as np
import pytest
from app.processing.preprocess import gaussian_blur, preprocess, to_grayscale
from app.processing.threshold import adaptive, global_threshold, otsu, should_invert

from tests.fixtures import synthetic


def _binary_values_ok(arr: np.ndarray) -> bool:
    return arr.dtype == np.uint8 and set(np.unique(arr).tolist()).issubset({0, 255})


# --- output is strictly binary -------------------------------------------------


@pytest.mark.parametrize("fixture", [synthetic.line_art(), synthetic.gradient(), synthetic.noise()])
def test_all_methods_produce_binary(fixture):
    gray = preprocess(fixture)
    assert _binary_values_ok(otsu(gray))
    assert _binary_values_ok(global_threshold(gray, 128))
    assert _binary_values_ok(adaptive(gray))


# --- Otsu splits a bimodal image at the valley ---------------------------------


def test_otsu_splits_bimodal_at_valley():
    gray = preprocess(synthetic.bimodal(100, low=40, high=200, split=0.5))
    b = otsu(gray, invert=False)  # dark(40) -> foreground 255, bright(200) -> 0
    assert (b[:, :45] == 255).all()
    assert (b[:, 55:] == 0).all()


# --- global threshold is monotonic in t ----------------------------------------


def test_global_threshold_monotonic_in_t():
    gray = preprocess(synthetic.gradient())
    counts = []
    for t in range(0, 256, 32):
        b = global_threshold(gray, t, invert=False)  # pixels <= t become foreground
        counts.append(int((b > 0).sum()))
    assert counts == sorted(counts)  # non-decreasing


# --- adaptive handles a smooth gradient better than global ---------------------


def test_adaptive_beats_global_on_gradient():
    gray = preprocess(synthetic.gradient(256))
    g = global_threshold(gray, 128, invert=False)
    a = adaptive(gray, block_size=21, c=5, invert=False)
    total = gray.size
    global_fg = (g > 0).sum() / total
    adaptive_fg = (a > 0).sum() / total
    # A mid global threshold slices the smooth ramp roughly in half (false edge);
    # adaptive compares each pixel to its neighbourhood so a smooth ramp yields
    # almost no foreground.
    assert global_fg == pytest.approx(0.5, abs=0.1)
    assert adaptive_fg < 0.15


# --- background polarity detection ---------------------------------------------


def test_should_invert_true_for_dark_background():
    gray = preprocess(synthetic.light_on_dark())
    assert should_invert(gray) is True


def test_should_invert_false_for_light_background():
    gray = preprocess(synthetic.line_art())
    assert should_invert(gray) is False


def test_invert_produces_foreground_for_light_subject():
    gray = preprocess(synthetic.light_on_dark(200))
    b = otsu(gray, invert=True)
    # The white circle (centre) must be foreground; the dark corner must be bg.
    assert b[100, 100] == 255
    assert b[0, 0] == 0


# --- preprocess helpers --------------------------------------------------------


def test_to_grayscale_reduces_channels():
    gray = to_grayscale(synthetic.line_art())
    assert gray.ndim == 2


def test_gaussian_blur_noop_when_zero():
    gray = to_grayscale(synthetic.line_art())
    assert np.array_equal(gaussian_blur(gray, 0), gray)


def test_gaussian_blur_changes_image_when_positive():
    gray = to_grayscale(synthetic.crosshair())
    assert not np.array_equal(gaussian_blur(gray, 5), gray)


# --- performance guard ---------------------------------------------------------


def test_large_image_thresholds_are_fast():
    # 4000x4000 grayscale; all three methods should be well under the budget.
    gray = np.random.default_rng(0).integers(0, 256, (4000, 4000), dtype=np.uint8)
    start = time.perf_counter()
    otsu(gray)
    global_threshold(gray, 128)
    adaptive(gray)
    elapsed = time.perf_counter() - start
    # Generous bound for CI; locally this is a few hundred ms.
    assert elapsed < 3.0
