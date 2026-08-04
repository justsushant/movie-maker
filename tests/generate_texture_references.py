"""
Generate reference PNG outputs for all Phase 4 texture effects.

Stores results in tests/fixtures/visual_regression/phase4/
with filenames like texture_scan_lines.png, texture_letterbox.png, etc.

Usage:
    source .venv/bin/activate && python tests/generate_texture_references.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.effects import (
    scan_lines,
    letterbox,
    vignette_simple,
    gradient_overlay,
    image_watermark,
    border,
    pattern_overlay,
    light_leak,
    bokeh_overlay,
    dust_scratches,
    lens_flare,
    progress_bar,
)

OUTPUT_DIR = Path(__file__).parent / "fixtures" / "visual_regression" / "phase4"
FIXTURE_IMAGES_DIR = Path(__file__).parent / "fixtures" / "images"

# Standard test frame: 640x360 (16:9, fast to generate)
FRAME_W, FRAME_H = 640, 360
T = 0.5
PROGRESS = 0.5


def load_test_frame() -> np.ndarray:
    """Load a real fixture image as the test frame, resized to standard size."""
    candidate = FIXTURE_IMAGES_DIR / "landscape_1280x720.jpg"
    if candidate.exists():
        img = cv2.imread(str(candidate))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (FRAME_W, FRAME_H))
        return img
    # Fallback: synthetic gradient frame
    frame = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)
    for y in range(FRAME_H):
        for x in range(FRAME_W):
            frame[y, x] = [
                int(x / FRAME_W * 200) + 30,
                int(y / FRAME_H * 150) + 50,
                int((x + y) / (FRAME_W + FRAME_H) * 180) + 40,
            ]
    return frame


def save_reference(frame: np.ndarray, name: str) -> None:
    """Save a reference PNG (convert RGB -> BGR for cv2)."""
    out_path = OUTPUT_DIR / name
    bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(out_path), bgr)
    print(f"  Saved: {out_path.name}")


def make_watermark() -> np.ndarray:
    """Create a simple test watermark image (RGBA)."""
    wm = np.zeros((60, 120, 4), dtype=np.uint8)
    wm[:, :, :3] = (200, 200, 200)
    wm[:, :, 3] = 180  # semi-transparent
    # Draw a simple "WM" text-like pattern
    wm[10:50, 10:50, :3] = (255, 255, 255)
    wm[10:50, 70:110, :3] = (255, 255, 255)
    return wm


def make_pattern() -> np.ndarray:
    """Create a simple repeating dot pattern."""
    pat = np.zeros((20, 20, 3), dtype=np.uint8)
    pat[8:12, 8:12] = (200, 200, 200)
    return pat


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = load_test_frame()
    print(f"Test frame shape: {frame.shape}, dtype: {frame.dtype}")
    print(f"Output dir: {OUTPUT_DIR}\n")

    effects = [
        # (filename, effect_callable)
        ("texture_scan_lines.png",
         scan_lines(spacing=3, intensity=0.4)),

        ("texture_letterbox.png",
         letterbox(top=60, bottom=60, color=(0, 0, 0))),

        ("texture_vignette_simple.png",
         vignette_simple(intensity=0.6)),

        ("texture_gradient_overlay.png",
         gradient_overlay(
             color_start=(0, 0, 80),
             color_end=(80, 0, 0),
             direction="vertical",
             alpha=0.4,
         )),

        ("texture_image_watermark.png",
         image_watermark(
             watermark_img=make_watermark(),
             position="bottom-right",
             opacity=0.5,
         )),

        ("texture_border.png",
         border(thickness=20, color=(255, 255, 255))),

        ("texture_pattern_overlay.png",
         pattern_overlay(pattern=make_pattern(), opacity=0.3)),

        # light_leak uses random positions — seed numpy for determinism
        ("texture_light_leak.png", None),  # handled separately below

        ("texture_bokeh_overlay.png",
         bokeh_overlay(num_circles=25, max_radius=60)),

        # dust_scratches uses random positions — seed numpy for determinism
        ("texture_dust_scratches.png", None),  # handled separately below

        ("texture_lens_flare.png",
         lens_flare(x=FRAME_W // 3, y=FRAME_H // 3)),

        ("texture_progress_bar.png",
         progress_bar(position="bottom", height=12, color=(0, 200, 255))),
    ]

    for filename, effect in effects:
        if effect is None:
            continue  # handled below
        result = effect(frame.copy(), T, PROGRESS)
        save_reference(result, filename)

    # light_leak: seed RNG for determinism
    np.random.seed(42)
    result = light_leak(intensity=0.35)(frame.copy(), T, PROGRESS)
    save_reference(result, "texture_light_leak.png")

    # dust_scratches: seed RNG for determinism
    np.random.seed(42)
    result = dust_scratches(density=0.001)(frame.copy(), T, PROGRESS)
    save_reference(result, "texture_dust_scratches.png")

    print(f"\nDone. Generated {len(list(OUTPUT_DIR.glob('texture_*.png')))} texture reference images.")


if __name__ == "__main__":
    main()
