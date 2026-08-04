"""
Engagement Benchmark — Systematic Comparison

Renders the **same narration + images** through five progressively richer
configurations so you can compare engagement side-by-side:

  1. baseline        — solid-colour background + subtitles only (no Scene)
  2. scene_only      — image sequence with motion + crossfade-only transitions
  3. scene_effects   — adds a cinematic effect chain
  4. scene_beatsync  — adds beat-synchronised transition timing
  5. max             — all of the above + varied transitions

Each run writes to  output/engagement_benchmark/<preset>/output_video.mp4
so you can play them back-to-back and judge the difference.

Usage
-----
    python examples/engagement_benchmark.py            # run all 5
    python examples/engagement_benchmark.py baseline   # run just one

Requires images in  examples/wolves/  (auto-generates test images if missing).
"""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from api.library import generate_video_from_text
from subtitle.config import SubtitleConfig, SubtitleMode
from engine.scene import (
    Scene, ImageClip, MotionPreset, Transition, TransitionType, BeatSync,
)
from engine.effects import (
    gamma_correction, saturation, contrast, vignette,
    color_temperature, film_grain, fade_in, fade_out,
)

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

IMAGE_DIR = Path("examples/wolves")
OUTPUT_ROOT = Path("output/engagement_benchmark")

NARRATION = (
    "Wolves are among the most iconic animals on Earth. "
    "They live in complex social groups called packs, led by an alpha pair. "
    "Communication happens through howls, body language, and scent marking. "
    "A single pack can roam territories spanning hundreds of square miles. "
    "Their teamwork during hunts is legendary, coordinating with precision "
    "that rivals any military operation. "
    "Despite centuries of persecution, wolves continue to thrive in the wild, "
    "a testament to their resilience and adaptability."
)

SUBTITLE_CFG = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
    base_color=(255, 255, 255),
    highlight_color=(255, 220, 50),
    vertical_align="bottom",
    y_margin=0.08,
)

MOTIONS = [
    MotionPreset.KEN_BURNS_ZOOM_IN,
    MotionPreset.PAN_RIGHT,
    MotionPreset.ZOOM_IN,
    MotionPreset.PAN_LEFT,
    MotionPreset.KEN_BURNS_ZOOM_OUT,
    MotionPreset.PAN_UP,
    MotionPreset.ZOOM_OUT,
]

CINEMATIC = [
    gamma_correction(1.15),
    saturation(0.95),
    contrast(1.05),
    vignette(0.45),
    color_temperature(6200),
    film_grain(0.04),
]

VARIED_TRANSITIONS = [
    (TransitionType.FADE_THROUGH_BLACK, 0.7),
    (TransitionType.WIPE_RIGHT,         0.6),
    (TransitionType.IRIS_OPEN,          0.9),
    (TransitionType.CROSSFADE,          0.8),
    (TransitionType.ZOOM_THROUGH,       0.7),
    (TransitionType.GLITCH,             0.5),
]

# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------

def _gather_images(min_count: int = 7) -> list[Path]:
    extensions = ("*.jpg", "*.jpeg", "*.png")
    images: list[Path] = []
    for ext in extensions:
        images.extend(IMAGE_DIR.glob(ext))
    images = sorted(set(images))

    if len(images) >= min_count:
        return images[:min_count]

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    from PIL import Image as PILImage

    colours = [
        (40, 80, 120), (120, 40, 80), (80, 120, 40),
        (100, 60, 140), (140, 100, 60), (60, 140, 100),
        (90, 90, 150),
    ]
    for i, c in enumerate(colours):
        p = IMAGE_DIR / f"test_bench_{i}.jpg"
        if not p.exists():
            PILImage.new("RGB", (1920, 1080), c).save(p, quality=95)
        images.append(p)

    return sorted(set(images))[:min_count]

# ---------------------------------------------------------------------------
# Preset builders — each returns (name, scene_or_None)
# ---------------------------------------------------------------------------

def _make_clips(images: list[Path], effects: list | None = None) -> list[ImageClip]:
    clip_dur = 5.0
    return [
        ImageClip(
            source=str(img),
            duration=clip_dur,
            motion=MOTIONS[i % len(MOTIONS)],
            effects=list(effects) if effects else [],
        )
        for i, img in enumerate(images)
    ]


def preset_baseline(images: list[Path], out: Path) -> Scene | None:
    """No scene at all — solid background + subtitles."""
    return None


def preset_scene_only(images: list[Path], out: Path) -> Scene:
    """Image sequence with motion and simple crossfade transitions."""
    clips = _make_clips(images)
    transitions = [
        Transition(type=TransitionType.CROSSFADE, duration=0.8)
        for _ in range(len(clips) - 1)
    ]
    return Scene(
        clips=clips,
        transitions=transitions,
        resolution=(1080, 1920),
        fps=30,
    )


def preset_scene_effects(images: list[Path], out: Path) -> Scene:
    """Scene + cinematic effect chain on every clip."""
    clips = _make_clips(images, effects=[fade_in(0.3), *CINEMATIC, fade_out(0.3)])
    transitions = [
        Transition(type=TransitionType.CROSSFADE, duration=0.8)
        for _ in range(len(clips) - 1)
    ]
    return Scene(
        clips=clips,
        transitions=transitions,
        resolution=(1080, 1920),
        fps=30,
    )


def preset_scene_beatsync(images: list[Path], out: Path) -> Scene:
    """Scene + effects + beat-synchronised crossfades."""
    clips = _make_clips(images, effects=[fade_in(0.3), *CINEMATIC, fade_out(0.3)])
    transitions = [
        Transition(
            type=TransitionType.CROSSFADE,
            duration=0.8,
            sync=BeatSync.NEAREST_BEAT,
        )
        for _ in range(len(clips) - 1)
    ]
    audio_path = out / "output_moviepy.wav"
    return Scene(
        clips=clips,
        transitions=transitions,
        resolution=(1080, 1920),
        fps=30,
        audio=str(audio_path),
    )


def preset_max(images: list[Path], out: Path) -> Scene:
    """Everything: effects + varied transitions + beat sync."""
    clips = _make_clips(images, effects=[fade_in(0.3), *CINEMATIC, fade_out(0.3)])
    transitions = [
        Transition(
            type=VARIED_TRANSITIONS[i % len(VARIED_TRANSITIONS)][0],
            duration=VARIED_TRANSITIONS[i % len(VARIED_TRANSITIONS)][1],
            sync=BeatSync.NEAREST_BEAT,
        )
        for i in range(len(clips) - 1)
    ]
    audio_path = out / "output_moviepy.wav"
    return Scene(
        clips=clips,
        transitions=transitions,
        resolution=(1080, 1920),
        fps=30,
        audio=str(audio_path),
    )


PRESETS = {
    "baseline":       preset_baseline,
    "scene_only":     preset_scene_only,
    "scene_effects":  preset_scene_effects,
    "scene_beatsync": preset_scene_beatsync,
    "max":            preset_max,
}

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_preset(name: str, builder, images: list[Path]) -> Path:
    out = OUTPUT_ROOT / name
    out.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"  PRESET: {name}")
    print(f"  Output: {out}")
    print(f"{'=' * 60}\n")

    scene = builder(images, out)
    return generate_video_from_text(
        text=NARRATION,
        output_dir=out,
        subtitle_config=SUBTITLE_CFG,
        scene=scene,
    )


def main() -> None:
    requested = sys.argv[1:] if len(sys.argv) > 1 else list(PRESETS.keys())
    unknown = [r for r in requested if r not in PRESETS]
    if unknown:
        print(f"Unknown preset(s): {unknown}")
        print(f"Available: {list(PRESETS.keys())}")
        sys.exit(1)

    images = _gather_images()
    print(f"Images: {len(images)} from {IMAGE_DIR}")
    print(f"Presets to run: {requested}\n")

    results: dict[str, Path] = {}
    for name in requested:
        results[name] = run_preset(name, PRESETS[name], images)

    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)
    for name, path in results.items():
        print(f"  {name:20s} -> {path}")
    print()
    print("Play them side-by-side and compare engagement!")


if __name__ == "__main__":
    main()
