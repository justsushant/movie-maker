"""
Mahabharata Video - Phase 4 Rich Effects Showcase

Creates multiple Mahabharata videos with different Phase 4 effect styles:
1. Ancient Epic (sepia, vignette, film grain)
2. Mystical (hue shift, light leak, ethereal)
3. Dramatic (high contrast, chromatic aberration)
4. Illustrated (sketch, halftone, artistic)
5. Modern Cinematic (color grading, subtle effects)
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
    brightness, contrast, saturation, vignette, film_grain,
    # Phase 4 color effects
    sepia, hue_shift, color_temperature, gamma_correction, duotone, posterize, invert,
    # Phase 4 blur effects
    gaussian_blur, motion_blur, pixelate, sharpen,
    # Phase 4 texture effects
    scan_lines, letterbox, light_leak, border, gradient_overlay,
    # Phase 4 stylization effects
    sketch, edge_detection, halftone, chromatic_aberration,
    emboss, crt_retro, threshold_bw, dithering,
)

# ============================================================================
# Configuration
# ============================================================================

mahabharata_dir = Path("files/mahabharata")
output_dir = Path("output/mahabharata_phase4")
output_dir.mkdir(parents=True, exist_ok=True)

# Get all mahabharata images
image_files = sorted([
    f for f in mahabharata_dir.glob("*.jpg") 
    if f.is_file()
] + [
    f for f in mahabharata_dir.glob("*.png") 
    if f.is_file()
])

print(f"Found {len(image_files)} Mahabharata images")

# ============================================================================
# Phase 4 Effect Presets
# ============================================================================

# Style 1: Ancient Epic (sepia tone, aged look)
ancient_effects = [
    sepia(),
    vignette(0.5),
    film_grain(0.04),
    gamma_correction(1.1),
]

# Style 2: Mystical/Divine (ethereal, glowing)
mystical_effects = [
    hue_shift(30),
    light_leak(0.5),
    gaussian_blur(2),
    saturation(1.3),
    brightness(0.1),
]

# Style 3: Dramatic/Intense (high contrast, bold)
dramatic_effects = [
    contrast(1.4),
    chromatic_aberration(6),
    vignette(0.6),
    saturation(0.9),
]

# Style 4: Illustrated/Artistic (sketch-like)
illustrated_effects = [
    sketch(),
    saturation(1.2),
]

# Style 5: Modern Cinematic (clean, professional)
cinematic_effects = [
    gamma_correction(1.15),
    color_temperature(6000),
    saturation(0.95),
    vignette(0.4),
    sharpen(1.2),
]

# Style 6: Duotone/Stylized (two-color look)
duotone_effects = [
    duotone((20, 10, 50), (255, 200, 100)),
    vignette(0.5),
]

# Style 7: Comic Book (posterized, bold)
comic_effects = [
    posterize(4),
    edge_detection(),
    saturation(1.4),
    contrast(1.2),
]

# Style 8: Ethereal Dream (soft, glowing)
ethereal_effects = [
    gaussian_blur(4),
    light_leak(0.6),
    hue_shift(15),
    brightness(0.15),
    saturation(1.1),
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
    
    # Use up to 10 images
    num_images = min(10, len(image_files))
    
    for i in range(num_images):
        clips.append(
            ImageClip(
                source=str(image_files[i]),
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
    print("MAHABHARATA VIDEO - PHASE 4 EFFECTS SHOWCASE")
    print("=" * 70)
    print("\nCreating 8 different styled videos...")
    
    styles = [
        ("mahabharata_ancient", ancient_effects, "Ancient Epic"),
        ("mahabharata_mystical", mystical_effects, "Mystical/Divine"),
        ("mahabharata_dramatic", dramatic_effects, "Dramatic/Intense"),
        ("mahabharata_illustrated", illustrated_effects, "Illustrated/Artistic"),
        ("mahabharata_cinematic", cinematic_effects, "Modern Cinematic"),
        ("mahabharata_duotone", duotone_effects, "Duotone/Stylized"),
        ("mahabharata_comic", comic_effects, "Comic Book"),
        ("mahabharata_ethereal", ethereal_effects, "Ethereal Dream"),
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
