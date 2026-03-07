"""
Mahabharata - The Great War of Dharma (Phase 3 - Audio-Reactive)

This script creates an epic video about the Mahabharata with Phase 3 audio-reactive features:
- Audio analysis of TTS narration
- Beat-synced transitions that align with speech rhythm
- Audio-reactive visual effects:
  * OnsetFlash: Brightness pulses on speech onsets
  * EnergyZoom: Dynamic zoom based on narration energy
  * EnergyBrightness: Brightness responds to voice intensity
  * SpectralColorShift: Color temperature shifts with voice tone
- Cinematic motion effects
- Epic color grading
- TTS narration with subtitles

This demonstrates how Phase 3 makes videos feel more alive and responsive to the narration.
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
    OnsetFlash, EnergyZoom, EnergyBrightness, SpectralColorShift
)

# ============================================================================
# Configuration
# ============================================================================

# Paths
mahabharata_dir = Path("files/mahabharata")
output_dir = Path("output/mahabharata_phase3")
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
# Epic Color Grading Presets (Phase 2)
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
# Audio-Reactive Effect Factory (Phase 3)
# ============================================================================

def create_audio_reactive_effects(audio_sync, style="balanced"):
    """
    Create audio-reactive effects based on style.
    
    Args:
        audio_sync: AudioSync object (will be None initially, set during planning)
        style: "subtle", "balanced", or "dramatic"
    
    Returns:
        List of audio-reactive effect instances
    """
    if style == "subtle":
        # Gentle audio response - good for wisdom/spiritual scenes
        return [
            OnsetFlash(audio_sync, flash_duration=0.15, intensity=0.2),
            EnergyBrightness(audio_sync, brightness_range=(0.95, 1.05), energy_range=(0.0, 1.0))
        ]
    
    elif style == "dramatic":
        # Strong audio response - good for battle/action scenes
        return [
            OnsetFlash(audio_sync, flash_duration=0.25, intensity=0.4),
            EnergyZoom(audio_sync, zoom_range=(1.0, 1.15), energy_range=(0.0, 1.0)),
            EnergyBrightness(audio_sync, brightness_range=(0.9, 1.15), energy_range=(0.0, 1.0))
        ]
    
    else:  # balanced
        # Moderate audio response - good for general narration
        return [
            OnsetFlash(audio_sync, flash_duration=0.2, intensity=0.3),
            EnergyZoom(audio_sync, zoom_range=(1.0, 1.08), energy_range=(0.0, 1.0)),
            SpectralColorShift(audio_sync, temperature_range=(-0.08, 0.08), centroid_range=(1000.0, 3000.0))
        ]

# ============================================================================
# Scene Definition with Audio-Reactive Effects
# ============================================================================

# Note: audio_sync will be None here, but will be populated during planning
# The effects will gracefully degrade if audio analysis fails
audio_sync = None

# Estimate ~3 seconds per line = ~45 seconds total
# 12 images, so ~3.75 seconds per image
clip_duration = 3.75

clips = [
    # Clip 1: Opening - Epic introduction (dramatic)
    ImageClip(
        source=str(image_files[0]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_IN,
        effects=[war_grade] + create_audio_reactive_effects(audio_sync, "dramatic")
    ),
    
    # Clip 2: The two families (balanced)
    ImageClip(
        source=str(image_files[1]),
        duration=clip_duration,
        motion=MotionPreset.PAN_RIGHT,
        effects=[war_grade] + create_audio_reactive_effects(audio_sync, "balanced")
    ),
    
    # Clip 3: Pandavas - righteousness (subtle)
    ImageClip(
        source=str(image_files[2]),
        duration=clip_duration,
        motion=MotionPreset.ZOOM_IN,
        effects=[divine_grade] + create_audio_reactive_effects(audio_sync, "subtle")
    ),
    
    # Clip 4: Kauravas - greed and power (dramatic)
    ImageClip(
        source=str(image_files[3]),
        duration=clip_duration,
        motion=MotionPreset.PAN_LEFT,
        effects=[war_grade] + create_audio_reactive_effects(audio_sync, "dramatic")
    ),
    
    # Clip 5: Betrayal and exile (balanced)
    ImageClip(
        source=str(image_files[4]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_OUT,
        effects=[war_grade] + create_audio_reactive_effects(audio_sync, "balanced")
    ),
    
    # Clip 6: The great battle begins (dramatic)
    ImageClip(
        source=str(image_files[5]),
        duration=clip_duration,
        motion=MotionPreset.PAN_UP,
        effects=[war_grade] + create_audio_reactive_effects(audio_sync, "dramatic")
    ),
    
    # Clip 7: Battlefield of Kurukshetra (dramatic)
    ImageClip(
        source=str(image_files[6]),
        duration=clip_duration,
        motion=MotionPreset.ZOOM_IN,
        effects=[war_grade] + create_audio_reactive_effects(audio_sync, "dramatic")
    ),
    
    # Clip 8: Arjuna's dilemma (subtle)
    ImageClip(
        source=str(image_files[7]),
        duration=clip_duration,
        motion=MotionPreset.PAN_DOWN,
        effects=[wisdom_grade] + create_audio_reactive_effects(audio_sync, "subtle")
    ),
    
    # Clip 9: Krishna reveals wisdom - Bhagavad Gita (subtle)
    ImageClip(
        source=str(image_files[8]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_IN,
        effects=[divine_grade] + create_audio_reactive_effects(audio_sync, "subtle")
    ),
    
    # Clip 10: The eighteen-day war (dramatic)
    ImageClip(
        source=str(image_files[9]),
        duration=clip_duration,
        motion=MotionPreset.PAN_RIGHT,
        effects=[war_grade] + create_audio_reactive_effects(audio_sync, "dramatic")
    ),
    
    # Clip 11: Victory of dharma (balanced)
    ImageClip(
        source=str(image_files[10]),
        duration=clip_duration,
        motion=MotionPreset.ZOOM_OUT,
        effects=[divine_grade] + create_audio_reactive_effects(audio_sync, "balanced")
    ),
    
    # Clip 12: Timeless lesson (subtle)
    ImageClip(
        source=str(image_files[11]),
        duration=clip_duration,
        motion=MotionPreset.KEN_BURNS_ZOOM_OUT,
        effects=[wisdom_grade] + create_audio_reactive_effects(audio_sync, "subtle")
    ),
]

# Transitions with beat synchronization (Phase 3)
# NEAREST_BEAT: Transition starts snap to nearest speech beat
# This makes transitions feel more natural and rhythmic with the narration
transitions = [
    Transition(type=TransitionType.CROSSFADE, duration=1.0, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.FADE_THROUGH_BLACK, duration=0.8, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.CROSSFADE, duration=1.0, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.WIPE_LEFT, duration=0.8, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.CROSSFADE, duration=1.0, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.IRIS_OPEN, duration=1.2, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.CROSSFADE, duration=1.0, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.FADE_THROUGH_WHITE, duration=1.0, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.CROSSFADE, duration=1.0, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.ZOOM_THROUGH, duration=1.0, sync=BeatSync.NEAREST_BEAT),
    Transition(type=TransitionType.CROSSFADE, duration=1.2, sync=BeatSync.NEAREST_BEAT),
]

# Create scene with audio path for Phase 3 analysis
# The audio will be generated by TTS, then analyzed for beats/onsets/energy
scene = Scene(
    clips=clips,
    resolution=(VIDEO_WIDTH, VIDEO_HEIGHT),
    fps=VIDEO_FPS,
    transitions=transitions,
    audio=None  # Will be set to TTS audio path during generation
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
print("MAHABHARATA - THE GREAT WAR OF DHARMA (PHASE 3 - AUDIO-REACTIVE)")
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

print(f"\nTransitions (with Beat Sync):")
for i, trans in enumerate(transitions, 1):
    sync_mode = trans.sync.value if hasattr(trans, 'sync') else 'none'
    print(f"  {i}→{i+1}: {trans.type.value} ({trans.duration}s) [sync: {sync_mode}]")

print(f"\nPhase 3 Audio-Reactive Effects:")
print(f"  ✓ OnsetFlash: Brightness pulses on speech onsets")
print(f"  ✓ EnergyZoom: Dynamic zoom based on voice energy")
print(f"  ✓ EnergyBrightness: Brightness responds to voice intensity")
print(f"  ✓ SpectralColorShift: Color temperature shifts with voice tone")
print(f"  ✓ Beat Sync: Transitions align with speech rhythm")

print(f"\nEffect Intensity by Clip:")
for i, clip in enumerate(clips, 1):
    # Count audio-reactive effects
    audio_effects = [e for e in clip.effects if isinstance(e, (OnsetFlash, EnergyZoom, EnergyBrightness, SpectralColorShift))]
    if audio_effects:
        effect_names = [type(e).__name__ for e in audio_effects]
        print(f"  Clip {i}: {', '.join(effect_names)}")

print(f"\n{'=' * 80}")
print("Generating video with TTS narration and audio analysis...")
print("=" * 80)
print("\nPhase 3 Pipeline:")
print("  1. Generate TTS audio from narration text")
print("  2. Analyze audio for beats, onsets, energy, and spectral features")
print("  3. Sync transitions to speech rhythm")
print("  4. Render frames with audio-reactive effects")
print("  5. Composite subtitles and encode final video")
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
    print("✓ MAHABHARATA PHASE 3 VIDEO CREATED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nOutput location: {video_path}")
    print(f"File size: {video_path.stat().st_size / (1024*1024):.2f} MB")
    
    print(f"\nPhase 3 Features Applied:")
    print(f"  ✓ Audio analysis completed")
    print(f"  ✓ Beat-synced transitions")
    print(f"  ✓ Audio-reactive visual effects")
    print(f"  ✓ Dynamic brightness and zoom")
    print(f"  ✓ Spectral color shifting")
    
    print(f"\nTo play the video:")
    print(f"  macOS:   open {video_path}")
    print(f"  Linux:   xdg-open {video_path}")
    print(f"  Windows: start {video_path}")
    print(f"\nOr simply double-click the file in Finder/Explorer")
    
    # Also show other output files
    print(f"\nAdditional files created:")
    print(f"  Audio: {output_dir / 'output_moviepy.wav'}")
    print(f"  Subtitles: {output_dir / 'output_moviepy.json'}")
    
    print(f"\nCompare with Phase 2 version:")
    print(f"  Phase 2: examples/mahabharata/create_mahabharata_video.py")
    print(f"  Phase 3: examples/mahabharata/create_mahabharata_video_phase3.py")
    print(f"\nNotice how Phase 3 makes the video feel more alive and responsive!")
    
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
    print(f"  4. Ensure librosa is installed: pip install librosa")
    print(f"  5. Check available disk space in output directory")
    
    print(f"\nNote: If librosa is not installed, Phase 3 features will be disabled")
    print(f"      but the video will still render with Phase 2 features.")
