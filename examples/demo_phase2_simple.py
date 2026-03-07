"""
Simple Phase 2 demo without TTS - just video engine features.

This creates a video with transitions and effects but no narration/subtitles.
Perfect for quick testing of visual features.
"""

import sys
from pathlib import Path
import numpy as np
from moviepy.editor import ImageSequenceClip, AudioFileClip

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader
from engine.effects import brightness, vignette, film_grain, contrast

# ============================================================================
# Configuration
# ============================================================================

output_dir = Path("output/phase2_simple")
output_dir.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Create Scene
# ============================================================================

scene = Scene(
    clips=[
        # Clip 1: Zoom in with brightness
        ImageClip(
            source="tests/fixtures/images/landscape.jpg",
            duration=2.0,
            motion=MotionPreset.KEN_BURNS_ZOOM_IN,
            effects=[brightness(0.1)]
        ),
        
        # Clip 2: Pan with vignette
        ImageClip(
            source="tests/fixtures/images/portrait.jpg",
            duration=2.0,
            motion=MotionPreset.PAN_LEFT,
            effects=[vignette(intensity=0.4)]
        ),
        
        # Clip 3: Static with film grain
        ImageClip(
            source="tests/fixtures/images/square.jpg",
            duration=2.0,
            motion=MotionPreset.STATIC,
            effects=[film_grain(intensity=0.05)]
        ),
    ],
    transitions=[
        Transition(type=TransitionType.CROSSFADE, duration=0.5),
        Transition(type=TransitionType.SLIDE_LEFT, duration=0.5),
    ],
    resolution=(1920, 1080),
    fps=30
)

# ============================================================================
# Render Video
# ============================================================================

print("Planning scene...")
planner = ScenePlanner()
timeline = planner.plan(scene)

print(f"Timeline duration: {timeline.duration:.2f}s")
print(f"Clips: {len(timeline.clips)}")
print(f"Transitions: {len(timeline.transitions)}")

print("\nRendering frames...")
image_loader = ImageLoader()
renderer = FrameRenderer(timeline, image_loader)

# Generate all frames
frames = []
total_frames = int(timeline.duration * scene.fps)

for frame_idx in range(total_frames):
    t = frame_idx / scene.fps
    frame = renderer.render_frame(t)
    frames.append(frame)
    
    if (frame_idx + 1) % 30 == 0:
        print(f"  Rendered {frame_idx + 1}/{total_frames} frames ({(frame_idx+1)/total_frames*100:.1f}%)")

print(f"  Rendered {total_frames}/{total_frames} frames (100.0%)")

# ============================================================================
# Export Video
# ============================================================================

print("\nExporting video...")
output_path = output_dir / "showcase.mp4"

clip = ImageSequenceClip(frames, fps=scene.fps)
clip.write_videofile(
    str(output_path),
    codec='libx264',
    audio=False,
    preset='medium',
    ffmpeg_params=['-crf', '18']
)

print(f"\n✓ Video created: {output_path}")
print(f"  Size: {output_path.stat().st_size / (1024*1024):.2f} MB")
print(f"  Duration: {timeline.duration:.2f}s")
print(f"  Frames: {total_frames}")
