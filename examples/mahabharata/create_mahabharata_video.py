"""
Mahabharata - The Great War of Dharma

This script creates an epic video about the Mahabharata with:
- 12 images depicting the great epic
- Cinematic motion effects
- Dramatic transitions
- Epic color grading
- TTS narration with subtitles
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
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
mahabharata_dir = Path("files/mahabharata")
output_dir = Path("output/mahabharata_epic")
output_dir.mkdir(parents=True, exist_ok=True)

# Read narration text
with open(mahabharata_dir / "input.txt", "r", encoding="utf-8") as f:
    narration_text = f.read()

# Get all images (sorted)
image_files = sorted([
    f for f in mahabharata_dir.glob("*.jpg") 
    if f.is_file()
])

print(f"Found {len(image_files)} Mahabharata images")

# Video settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30

# ============================================================================
# Epic Color Grading Presets
# ============================================================================

# Epic war look - dark, high contrast, desaturated
war_grade = chain_effects(
    brightness(-0.08),
    contrast(1.35),
    saturation(0.8),
    vignette(intensity=0.55, radius=0.7)
)

# Divine/spiritual look - brighter, golden tones
divine_grade = chain_effects(
    brightness(0.05),
    contrast(1.25),
    saturation(1.1),
    vignette(intensity=0.35, radius=0.8)
)

# Ancient wisdom look - desaturated, film grain
wisdom_grade = chain_effects(
    brightness(-0.03),
    contrast(1.2),
    saturation(0.75),
    film_grain(intensity=0.04),
    vignette(intensity=0.45, radius=0.75)
)

# ============================================================================
# Scene Definition
# ============================================================================

# Estimate ~3 seconds per line = ~45 seconds total
# 12 images, so ~3.75 seconds per image
clip_duration = 3.75

clips = [
    # Clip 1: Opening - Epic introduction
    ImageClip(
        source=str(image_files[0]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_IN,
        effects=[war_grade]
    ),
    
    # Clip 2: The two families
    ImageClip(
        source=str(image_files[1]),
        duration=clip_duration,
        motion=MotionPreset.PAN_RIGHT,
        effects=[war_grade]
    ),
    
    # Clip 3: Pandavas - righteousness
    ImageClip(
        source=str(image_files[2]),
        duration=clip_duration,
        motion=MotionPreset.ZOOM_IN,
        effects=[divine_grade]
    ),
    
    # Clip 4: Kauravas - greed and power
    ImageClip(
        source=str(image_files[3]),
        duration=clip_duration,
        motion=MotionPreset.PAN_LEFT,
        effects=[war_grade]
    ),
    
    # Clip 5: Betrayal and exile
    ImageClip(
        source=str(image_files[4]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_OUT,
        effects=[war_grade]
    ),
    
    # Clip 6: The great battle begins
    ImageClip(
        source=str(image_files[5]),
        duration=clip_duration,
        motion=MotionPreset.PAN_UP,
        effects=[war_grade]
    ),
    
    # Clip 7: Battlefield of Kurukshetra
    ImageClip(
        source=str(image_files[6]),
        duration=clip_duration,
        motion=MotionPreset.ZOOM_IN,
        effects=[war_grade]
    ),
    
    # Clip 8: Arjuna's dilemma
    ImageClip(
        source=str(image_files[7]),
        duration=clip_duration,
        motion=MotionPreset.PAN_DOWN,
        effects=[wisdom_grade]
    ),
    
    # Clip 9: Krishna reveals wisdom - Bhagavad Gita
    ImageClip(
        source=str(image_files[8]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_IN,
        effects=[divine_grade]
    ),
    
    # Clip 10: The eighteen-day war
    ImageClip(
        source=str(image_files[9]),
        duration=clip_duration,
        motion=MotionPreset.PAN_RIGHT,
        effects=[war_grade]
    ),
    
    # Clip 11: Victory of dharma
    ImageClip(
        source=str(image_files[10]),
        duration=clip_duration,
        motion=MotionPreset.ZOOM_OUT,
        effects=[divine_grade]
    ),
    
    # Clip 12: Timeless lesson
    ImageClip(
        source=str(image_files[11]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_OUT,
        effects=[wisdom_grade]
    ),
]

# Transitions - mix of dramatic and spiritual
transitions = [
    Transition(type=TransitionType.CROSSFADE, duration=1.0),           # 1->2: Smooth
    Transition(type=TransitionType.FADE_THROUGH_BLACK, duration=0.8),  # 2->3: Dramatic
    Transition(type=TransitionType.CROSSFADE, duration=1.0),           # 3->4: Smooth
    Transition(type=TransitionType.WIPE_LEFT, duration=0.8),           # 4->5: Conflict
    Transition(type=TransitionType.CROSSFADE, duration=1.0),           # 5->6: Smooth
    Transition(type=TransitionType.IRIS_OPEN, duration=1.2),           # 6->7: Epic reveal
    Transition(type=TransitionType.CROSSFADE, duration=1.0),           # 7->8: Smooth
    Transition(type=TransitionType.FADE_THROUGH_WHITE, duration=1.0),  # 8->9: Divine light
    Transition(type=TransitionType.CROSSFADE, duration=1.0),           # 9->10: Smooth
    Transition(type=TransitionType.ZOOM_THROUGH, duration=1.0),        # 10->11: Dramatic
    Transition(type=TransitionType.CROSSFADE, duration=1.2),           # 11->12: Final smooth
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

# Subtitle configuration - epic style with saffron/gold colors
subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
    font_size=58,
    base_color=(240, 240, 240),      # Off-white
    highlight_color=(255, 153, 51),  # Saffron/golden highlight
    y_margin=0.15,
    vertical_align="bottom"
)

# ============================================================================
# Generate Video
# ============================================================================

print("=" * 80)
print("MAHABHARATA - THE GREAT WAR OF DHARMA")
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
print(f"  War grade: {sum(1 for c in clips if c.effects and war_grade in c.effects)} clips")
print(f"  Divine grade: {sum(1 for c in clips if c.effects and divine_grade in c.effects)} clips")
print(f"  Wisdom grade: {sum(1 for c in clips if c.effects and wisdom_grade in c.effects)} clips")

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
    print("✓ MAHABHARATA VIDEO CREATED SUCCESSFULLY!")
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
    print(f"  2. Check that all images exist in: {mahabharata_dir}")
    print(f"  3. Verify dependencies are installed: make setup")
    print(f"  4. Check available disk space in output directory")
