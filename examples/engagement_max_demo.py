"""
Max-Engagement Short-Form Content Demo

Demonstrates the upper bound of engagement using every lever in the PRISM
pipeline in a single run:

  TTS narration + word-highlight subtitles
  + Image sequence with varied motion presets
  + Rich Phase 4 effect chains (cinematic style)
  + Varied transitions (crossfade, wipe, iris, glitch, zoom-through)
  + Beat-synchronized transition timing (snapped to speech rhythm)

Usage
-----
1. Place 7+ images (JPG/PNG) in  examples/wolves/  (or any other folder
   and update IMAGE_DIR below).
2. Run:
       python examples/engagement_max_demo.py
3. Output lands in  output/engagement_max/output_video.mp4

The script auto-generates simple coloured test images if no real images are
found, so it always runs out of the box.
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
    brightness, contrast, saturation, vignette, film_grain,
    gamma_correction, color_temperature, light_leak,
    fade_in, fade_out,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

IMAGE_DIR = Path("examples/wolves")
OUTPUT_DIR = Path("output/engagement_max")

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

MOTIONS = [
    MotionPreset.KEN_BURNS_ZOOM_IN,
    MotionPreset.PAN_RIGHT,
    MotionPreset.ZOOM_IN,
    MotionPreset.PAN_LEFT,
    MotionPreset.KEN_BURNS_ZOOM_OUT,
    MotionPreset.PAN_UP,
    MotionPreset.ZOOM_OUT,
    MotionPreset.PAN_DOWN,
]

TRANSITION_SEQUENCE = [
    (TransitionType.FADE_THROUGH_BLACK, 0.7),
    (TransitionType.WIPE_RIGHT,         0.6),
    (TransitionType.IRIS_OPEN,          0.9),
    (TransitionType.CROSSFADE,          0.8),
    (TransitionType.ZOOM_THROUGH,       0.7),
    (TransitionType.GLITCH,             0.5),
    (TransitionType.PUSH_LEFT,          0.6),
]

CINEMATIC_EFFECTS = [
    gamma_correction(1.15),
    saturation(0.95),
    contrast(1.05),
    vignette(0.45),
    color_temperature(6200),
    film_grain(0.04),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _gather_images(image_dir: Path, min_count: int = 7) -> list[Path]:
    """Return at least *min_count* image paths, generating test images if needed."""
    extensions = ("*.jpg", "*.jpeg", "*.png")
    images: list[Path] = []
    for ext in extensions:
        images.extend(sorted(image_dir.glob(ext)))
    images = sorted(set(images))

    if len(images) >= min_count:
        return images[:min_count]

    print(f"Found only {len(images)} images in {image_dir} — generating test images")
    image_dir.mkdir(parents=True, exist_ok=True)
    from PIL import Image as PILImage

    colours = [
        (40, 80, 120), (120, 40, 80), (80, 120, 40),
        (100, 60, 140), (140, 100, 60), (60, 140, 100),
        (90, 90, 150),
    ]
    for i, c in enumerate(colours):
        p = image_dir / f"test_engagement_{i}.jpg"
        if not p.exists():
            PILImage.new("RGB", (1920, 1080), c).save(p, quality=95)
            print(f"  created {p}")
        images.append(p)

    return sorted(set(images))[:min_count]


def _build_scene(images: list[Path], output_dir: Path) -> Scene:
    """
    Build a Scene that exercises every engagement lever.

    Scene.audio is set to the path where generate_video_from_text will write
    the TTS wav file.  Because the TTS step runs *before* the planner, the
    file will exist by the time the planner analyses beats.
    """
    clip_duration = 5.0
    clips = [
        ImageClip(
            source=str(img),
            duration=clip_duration,
            motion=MOTIONS[i % len(MOTIONS)],
            effects=[
                fade_in(0.3),
                *CINEMATIC_EFFECTS,
                fade_out(0.3),
            ],
        )
        for i, img in enumerate(images)
    ]

    transitions = [
        Transition(
            type=TRANSITION_SEQUENCE[i % len(TRANSITION_SEQUENCE)][0],
            duration=TRANSITION_SEQUENCE[i % len(TRANSITION_SEQUENCE)][1],
            sync=BeatSync.NEAREST_BEAT,
        )
        for i in range(len(clips) - 1)
    ]

    tts_audio_path = output_dir / "output_moviepy.wav"

    return Scene(
        clips=clips,
        transitions=transitions,
        resolution=(1080, 1920),  # 9:16 vertical (short-form)
        fps=30,
        audio=str(tts_audio_path),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("MAX-ENGAGEMENT SHORT-FORM CONTENT DEMO")
    print("=" * 70)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    images = _gather_images(IMAGE_DIR)
    print(f"Using {len(images)} images from {IMAGE_DIR}")

    scene = _build_scene(images, OUTPUT_DIR)

    subtitle_cfg = SubtitleConfig(
        mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
        base_color=(255, 255, 255),
        highlight_color=(255, 220, 50),
        vertical_align="bottom",
        y_margin=0.08,
    )

    total_scene_dur = sum(c.duration for c in scene.clips) - sum(
        t.duration for t in scene.transitions
    )
    print(f"Scene timeline ~ {total_scene_dur:.1f}s  "
          f"({len(scene.clips)} clips, {len(scene.transitions)} transitions)")
    print(f"Beat sync:  NEAREST_BEAT on all transitions")
    print(f"Effects:    cinematic chain ({len(CINEMATIC_EFFECTS)} effects per clip)")
    print(f"Subtitle:   sentence_with_word_highlight")
    print()

    video_path = generate_video_from_text(
        text=NARRATION,
        output_dir=OUTPUT_DIR,
        subtitle_config=subtitle_cfg,
        scene=scene,
    )

    print()
    print("=" * 70)
    print(f"Done!  Video at: {video_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
