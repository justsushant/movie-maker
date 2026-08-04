"""
Dragon Video - Phase 4 Rich Effects Showcase

Creates multiple dragon videos with different Phase 4 effect styles:
1. Cinematic (color grading + vignette)
2. Retro/VHS (CRT, scan lines, chromatic aberration)
3. Sketch/Artistic (sketch, edge detection, halftone)
4. Glitch/Cyberpunk (glitch effects, chromatic aberration)
5. Dreamy/Ethereal (blur, light leak, color shifts)
"""

import sys
from pathlib import Path
import numpy as np
from moviepy import ImageSequenceClip
import gc

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader
from engine.effects import (
    # Phase 2/3 effects
    brightness, contrast, saturation, vignette,
    # Phase 4 color effects
    sepia, hue_shift, color_temperature, gamma_correction, duotone, posterize,
    # Phase 4 blur effects
    gaussian_blur, motion_blur, pixelate,
    # Phase 4 texture effects
    scan_lines, letterbox, light_leak, border,
    # Phase 4 stylization effects
    sketch, edge_detection, halftone, chromatic_aberration,
    glitch_rgb_split, crt_retro, threshold_bw,
)

# ============================================================================
# Configuration
# ============================================================================

dragon_dir = Path("files/dragon")
output_dir = Path("output/dragon_phase4")
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
# Phase 4 Effect Presets
# ============================================================================

# Style 1: Cinematic Epic
cinematic_effects = [
    gamma_correction(1.2),
    saturation(0.9),
    vignette(0.6),
    color_temperature(6500),
]

# Style 2: Retro VHS
retro_effects = [
    crt_retro(0.15),
    scan_lines(2, 0.3),
    chromatic_aberration(5),
    hue_shift(10),
]

# Style 3: Sketch/Artistic
sketch_effects = [
    sketch(),
]

# Style 4: Glitch Cyberpunk
glitch_effects = [
    glitch_rgb_split(15),
    chromatic_aberration(8),
    scan_lines(1, 0.2),
]

# Style 5: Dreamy Ethereal
dreamy_effects = [
    gaussian_blur(3),
    light_leak(0.4),
    hue_shift(20),
    saturation(1.2),
]

# Style 6: Posterized Comic
comic_effects = [
    posterize(4),
    edge_detection(),
    saturation(1.3),
]

# Style 7: Noir/High Contrast
noir_effects = [
    threshold_bw(120),
    vignette(0.7),
]

# ============================================================================
# Helper Functions
# ============================================================================

def create_scene_with_effects(image_files, effects, name):
    """Create a scene with the given effects applied to all clips."""
    clips = []
    motions = [
        MotionPreset.KEN_BURNS_ZOOM_IN,
        MotionPreset.PAN_RIGHT,
        MotionPreset.ZOOM_IN,
        MotionPreset.PAN_LEFT,
        MotionPreset.KEN_BURNS_ZOOM_OUT,
        MotionPreset.PAN_UP,
        MotionPreset.ZOOM_IN,
        MotionPreset.PAN_DOWN,
        MotionPreset.KEN_BURNS_ZOOM_IN,
        MotionPreset.ZOOM_OUT,
    ]
    
    for i, img_file in enumerate(image_files[:10]):
        clips.append(
            ImageClip(
                source=str(img_file),
                duration=3.0,
                motion=motions[i % len(motions)],
                effects=effects
            )
        )
    
    transitions = [
        Transition(type=TransitionType.CROSSFADE, duration=0.8)
        for _ in range(len(clips) - 1)
    ]
    
    scene = Scene(
        clips=clips,
        transitions=transitions,
        resolution=(1920, 1080),
        fps=30
    )
    
    return scene


def render_video(scene, output_name):
    """Render a scene to video."""
    print(f"\n{'=' * 70}")
    print(f"Rendering: {output_name}")
    print('=' * 70)
    
    print("\nPlanning scene...")
    image_loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    
    print(f"  Timeline duration: {timeline.duration:.2f}s")
    print(f"  Clips: {len(timeline.clips)}")
    print(f"  Transitions: {len(timeline.transitions)}")
    
    print("\nRendering frames...")
    renderer = FrameRenderer(timeline, image_loader)
    
    frames = []
    total_frames = int(timeline.duration * scene.fps)
    
    for frame_idx in range(total_frames):
        t = frame_idx / scene.fps
        frame = renderer.render_frame(t)
        frames.append(frame)
        
        if (frame_idx + 1) % 90 == 0 or frame_idx == total_frames - 1:
            progress = (frame_idx + 1) / total_frames * 100
            print(f"  Progress: {frame_idx + 1}/{total_frames} frames ({progress:.1f}%)")
    
    print("\nExporting video...")
    output_path = output_dir / f"{output_name}.mp4"
    duration = timeline.duration
    
    clip = ImageSequenceClip(frames, fps=scene.fps)
    clip.write_videofile(
        str(output_path),
        codec='libx264',
        audio=False,
        preset='medium',
        ffmpeg_params=['-crf', '18'],
        threads=2  # Limit threads to reduce memory usage
    )
    
    # Clean up
    clip.close()
    del clip
    del frames
    del renderer
    del timeline
    del image_loader
    gc.collect()
    
    print(f"\n✓ Video created: {output_path}")
    print(f"  Size: {output_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"  Duration: {duration:.2f}s")


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("DRAGON VIDEO - PHASE 4 EFFECTS SHOWCASE")
    print("=" * 70)
    print("\nCreating 7 different styled videos...")
    
    styles = [
        ("dragon_cinematic", cinematic_effects, "Cinematic Epic"),
        ("dragon_retro", retro_effects, "Retro VHS"),
        ("dragon_sketch", sketch_effects, "Sketch/Artistic"),
        ("dragon_glitch", glitch_effects, "Glitch Cyberpunk"),
        ("dragon_dreamy", dreamy_effects, "Dreamy Ethereal"),
        ("dragon_comic", comic_effects, "Posterized Comic"),
        ("dragon_noir", noir_effects, "Noir/High Contrast"),
    ]
    
    for output_name, effects, description in styles:
        print(f"\n\nStyle: {description}")
        scene = create_scene_with_effects(image_files, effects, output_name)
        render_video(scene, output_name)
    
    print("\n" + "=" * 70)
    print("✓ ALL VIDEOS CREATED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\nOutput directory: {output_dir}")
    print("\nCreated videos:")
    for output_name, _, description in styles:
        print(f"  • {output_name}.mp4 - {description}")


if __name__ == "__main__":
    main()
