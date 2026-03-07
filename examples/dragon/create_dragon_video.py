"""
Dragon Legends Video - Showcasing Phase 2 Features

This script creates a cinematic dragon-themed video with:
- 10 dragon images with motion effects
- Smooth transitions between clips
- Cinematic color grading and effects
- TTS narration with word-by-word subtitles
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
from engine.effects import brightness, contrast, saturation, vignette, film_grain, chain_effects

# ============================================================================
# Configuration
# ============================================================================

# Paths
dragon_dir = Path("files/dragon")
output_dir = Path("output/dragon_legends")
output_dir.mkdir(parents=True, exist_ok=True)

# Read narration text
with open(dragon_dir / "input.txt", "r", encoding="utf-8") as f:
    narration_text = f.read()

# Get all dragon images (sorted)
image_files = sorted([
    f for f in dragon_dir.glob("*.jpg") 
    if f.is_file()
] + [
    f for f in dragon_dir.glob("*.png") 
    if f.is_file()
])

print(f"Found {len(image_files)} dragon images")

# Video settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30

# ============================================================================
# Cinematic Color Grading
# ============================================================================

# Epic cinematic look - slightly darker, high contrast, desaturated
epic_grade = chain_effects(
    brightness(-0.05),      # Slightly darker for drama
    contrast(1.3),          # High contrast
    saturation(0.85),       # Slightly desaturated
    vignette(intensity=0.5, radius=0.75)  # Strong vignette
)

# Warm fire look - brighter, saturated
fire_grade = chain_effects(
    brightness(0.1),
    contrast(1.2),
    saturation(1.2),
    vignette(intensity=0.3, radius=0.8)
)

# Cool mystical look - desaturated, subtle grain
mystical_grade = chain_effects(
    saturation(0.7),
    film_grain(intensity=0.03),
    vignette(intensity=0.4, radius=0.8)
)

# ============================================================================
# Scene Definition
# ============================================================================

# Estimate ~2.5 seconds per sentence/line = ~45 seconds total
# We have 10 images, so ~4.5 seconds per image
clip_duration = 4.5

clips = [
    # Clip 1: Opening - Epic zoom in
    ImageClip(
        source=str(image_files[0]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_IN,
        effects=[epic_grade]
    ),
    
    # Clip 2: Majestic pan
    ImageClip(
        source=str(image_files[1]),
        duration=clip_duration,
        motion=MotionPreset.PAN_RIGHT,
        effects=[epic_grade]
    ),
    
    # Clip 3: Fire dragon - warm look
    ImageClip(
        source=str(image_files[2]),
        duration=clip_duration,
        motion=MotionPreset.ZOOM_IN,
        effects=[fire_grade]
    ),
    
    # Clip 4: Mystical dragon
    ImageClip(
        source=str(image_files[3]),
        duration=clip_duration,
        motion=MotionPreset.PAN_LEFT,
        effects=[mystical_grade]
    ),
    
    # Clip 5: Epic reveal
    ImageClip(
        source=str(image_files[4]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_OUT,
        effects=[epic_grade]
    ),
    
    # Clip 6: Dramatic pan
    ImageClip(
        source=str(image_files[5]),
        duration=clip_duration,
        motion=MotionPreset.PAN_UP,
        effects=[epic_grade]
    ),
    
    # Clip 7: Fire scene
    ImageClip(
        source=str(image_files[6]),
        duration=clip_duration,
        motion=MotionPreset.ZOOM_IN,
        effects=[fire_grade]
    ),
    
    # Clip 8: Mystical atmosphere
    ImageClip(
        source=str(image_files[7]),
        duration=clip_duration,
        motion=MotionPreset.PAN_DOWN,
        effects=[mystical_grade]
    ),
    
    # Clip 9: Epic battle
    ImageClip(
        source=str(image_files[8]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_IN,
        effects=[epic_grade]
    ),
    
    # Clip 10: Final reveal
    ImageClip(
        source=str(image_files[9]),
        duration=clip_duration,
        motion=MotionPreset.ZOOM_OUT,
        effects=[epic_grade]
    ),
]

# Transitions - mix of dramatic and smooth
transitions = [
    Transition(type=TransitionType.CROSSFADE, duration=1.0),           # 1->2: Smooth
    Transition(type=TransitionType.FADE_THROUGH_BLACK, duration=0.8),  # 2->3: Dramatic
    Transition(type=TransitionType.CROSSFADE, duration=1.0),           # 3->4: Smooth
    Transition(type=TransitionType.IRIS_OPEN, duration=1.2),           # 4->5: Epic reveal
    Transition(type=TransitionType.CROSSFADE, duration=1.0),           # 5->6: Smooth
    Transition(type=TransitionType.SLIDE_LEFT, duration=0.8),          # 6->7: Dynamic
    Transition(type=TransitionType.CROSSFADE, duration=1.0),           # 7->8: Smooth
    Transition(type=TransitionType.ZOOM_THROUGH, duration=1.0),        # 8->9: Dramatic
    Transition(type=TransitionType.CROSSFADE, duration=1.2),           # 9->10: Final smooth
]

# Create scene
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
    bg_color=(0, 0, 0)
)

# Subtitle configuration - cinematic style
subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
    font_size=60,
    base_color=(220, 220, 220),      # Light gray
    highlight_color=(255, 200, 100),  # Golden highlight
    y_margin=0.15,
    vertical_align="bottom"
)

# ============================================================================
# Generate Video
# ============================================================================

print("=" * 80)
print("DRAGON LEGENDS VIDEO - PHASE 2 SHOWCASE")
print("=" * 80)
print(f"\nScene Configuration:")
print(f"  Images: {len(clips)}")
print(f"  Transitions: {len(transitions)}")
print(f"  Clip duration: {clip_duration}s each")
print(f"  Total duration (without transitions): {sum(clip.duration for clip in clips):.1f}s")
print(f"  Total duration (with transitions): {sum(clip.duration for clip in clips) - sum(t.duration for t in transitions):.1f}s")
print(f"  Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS}fps")

print(f"\nMotion Effects:")
for i, clip in enumerate(clips, 1):
    print(f"  Clip {i}: {clip.motion.value}")

print(f"\nTransitions:")
for i, trans in enumerate(transitions, 1):
    print(f"  {i}→{i+1}: {trans.type.value} ({trans.duration}s)")

print(f"\nColor Grading:")
print(f"  Epic grade: {sum(1 for c in clips if c.effects and epic_grade in c.effects)} clips")
print(f"  Fire grade: {sum(1 for c in clips if c.effects and fire_grade in c.effects)} clips")
print(f"  Mystical grade: {sum(1 for c in clips if c.effects and mystical_grade in c.effects)} clips")

print(f"\n{'=' * 80}")
print("Generating video with TTS narration...")
print("=" * 80)
print("\nThis may take a few minutes depending on your system.")
print("Progress will be shown below:\n")

try:
    video_path = generate_video_from_text(
        text=narration_text,
        output_dir=output_dir,
        video_config=video_config,
        subtitle_config=subtitle_config,
        scene=scene
    )
    
    print(f"\n{'=' * 80}")
    print("✓ DRAGON LEGENDS VIDEO CREATED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nOutput location: {video_path}")
    print(f"File size: {video_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"\nTo play the video:")
    print(f"  macOS:   open {video_path}")
    print(f"  Linux:   xdg-open {video_path}")
    print(f"  Windows: start {video_path}")
    print(f"\nOr simply double-click the file in Finder/Explorer")
    
    # Also show other output files
    print(f"\nAdditional files created:")
    print(f"  Audio: {output_dir / 'output_moviepy.wav'}")
    print(f"  Subtitles: {output_dir / 'output_moviepy.json'}")
    
except Exception as e:
    print(f"\n{'=' * 80}")
    print("✗ ERROR GENERATING VIDEO")
    print("=" * 80)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    
    print(f"\nTroubleshooting:")
    print(f"  1. Ensure virtual environment is activated: source .venv/bin/activate")
    print(f"  2. Check that all images exist in: {dragon_dir}")
    print(f"  3. Verify dependencies are installed: make setup")
    print(f"  4. Check available disk space in output directory")
