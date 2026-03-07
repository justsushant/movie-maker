"""
Demo script showcasing all Phase 1 and Phase 2 video engine features.

This script creates a complete video demonstrating:
- Phase 1: Motion effects (Ken Burns, pan, zoom)
- Phase 2: Transitions (blend, geometric, animated)
- Phase 2: Visual effects (color grading, vignette, film grain)

Requirements:
1. Images in tests/fixtures/images/ directory
2. Text narration (can be customized below)
3. Virtual environment activated with all dependencies
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.library import generate_video_from_text
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig, SubtitleMode
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.effects import brightness, contrast, saturation, vignette, film_grain, fade_in, fade_out, chain_effects

# ============================================================================
# Configuration
# ============================================================================

# Output directory
output_dir = Path("output/phase2_showcase")
output_dir.mkdir(parents=True, exist_ok=True)

# Narration text (adjust to match your desired video length)
text = """
Welcome to the video engine showcase.
This demonstrates motion effects and smooth transitions.
Watch as images come to life with professional effects.
Each clip features unique visual enhancements.
The journey continues with stunning animations.
"""

# Video settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30

# ============================================================================
# Scene Definition with All Features
# ============================================================================

# Define image paths (using test fixtures)
# You can replace these with your own images
image_paths = [
    "tests/fixtures/images/landscape.jpg",
    "tests/fixtures/images/portrait.jpg", 
    "tests/fixtures/images/square.jpg",
    "tests/fixtures/images/landscape.jpg",  # Reuse for demo
    "tests/fixtures/images/portrait.jpg",
]

# Create clips with motion effects and visual effects
clips = [
    # Clip 1: Ken Burns zoom with fade in and brightness boost
    ImageClip(
        source=image_paths[0],
        duration=3.0,
        motion=MotionPreset.KEN_BURNS_ZOOM_IN,
        effects=[
            fade_in(1.0),  # Fade in over 1 second
            brightness(0.1),  # Slightly brighter
        ]
    ),
    
    # Clip 2: Pan left with vignette effect
    ImageClip(
        source=image_paths[1],
        duration=3.0,
        motion=MotionPreset.PAN_LEFT,
        effects=[
            vignette(intensity=0.4, radius=0.7),  # Subtle vignette
            contrast(1.2),  # Increase contrast
        ]
    ),
    
    # Clip 3: Zoom out with film grain for vintage look
    ImageClip(
        source=image_paths[2],
        duration=3.0,
        motion=MotionPreset.ZOOM_OUT,
        effects=[
            film_grain(intensity=0.05),  # Subtle grain
            saturation(0.8),  # Slightly desaturated
        ]
    ),
    
    # Clip 4: Pan right with multiple effects chained
    ImageClip(
        source=image_paths[3],
        duration=3.0,
        motion=MotionPreset.PAN_RIGHT,
        effects=[
            chain_effects(
                brightness(0.05),
                contrast(1.1),
                vignette(intensity=0.3, radius=0.8)
            )
        ]
    ),
    
    # Clip 5: Static with fade out
    ImageClip(
        source=image_paths[4],
        duration=3.0,
        motion=MotionPreset.STATIC,
        effects=[
            fade_out(1.0),  # Fade out in last second
        ]
    ),
]

# Define transitions between clips
transitions = [
    # Transition 1->2: Crossfade (classic)
    Transition(
        type=TransitionType.CROSSFADE,
        duration=0.5
    ),
    
    # Transition 2->3: Slide left (geometric)
    Transition(
        type=TransitionType.SLIDE_LEFT,
        duration=0.8
    ),
    
    # Transition 3->4: Iris open (shape-based)
    Transition(
        type=TransitionType.IRIS_OPEN,
        duration=1.0
    ),
    
    # Transition 4->5: Glitch (animated)
    Transition(
        type=TransitionType.GLITCH,
        duration=0.6
    ),
]

# Create the scene
scene = Scene(
    clips=clips,
    resolution=(VIDEO_WIDTH, VIDEO_HEIGHT),
    fps=VIDEO_FPS,
    transitions=transitions
)

# ============================================================================
# Video Configuration
# ============================================================================

video_config = VideoConfig(
    width=VIDEO_WIDTH,
    height=VIDEO_HEIGHT,
    fps=VIDEO_FPS,
    bg_color=(0, 0, 0)  # Black background
)

# Subtitle configuration
subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
    font_size=56,
    base_color=(255, 255, 255),  # White text
    highlight_color=(255, 215, 0),  # Gold highlight
    y_margin=0.12,
    vertical_align="bottom"
)

# ============================================================================
# Generate Video
# ============================================================================

print("=" * 70)
print("PHASE 2 VIDEO ENGINE SHOWCASE")
print("=" * 70)
print(f"\nScene Configuration:")
print(f"  - Clips: {len(clips)}")
print(f"  - Transitions: {len(transitions)}")
print(f"  - Total duration: {sum(clip.duration for clip in clips):.1f}s")
print(f"  - With transitions: {sum(clip.duration for clip in clips) - sum(t.duration for t in transitions):.1f}s")
print(f"  - Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS}fps")
print(f"\nMotion Effects:")
for i, clip in enumerate(clips, 1):
    print(f"  Clip {i}: {clip.motion.value}")
print(f"\nTransitions:")
for i, trans in enumerate(transitions, 1):
    print(f"  {i}→{i+1}: {trans.type.value} ({trans.duration}s)")
print(f"\nVisual Effects:")
for i, clip in enumerate(clips, 1):
    if clip.effects:
        print(f"  Clip {i}: {len(clip.effects)} effect(s)")
    else:
        print(f"  Clip {i}: No effects")

print(f"\n{'=' * 70}")
print("Generating video...")
print("=" * 70)

try:
    video_path = generate_video_from_text(
        text=text,
        output_dir=output_dir,
        video_config=video_config,
        subtitle_config=subtitle_config,
        scene=scene
    )
    
    print(f"\n{'=' * 70}")
    print("✓ VIDEO GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\nOutput: {video_path}")
    print(f"Size: {video_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"\nYou can play the video with:")
    print(f"  open {video_path}  # macOS")
    print(f"  xdg-open {video_path}  # Linux")
    print(f"  start {video_path}  # Windows")
    
except Exception as e:
    print(f"\n{'=' * 70}")
    print("✗ ERROR GENERATING VIDEO")
    print("=" * 70)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    print(f"\nTroubleshooting:")
    print(f"  1. Ensure images exist in tests/fixtures/images/")
    print(f"  2. Check that virtual environment is activated")
    print(f"  3. Verify all dependencies are installed (make setup)")
