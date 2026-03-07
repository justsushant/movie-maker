"""
Mahabharata Video - Simple Version (No TTS)

Quick visual-only version for testing the video engine with Mahabharata images.
No narration, just epic visuals with transitions and effects.
"""

import sys
from pathlib import Path
import numpy as np
from moviepy.editor import ImageSequenceClip

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader
from engine.effects import brightness, contrast, saturation, vignette, film_grain, chain_effects

# ============================================================================
# Configuration
# ============================================================================

mahabharata_dir = Path("files/mahabharata")
output_dir = Path("output/mahabharata_simple")
output_dir.mkdir(parents=True, exist_ok=True)

# Get all images
image_files = sorted([
    f for f in mahabharata_dir.glob("*.jpg") 
    if f.is_file()
])

print(f"Found {len(image_files)} Mahabharata images")

# ============================================================================
# Color Grading Presets
# ============================================================================

war_grade = chain_effects(
    brightness(-0.08),
    contrast(1.35),
    saturation(0.8),
    vignette(intensity=0.55, radius=0.7)
)

divine_grade = chain_effects(
    brightness(0.05),
    contrast(1.25),
    saturation(1.1),
    vignette(intensity=0.35, radius=0.8)
)

wisdom_grade = chain_effects(
    brightness(-0.03),
    contrast(1.2),
    saturation(0.75),
    film_grain(intensity=0.04),
    vignette(intensity=0.45, radius=0.75)
)

# ============================================================================
# Create Scene
# ============================================================================

scene = Scene(
    clips=[
        ImageClip(str(image_files[0]), duration=3.0, motion=MotionPreset.KEN_BURNS_ZOOM_IN, effects=[war_grade]),
        ImageClip(str(image_files[1]), duration=3.0, motion=MotionPreset.PAN_RIGHT, effects=[war_grade]),
        ImageClip(str(image_files[2]), duration=3.0, motion=MotionPreset.ZOOM_IN, effects=[divine_grade]),
        ImageClip(str(image_files[3]), duration=3.0, motion=MotionPreset.PAN_LEFT, effects=[war_grade]),
        ImageClip(str(image_files[4]), duration=3.0, motion=MotionPreset.KEN_BURNS_ZOOM_OUT, effects=[war_grade]),
        ImageClip(str(image_files[5]), duration=3.0, motion=MotionPreset.PAN_UP, effects=[war_grade]),
        ImageClip(str(image_files[6]), duration=3.0, motion=MotionPreset.ZOOM_IN, effects=[war_grade]),
        ImageClip(str(image_files[7]), duration=3.0, motion=MotionPreset.PAN_DOWN, effects=[wisdom_grade]),
        ImageClip(str(image_files[8]), duration=3.0, motion=MotionPreset.KEN_BURNS_ZOOM_IN, effects=[divine_grade]),
        ImageClip(str(image_files[9]), duration=3.0, motion=MotionPreset.PAN_RIGHT, effects=[war_grade]),
        ImageClip(str(image_files[10]), duration=3.0, motion=MotionPreset.ZOOM_OUT, effects=[divine_grade]),
        ImageClip(str(image_files[11]), duration=3.0, motion=MotionPreset.KEN_BURNS_ZOOM_OUT, effects=[wisdom_grade]),
    ],
    transitions=[
        Transition(type=TransitionType.CROSSFADE, duration=0.8),
        Transition(type=TransitionType.FADE_THROUGH_BLACK, duration=0.6),
        Transition(type=TransitionType.CROSSFADE, duration=0.8),
        Transition(type=TransitionType.WIPE_LEFT, duration=0.6),
        Transition(type=TransitionType.CROSSFADE, duration=0.8),
        Transition(type=TransitionType.IRIS_OPEN, duration=1.0),
        Transition(type=TransitionType.CROSSFADE, duration=0.8),
        Transition(type=TransitionType.FADE_THROUGH_WHITE, duration=0.8),
        Transition(type=TransitionType.CROSSFADE, duration=0.8),
        Transition(type=TransitionType.ZOOM_THROUGH, duration=0.8),
        Transition(type=TransitionType.CROSSFADE, duration=1.0),
    ],
    resolution=(1920, 1080),
    fps=30
)

# ============================================================================
# Render Video
# ============================================================================

print("=" * 70)
print("MAHABHARATA VIDEO - SIMPLE VERSION (NO TTS)")
print("=" * 70)

print("\nPlanning scene...")
planner = ScenePlanner()
timeline = planner.plan(scene)

print(f"  Timeline duration: {timeline.duration:.2f}s")
print(f"  Clips: {len(timeline.clips)}")
print(f"  Transitions: {len(timeline.transitions)}")

print("\nRendering frames...")
image_loader = ImageLoader()
renderer = FrameRenderer(timeline, image_loader)

frames = []
total_frames = int(timeline.duration * scene.fps)

for frame_idx in range(total_frames):
    t = frame_idx / scene.fps
    frame = renderer.render_frame(t)
    frames.append(frame)
    
    if (frame_idx + 1) % 30 == 0 or frame_idx == total_frames - 1:
        progress = (frame_idx + 1) / total_frames * 100
        print(f"  Progress: {frame_idx + 1}/{total_frames} frames ({progress:.1f}%)")

print("\nExporting video...")
output_path = output_dir / "mahabharata_epic.mp4"

clip = ImageSequenceClip(frames, fps=scene.fps)
clip.write_videofile(
    str(output_path),
    codec='libx264',
    audio=False,
    preset='medium',
    ffmpeg_params=['-crf', '18']
)

print(f"\n{'=' * 70}")
print("✓ VIDEO CREATED SUCCESSFULLY!")
print("=" * 70)
print(f"\nOutput: {output_path}")
print(f"Size: {output_path.stat().st_size / (1024*1024):.2f} MB")
print(f"Duration: {timeline.duration:.2f}s")
print(f"Frames: {total_frames}")
print(f"\nTo play: open {output_path}")
