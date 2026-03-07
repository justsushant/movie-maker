"""
Dragon's Journey - Epic Fantasy Adventure (Phase 3 - Audio-Reactive)

This script creates a fantasy video with Phase 3 audio-reactive features:
- Audio analysis of TTS narration
- Beat-synced transitions for dramatic timing
- Audio-reactive visual effects that respond to narration:
  * OnsetFlash: Dramatic brightness pulses on key words
  * EnergyZoom: Dynamic zoom during intense moments
  * EnergyBrightness: Brightness pulses with voice energy
  * EnergyShake: Camera shake during action sequences
  * SpectralColorShift: Color shifts with voice tone
- Cinematic motion and transitions
- Fantasy color grading
- TTS narration with subtitles

Perfect for fantasy storytelling where visuals should react to the drama of the narration!
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api.library import generate_video_from_text
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig, SubtitleMode
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType, BeatSync
from engine.effects import (
    brightness, contrast, saturation, vignette, film_grain, chain_effects,
    OnsetFlash, OnsetZoomPulse, EnergyZoom, EnergyBrightness, EnergyShake, SpectralColorShift
)

# ============================================================================
# Configuration
# ============================================================================

# Paths
dragon_dir = Path("files/dragon")
output_dir = Path("output/dragon_phase3")
output_dir.mkdir(parents=True, exist_ok=True)

# Read narration text
with open(dragon_dir / "input.txt", "r", encoding="utf-8") as f:
    narration_text = f.read()

# Get all images (sorted)
image_files = sorted([
    f for f in dragon_dir.glob("*.jpg") 
    if f.is_file()
])

print(f"Found {len(image_files)} dragon images")

# Video settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30

# ============================================================================
# Fantasy Color Grading Presets
# ============================================================================

# Mystical/magical look - enhanced colors, soft glow
mystical_grade = chain_effects(
    brightness(0.08),
    contrast(1.15),
    saturation(1.25),
    vignette(intensity=0.3, radius=0.85)
)

# Dark/ominous look - for danger and conflict
dark_grade = chain_effects(
    brightness(-0.12),
    contrast(1.4),
    saturation(0.85),
    vignette(intensity=0.6, radius=0.7)
)

# Epic/heroic look - bright, high contrast
epic_grade = chain_effects(
    brightness(0.05),
    contrast(1.3),
    saturation(1.15),
    vignette(intensity=0.4, radius=0.75)
)

# Ancient/legendary look - desaturated with grain
ancient_grade = chain_effects(
    brightness(-0.05),
    contrast(1.25),
    saturation(0.8),
    film_grain(intensity=0.05),
    vignette(intensity=0.5, radius=0.75)
)

# ============================================================================
# Audio-Reactive Effect Presets for Fantasy Storytelling
# ============================================================================

def create_fantasy_effects(audio_sync, scene_type="adventure"):
    """
    Create audio-reactive effects tailored for fantasy storytelling.
    
    Args:
        audio_sync: AudioSync object (None initially, set during planning)
        scene_type: "mystical", "action", "adventure", or "dramatic"
    
    Returns:
        List of audio-reactive effect instances
    """
    if scene_type == "mystical":
        # Gentle, magical response - for wonder and discovery
        return [
            OnsetFlash(audio_sync, flash_duration=0.25, intensity=0.25),
            SpectralColorShift(audio_sync, temperature_range=(-0.12, 0.12), centroid_range=(1000.0, 3000.0)),
            EnergyBrightness(audio_sync, brightness_range=(0.95, 1.08), energy_range=(0.0, 1.0))
        ]
    
    elif scene_type == "action":
        # Intense response - for battles and dramatic moments
        return [
            OnsetFlash(audio_sync, flash_duration=0.2, intensity=0.45),
            OnsetZoomPulse(audio_sync, pulse_duration=0.3, zoom_magnitude=1.12),
            EnergyShake(audio_sync, shake_range=(0.0, 8.0), energy_range=(0.0, 1.0)),
            EnergyBrightness(audio_sync, brightness_range=(0.88, 1.18), energy_range=(0.0, 1.0))
        ]
    
    elif scene_type == "dramatic":
        # Strong emotional response - for key story moments
        return [
            OnsetFlash(audio_sync, flash_duration=0.3, intensity=0.35),
            EnergyZoom(audio_sync, zoom_range=(1.0, 1.12), energy_range=(0.0, 1.0)),
            SpectralColorShift(audio_sync, temperature_range=(-0.1, 0.1), centroid_range=(1000.0, 3000.0))
        ]
    
    else:  # adventure (balanced)
        # Moderate response - for general storytelling
        return [
            OnsetFlash(audio_sync, flash_duration=0.22, intensity=0.3),
            EnergyZoom(audio_sync, zoom_range=(1.0, 1.1), energy_range=(0.0, 1.0)),
            EnergyBrightness(audio_sync, brightness_range=(0.92, 1.1), energy_range=(0.0, 1.0))
        ]

# ============================================================================
# Scene Definition with Audio-Reactive Effects
# ============================================================================

audio_sync = None  # Will be populated during planning
clip_duration = 4.0  # Adjust based on narration length

clips = [
    # Opening - mystical discovery
    ImageClip(
        source=str(image_files[0]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_IN,
        effects=[mystical_grade] + create_fantasy_effects(audio_sync, "mystical")
    ),
    
    # Dragon awakens - dramatic
    ImageClip(
        source=str(image_files[1]),
        duration=clip_duration,
        motion=MotionPreset.ZOOM_IN,
        effects=[dark_grade] + create_fantasy_effects(audio_sync, "dramatic")
    ),
    
    # First flight - adventure
    ImageClip(
        source=str(image_files[2]),
        duration=clip_duration,
        motion=MotionPreset.PAN_UP,
        effects=[epic_grade] + create_fantasy_effects(audio_sync, "adventure")
    ),
    
    # Danger approaches - action
    ImageClip(
        source=str(image_files[3]),
        duration=clip_duration,
        motion=MotionPreset.PAN_LEFT,
        effects=[dark_grade] + create_fantasy_effects(audio_sync, "action")
    ),
    
    # Epic battle - intense action
    ImageClip(
        source=str(image_files[4]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_OUT,
        effects=[dark_grade] + create_fantasy_effects(audio_sync, "action")
    ),
    
    # Victory - epic
    ImageClip(
        source=str(image_files[5]),
        duration=clip_duration,
        motion=MotionPreset.ZOOM_OUT,
        effects=[epic_grade] + create_fantasy_effects(audio_sync, "dramatic")
    ),
    
    # New horizon - mystical
    ImageClip(
        source=str(image_files[6]),
        duration=clip_duration,
        motion=MotionPreset.PAN_RIGHT,
        effects=[mystical_grade] + create_fantasy_effects(audio_sync, "mystical")
    ),
    
    # Legend continues - ancient
    ImageClip(
        source=str(image_files[7]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_IN,
        effects=[ancient_grade] + create_fantasy_effects(audio_sync, "adventure")
    ),
]

# Transitions with beat synchronization for dramatic timing
transitions = [
    Transition(type=TransitionType.CROSSFADE, duration=0.8, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.FADE_THROUGH_BLACK, duration=1.0, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.ZOOM_THROUGH, duration=0.9, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.WIPE_RIGHT, duration=0.7, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.IRIS_OPEN, duration=1.2, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.CROSSFADE, duration=1.0, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.FADE_THROUGH_WHITE, duration=0.9, sync=BeatSync.NEAREST_BEAT),
]

# Create scene
scene = Scene(
    clips=clips,
    resolution=(VIDEO_WIDTH, VIDEO_HEIGHT),
    fps=VIDEO_FPS,
    transitions=transitions,
    audio=None  # Will be set to TTS audio during generation
)

# ============================================================================
# Video Configuration
# ============================================================================

video_config = VideoConfig(
    width=VIDEO_WIDTH,
    height=VIDEO_HEIGHT,
    fps=VIDEO_FPS,
    bg_color=(10, 10, 20)  # Dark blue-black for fantasy
)

# Subtitle configuration - fantasy style with magical colors
subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
    font_size=56,
    base_color=(220, 220, 240),      # Soft white-blue
    highlight_color=(100, 200, 255),  # Magical cyan highlight
    y_margin=0.15,
    vertical_align="bottom"
)

# ============================================================================
# Generate Video
# ============================================================================

print("=" * 80)
print("DRAGON'S JOURNEY - EPIC FANTASY ADVENTURE (PHASE 3)")
print("=" * 80)
print(f"\nScene Configuration:")
print(f"  Images: {len(clips)}")
print(f"  Transitions: {len(transitions)}")
print(f"  Clip duration: {clip_duration}s each")
print(f"  Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS}fps")

print(f"\nPhase 3 Audio-Reactive Features:")
print(f"  ✓ OnsetFlash: Dramatic brightness pulses")
print(f"  ✓ OnsetZoomPulse: Zoom pulses on key moments")
print(f"  ✓ EnergyZoom: Dynamic zoom with voice intensity")
print(f"  ✓ EnergyBrightness: Brightness responds to narration")
print(f"  ✓ EnergyShake: Camera shake during action")
print(f"  ✓ SpectralColorShift: Color shifts with voice tone")
print(f"  ✓ Beat Sync: Transitions align with speech rhythm")

print(f"\nScene Types:")
for i, clip in enumerate(clips, 1):
    audio_effects = [e for e in clip.effects if isinstance(e, (OnsetFlash, OnsetZoomPulse, EnergyZoom, EnergyBrightness, EnergyShake, SpectralColorShift))]
    if audio_effects:
        effect_count = len(audio_effects)
        print(f"  Clip {i}: {effect_count} audio-reactive effects")

print(f"\n{'=' * 80}")
print("Generating fantasy video with audio-reactive effects...")
print("=" * 80)
print("\nThis creates a truly immersive experience where the visuals")
print("respond dynamically to the narration, making the story come alive!")
print("\nProgress will be shown below:\n")

try:
    video_path = generate_video_from_text(
        text=narration_text,
        output_dir=output_dir,
        video_config=video_config,
        subtitle_config=subtitle_config,
        scene=scene
    )
    
    print(f"\n{'=' * 80}")
    print("✓ DRAGON'S JOURNEY PHASE 3 VIDEO CREATED!")
    print("=" * 80)
    print(f"\nOutput: {video_path}")
    print(f"Size: {video_path.stat().st_size / (1024*1024):.2f} MB")
    
    print(f"\nPhase 3 Magic Applied:")
    print(f"  ✓ Audio analyzed for beats, onsets, and energy")
    print(f"  ✓ Transitions synced to speech rhythm")
    print(f"  ✓ Visual effects respond to voice intensity")
    print(f"  ✓ Colors shift with voice tone")
    print(f"  ✓ Camera movements react to narration")
    
    print(f"\nWatch the video and notice how:")
    print(f"  • Brightness pulses on emphasized words")
    print(f"  • Zoom responds to voice intensity")
    print(f"  • Colors shift with emotional tone")
    print(f"  • Transitions feel natural with speech rhythm")
    print(f"  • Action scenes have dynamic camera shake")
    
    print(f"\nTo play: open {video_path}")
    
except Exception as e:
    print(f"\n{'=' * 80}")
    print("✗ ERROR")
    print("=" * 80)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    
    print(f"\nNote: Phase 3 requires librosa for audio analysis.")
    print(f"      Install with: pip install librosa")
    print(f"      Without librosa, video will render with Phase 2 features only.")
