"""
Dragon Video - Simple Version (No TTS)

Quick visual-only version for testing the video engine with your dragon images.
No narration, just beautiful transitions and effects.
"""

import sys
from pathlib import Path
import numpy as np
from moviepy.editor import ImageSequenceClip

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader
from engine.effects import brightness, contrast, saturation, vignette, film_grain, chain_effects

# ============================================================================
# Configuration
# ============================================================================

dragon_dir = Path("files/dragon")
output_dir = Path("output/dragon_simple")
output_dir.mkdir(parents=True, exist_ok=True)

# Get all dragon images
image_files = sorted([
    f for f in dragon_dir.glob("*.jpg") 
    if f.is_file()
] + [
    f for f in dragon_dir.glob("*.png") 
    if f.is_file()
])

print(f"Found {len(image_files)} dragon images")

# ============================================================================
# Color Grading Presets
# ============================================================================

epic_grade = chain_effects(
    brightness(-0.05),
    contrast(1.3),
    saturation(0.85),
    vignette(intensity=0.5, radius=0.75)
)

fire_grade = chain_effects(
    brightness(0.1),
    contrast(1.2),
    saturation(1.2),
    vignette(intensity=0.3, radius=0.8)
)

mystical_grade = chain_effects(
    saturation(0.7),
    film_grain(intensity=0.03),
    vignette(intensity=0.4, radius=0.8)
)

# ============================================================================
# Create Scene
# ============================================================================

scene = Scene(
    clips=[
        ImageClip(str(image_files[0]), duration=3.0, motion=MotionPreset.KEN_BURNS_ZOOM_IN, effects=[epic_grade]),
        ImageClip(str(image_files[1]), duration=3.0, motion=MotionPreset.PAN_RIGHT, effects=[epic_grade]),
        ImageClip(str(image_files[2]), duration=3.0, motion=MotionPreset.ZOOM_IN, effects=[fire_grade]),
        ImageClip(str(image_files[3]), duration=3.0, motion=MotionPreset.PAN_LEFT, effects=[mystical_grade]),
        ImageClip(str(image_files[4]), duration=3.0, motion=MotionPreset.KEN_BURNS_ZOOM_OUT, effects=[epic_grade]),
        ImageClip(str(image_files[5]), duration=3.0, motion=MotionPreset.PAN_UP, effects=[epic_grade]),
        ImageClip(str(image_files[6]), duration=3.0, motion=MotionPreset.ZOOM_IN, effects=[fire_grade]),
        ImageClip(str(image_files[7]), duration=3.0, motion=MotionPreset.PAN_DOWN, effects=[mystical_grade]),
        ImageClip(str(image_files[8]), duration=3.0, motion=MotionPreset.KEN_BURNS_ZOOM_IN, effects=[epic_grade]),
        ImageClip(str(image_files[9]), duration=3.0, motion=MotionPreset.ZOOM_OUT, effects=[epic_grade]),
    ],
    transitions=[
        Transition(type=TransitionType.CROSSFADE, duration=0.8),
        Transition(type=TransitionType.FADE_THROUGH_BLACK, duration=0.6),
        Transition(type=TransitionType.CROSSFADE, duration=0.8),
        Transition(type=TransitionType.IRIS_OPEN, duration=1.0),
        Transition(type=TransitionType.CROSSFADE, duration=0.8),
        Transition(type=TransitionType.SLIDE_LEFT, duration=0.6),
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
print("DRAGON VIDEO - SIMPLE VERSION (NO TTS)")
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
output_path = output_dir / "dragon_showcase.mp4"

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
