# Phase 2 Video Engine - Complete Usage Guide

## Overview

Phase 2 adds **transitions** and **visual effects** to the video engine, enabling professional-looking videos with smooth blends between clips and cinematic color grading.

## What You Need

### 1. Images
Place your images in any directory. Supported formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- Other formats supported by PIL/Pillow

**Recommended:**
- Resolution: 1920x1080 or higher
- Aspect ratio: Match your target video resolution
- Quality: High-quality images for best results

### 2. Text Script (for narrated videos)
Create a text file with your narration:
```
files/input.txt
```

Or pass text directly to the API.

### 3. Python Environment
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Ensure dependencies are installed
make setup
```

## Available Features

### Phase 1: Motion Effects
```python
from engine.scene import MotionPreset

MotionPreset.STATIC              # No movement
MotionPreset.KEN_BURNS_ZOOM_IN   # Slow zoom in
MotionPreset.KEN_BURNS_ZOOM_OUT  # Slow zoom out
MotionPreset.PAN_LEFT            # Pan left
MotionPreset.PAN_RIGHT           # Pan right
MotionPreset.PAN_UP              # Pan up
MotionPreset.PAN_DOWN            # Pan down
MotionPreset.ZOOM_IN             # Zoom in
MotionPreset.ZOOM_OUT            # Zoom out
```

### Phase 2: Transitions (24 types)

#### Blend Transitions
```python
from engine.scene import TransitionType

TransitionType.CROSSFADE              # Classic crossfade
TransitionType.FADE_THROUGH_BLACK     # Fade to black, then from black
TransitionType.FADE_THROUGH_WHITE     # Fade to white, then from white
```

#### Geometric Transitions - Slides
```python
TransitionType.SLIDE_LEFT    # New clip slides in from right
TransitionType.SLIDE_RIGHT   # New clip slides in from left
TransitionType.SLIDE_UP      # New clip slides in from bottom
TransitionType.SLIDE_DOWN    # New clip slides in from top
```

#### Geometric Transitions - Pushes
```python
TransitionType.PUSH_LEFT     # Both clips move left together
TransitionType.PUSH_RIGHT    # Both clips move right together
TransitionType.PUSH_UP       # Both clips move up together
TransitionType.PUSH_DOWN     # Both clips move down together
```

#### Geometric Transitions - Wipes
```python
TransitionType.WIPE_LEFT     # Hard edge wipe left to right
TransitionType.WIPE_RIGHT    # Hard edge wipe right to left
TransitionType.WIPE_UP       # Hard edge wipe top to bottom
TransitionType.WIPE_DOWN     # Hard edge wipe bottom to top
```

#### Geometric Transitions - Shapes
```python
TransitionType.IRIS_OPEN          # Circular reveal from center
TransitionType.IRIS_CLOSE         # Circular close to center
TransitionType.CLOCK_WIPE         # Clockwise sweep from 12 o'clock
TransitionType.DIAMOND_WIPE       # Diamond shape reveal
TransitionType.BLINDS_HORIZONTAL  # Horizontal venetian blinds
TransitionType.BLINDS_VERTICAL    # Vertical venetian blinds
```

#### Animated Transitions
```python
TransitionType.ZOOM_THROUGH  # Zoom through effect
TransitionType.WHIP_PAN      # Fast motion blur pan
TransitionType.PIXELATE      # Pixelate/unpixelate effect
TransitionType.GLITCH        # Digital glitch effect
```

### Phase 2: Visual Effects

#### Color Effects
```python
from engine.effects import brightness, contrast, saturation, vignette

brightness(0.2)              # Increase brightness (range: -1.0 to 1.0)
brightness(-0.3)             # Decrease brightness

contrast(1.5)                # Increase contrast (range: 0.0 to 2.0)
contrast(0.7)                # Decrease contrast

saturation(1.3)              # Increase saturation (range: 0.0 to 2.0)
saturation(0.5)              # Decrease saturation
saturation(0.0)              # Grayscale

vignette(intensity=0.5, radius=0.8)  # Darken edges
```

#### Texture Effects
```python
from engine.effects import film_grain

film_grain(intensity=0.1)    # Add film grain (range: 0.0 to 1.0)
```

#### Animated Effects
```python
from engine.effects import fade_in, fade_out, pulse

fade_in(1.0)                 # Fade in from black over 1 second
fade_out(1.5)                # Fade out to black over 1.5 seconds
pulse(frequency=2.0, amount=0.2)  # Pulsing brightness
```

#### Chaining Effects
```python
from engine.effects import chain_effects

# Apply multiple effects in sequence
chain_effects(
    brightness(0.1),
    contrast(1.2),
    vignette(intensity=0.3)
)
```

## Usage Examples

### Example 1: Simple Video with Transitions

```python
from pathlib import Path
from api.library import generate_video_from_text
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType

# Define scene
scene = Scene(
    clips=[
        ImageClip(
            source="images/photo1.jpg",
            duration=3.0,
            motion=MotionPreset.KEN_BURNS_ZOOM_IN
        ),
        ImageClip(
            source="images/photo2.jpg",
            duration=3.0,
            motion=MotionPreset.PAN_LEFT
        ),
        ImageClip(
            source="images/photo3.jpg",
            duration=3.0,
            motion=MotionPreset.ZOOM_OUT
        ),
    ],
    transitions=[
        Transition(type=TransitionType.CROSSFADE, duration=0.5),
        Transition(type=TransitionType.SLIDE_LEFT, duration=0.8),
    ],
    resolution=(1920, 1080),
    fps=30
)

# Generate video
text = "Your narration text here."
output_dir = Path("output/my_video")

video_path = generate_video_from_text(
    text=text,
    output_dir=output_dir,
    scene=scene
)
```

### Example 2: Video with Effects

```python
from engine.effects import brightness, vignette, film_grain

scene = Scene(
    clips=[
        ImageClip(
            source="images/photo1.jpg",
            duration=3.0,
            motion=MotionPreset.STATIC,
            effects=[
                brightness(0.1),
                vignette(intensity=0.4, radius=0.7)
            ]
        ),
        ImageClip(
            source="images/photo2.jpg",
            duration=3.0,
            motion=MotionPreset.PAN_RIGHT,
            effects=[
                film_grain(intensity=0.05)
            ]
        ),
    ],
    transitions=[
        Transition(type=TransitionType.IRIS_OPEN, duration=1.0)
    ],
    resolution=(1920, 1080),
    fps=30
)
```

### Example 3: Cinematic Look with Chained Effects

```python
from engine.effects import chain_effects, brightness, contrast, saturation, vignette

# Create a cinematic color grade
cinematic_grade = chain_effects(
    brightness(0.05),
    contrast(1.2),
    saturation(0.9),
    vignette(intensity=0.5, radius=0.75)
)

scene = Scene(
    clips=[
        ImageClip(
            source="images/photo1.jpg",
            duration=4.0,
            motion=MotionPreset.KEN_BURNS_ZOOM_IN,
            effects=[cinematic_grade]
        ),
        ImageClip(
            source="images/photo2.jpg",
            duration=4.0,
            motion=MotionPreset.PAN_LEFT,
            effects=[cinematic_grade]
        ),
    ],
    transitions=[
        Transition(type=TransitionType.CROSSFADE, duration=1.0)
    ],
    resolution=(1920, 1080),
    fps=30
)
```

### Example 4: Video Without Narration (Visual Only)

```python
from pathlib import Path
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader
from moviepy.editor import ImageSequenceClip

# Create scene
scene = Scene(
    clips=[
        ImageClip("images/photo1.jpg", duration=2.0, motion=MotionPreset.ZOOM_IN),
        ImageClip("images/photo2.jpg", duration=2.0, motion=MotionPreset.PAN_LEFT),
    ],
    transitions=[
        Transition(type=TransitionType.CROSSFADE, duration=0.5)
    ],
    resolution=(1920, 1080),
    fps=30
)

# Plan and render
planner = ScenePlanner()
timeline = planner.plan(scene)

image_loader = ImageLoader()
renderer = FrameRenderer(timeline, image_loader)

# Generate frames
frames = []
total_frames = int(timeline.duration * scene.fps)
for frame_idx in range(total_frames):
    t = frame_idx / scene.fps
    frame = renderer.render_frame(t)
    frames.append(frame)

# Export
clip = ImageSequenceClip(frames, fps=scene.fps)
clip.write_videofile("output/video.mp4", codec='libx264')
```

## Running the Demo Scripts

### Full Showcase with Narration
```bash
python demo_phase2_showcase.py
```
Creates a complete video with TTS narration, subtitles, transitions, and effects.

### Simple Visual Demo (No TTS)
```bash
python demo_phase2_simple.py
```
Creates a video with just transitions and effects, no narration.

## Tips and Best Practices

### Transition Duration
- **Short transitions (0.3-0.5s)**: Fast-paced, energetic videos
- **Medium transitions (0.5-1.0s)**: Standard, professional look
- **Long transitions (1.0-2.0s)**: Slow, cinematic feel

### Effect Intensity
- Start subtle and increase gradually
- Brightness: ±0.1 to ±0.2 for subtle adjustments
- Contrast: 1.1 to 1.3 for enhancement
- Saturation: 0.8 to 1.2 for natural looks
- Vignette: 0.3 to 0.5 intensity for subtle darkening

### Performance
- 1080p rendering: ~2-3ms per frame (no effects)
- Effects add overhead: ~5-10ms per effect
- Transitions: Blend <50ms, Geometric <100ms, Animated <150ms
- Use lower resolution for testing, full resolution for final export

### Transition Selection
- **Crossfade**: Universal, works for any content
- **Slides/Pushes**: Good for related content, directional flow
- **Wipes**: Clean, professional, good for presentations
- **Iris/Shapes**: Dramatic, attention-grabbing
- **Animated**: Modern, energetic, use sparingly

## Troubleshooting

### Images Not Found
```python
# Use absolute paths or Path objects
from pathlib import Path
image_path = Path("images/photo.jpg").absolute()
```

### Memory Issues with Large Videos
- Reduce resolution during testing
- Use fewer clips or shorter durations
- Process in batches if needed

### Slow Rendering
- Reduce FPS for testing (15-20 fps)
- Use simpler transitions (crossfade instead of animated)
- Minimize effect chains

### Transition Duration Errors
```
ValueError: Transition duration exceeds clip duration
```
Solution: Ensure transition duration ≤ min(clip_a.duration, clip_b.duration)

## File Structure

```
your_project/
├── images/                    # Your image files
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── photo3.jpg
├── files/
│   └── input.txt             # Narration text (optional)
├── output/                   # Generated videos
│   └── my_video/
│       ├── output_moviepy.wav
│       ├── output_moviepy.json
│       └── output_video.mp4
└── your_script.py            # Your video generation script
```

## Next Steps

1. **Start Simple**: Create a basic video with 2-3 clips and crossfade transitions
2. **Add Motion**: Experiment with different motion presets
3. **Try Transitions**: Test different transition types to find your style
4. **Apply Effects**: Add subtle color grading and vignettes
5. **Combine Features**: Create complex scenes with multiple effects and transitions

## Reference

- **Phase 1 Implementation**: `.kiro/specs/video-engine-phase-1/`
- **Phase 2 Implementation**: `.kiro/specs/video-engine-phase-2/`
- **Test Examples**: `tests/test_phase2_integration.py`
- **API Documentation**: `api/library.py`

## Support

For issues or questions:
1. Check test files for working examples
2. Review PROGRESS.md for implementation details
3. Examine integration tests for usage patterns


---

# Phase 3 Video Engine - Audio-Reactive Features

## Overview

Phase 3 adds **audio analysis and synchronization** capabilities, enabling visual effects that respond dynamically to audio. Videos can now pulse with beats, flash on onsets, zoom with energy, and shift colors with audio tone.

## What's New in Phase 3

- **Audio Analysis**: Automatic extraction of beats, onsets, energy, and spectral features from audio files
- **Beat Synchronization**: Transitions can snap to musical beats for rhythm-aligned editing
- **Audio-Reactive Effects**: 6 new effects that respond to audio in real-time
- **Graceful Degradation**: All audio features are optional; system works without librosa or audio files

## Requirements

### Optional: Audio Analysis

```bash
# Install librosa for audio analysis (optional)
pip install librosa
```

If librosa is not installed, the system will log a warning and continue without audio features. All Phase 1 and Phase 2 functionality works unchanged.

## Audio Analysis Features

### Supported Audio Formats

- WAV (.wav)
- MP3 (.mp3)
- OGG (.ogg)
- FLAC (.flac)
- Other formats supported by librosa

### Extracted Features

When you provide an audio file to a Scene, the system automatically analyzes:

1. **Beats**: Rhythmic pulses detected using beat tracking
2. **Onsets**: Sharp transients marking sound event starts (percussive hits, word starts)
3. **Energy Envelope**: RMS loudness over time
4. **Spectral Centroid**: Brightness/tone of the audio spectrum (Hz)

## Beat Synchronization

### BeatSync Modes

```python
from engine.scene import BeatSync

BeatSync.NONE           # Use declared timing (default)
BeatSync.NEAREST_BEAT   # Snap transition start to nearest beat
BeatSync.BEAT_GRID      # Snap both start and end to beats
```

### Usage

```python
from engine.scene import Scene, ImageClip, Transition, TransitionType, BeatSync

scene = Scene(
    clips=[
        ImageClip("image1.jpg", duration=2.0),
        ImageClip("image2.jpg", duration=2.0),
        ImageClip("image3.jpg", duration=2.0),
    ],
    transitions=[
        Transition(
            type=TransitionType.CROSSFADE,
            duration=0.5,
            sync=BeatSync.NEAREST_BEAT  # Snap to nearest beat
        ),
        Transition(
            type=TransitionType.SLIDE_LEFT,
            duration=0.8,
            sync=BeatSync.BEAT_GRID  # Snap both boundaries to beats
        ),
    ],
    audio="audio/music.mp3",  # Audio file for analysis
    resolution=(1920, 1080),
    fps=30
)
```

### How Beat Sync Works

- **NONE**: Uses your declared transition timings exactly (default behavior)
- **NEAREST_BEAT**: Adjusts transition start time to the nearest detected beat
- **BEAT_GRID**: Adjusts both start and end times to align with beats, creating rhythm-locked transitions
- If beat snapping would create invalid durations, the system falls back to declared timing with a warning

## Audio-Reactive Effects

Phase 3 adds 6 new effects that respond to audio features in real-time.

### Onset-Triggered Effects

These effects activate when sharp transients (onsets) are detected in the audio.

#### OnsetFlash

Brightens the frame when an onset is detected, with smooth decay.

```python
from engine.effects import OnsetFlash

# Create effect (requires AudioSync from scene planning)
flash_effect = OnsetFlash(
    audio_sync=timeline.audio_sync,  # Provided by planner
    flash_duration=0.2,               # Flash lasts 0.2 seconds
    intensity=0.5,                    # 50% brightness increase
    easing=ease_out_cubic             # Smooth decay
)

# Use in clip
ImageClip(
    source="image.jpg",
    duration=3.0,
    effects=[flash_effect]
)
```

**Parameters:**
- `audio_sync`: AudioSync object (None for graceful degradation)
- `flash_duration`: Duration of flash effect in seconds (default: 0.2)
- `intensity`: Flash intensity 0.0-1.0, where 1.0 doubles brightness (default: 0.5)
- `easing`: Easing function for flash decay (default: ease_out_cubic)

#### OnsetZoomPulse

Scales the frame when an onset is detected, creating a pulsing zoom effect.

```python
from engine.effects import OnsetZoomPulse

pulse_effect = OnsetZoomPulse(
    audio_sync=timeline.audio_sync,
    pulse_duration=0.3,      # Pulse lasts 0.3 seconds
    zoom_magnitude=1.1,      # 10% zoom
    easing=ease_out_cubic
)
```

**Parameters:**
- `audio_sync`: AudioSync object (None for graceful degradation)
- `pulse_duration`: Duration of pulse effect in seconds (default: 0.3)
- `zoom_magnitude`: Maximum zoom scale, e.g., 1.1 = 10% zoom (default: 1.1)
- `easing`: Easing function for pulse decay (default: ease_out_cubic)

### Energy-Driven Effects

These effects continuously respond to audio loudness (energy envelope).

#### EnergyZoom

Scales the frame based on audio energy level.

```python
from engine.effects import EnergyZoom

energy_zoom = EnergyZoom(
    audio_sync=timeline.audio_sync,
    zoom_range=(1.0, 1.2),      # Zoom from 1.0x to 1.2x
    energy_range=(0.0, 1.0)     # Map energy 0.0-1.0 to zoom range
)
```

**Parameters:**
- `audio_sync`: AudioSync object (None for graceful degradation)
- `zoom_range`: Tuple of (min_zoom, max_zoom) scales (default: (1.0, 1.2))
- `energy_range`: Tuple of (min_energy, max_energy) for mapping (default: (0.0, 1.0))

#### EnergyBrightness

Adjusts frame brightness based on audio energy level.

```python
from engine.effects import EnergyBrightness

energy_brightness = EnergyBrightness(
    audio_sync=timeline.audio_sync,
    brightness_range=(0.8, 1.2),  # Brightness from 80% to 120%
    energy_range=(0.0, 1.0)
)
```

**Parameters:**
- `audio_sync`: AudioSync object (None for graceful degradation)
- `brightness_range`: Tuple of (min_brightness, max_brightness) multipliers (default: (0.8, 1.2))
- `energy_range`: Tuple of (min_energy, max_energy) for mapping (default: (0.0, 1.0))

#### EnergyShake

Translates the frame based on audio energy, creating a camera shake effect.

```python
from engine.effects import EnergyShake

energy_shake = EnergyShake(
    audio_sync=timeline.audio_sync,
    shake_range=(0.0, 10.0),  # Shake from 0 to 10 pixels
    energy_range=(0.0, 1.0)
)
```

**Parameters:**
- `audio_sync`: AudioSync object (None for graceful degradation)
- `shake_range`: Tuple of (min_shake, max_shake) in pixels (default: (0.0, 10.0))
- `energy_range`: Tuple of (min_energy, max_energy) for mapping (default: (0.0, 1.0))

### Spectral-Driven Effects

These effects respond to the spectral centroid (brightness/tone of audio).

#### SpectralColorShift

Adjusts color temperature based on spectral centroid. Higher centroid = warmer colors, lower centroid = cooler colors.

```python
from engine.effects import SpectralColorShift

color_shift = SpectralColorShift(
    audio_sync=timeline.audio_sync,
    temperature_range=(-0.2, 0.2),    # Cool to warm shift
    centroid_range=(1000.0, 3000.0)   # Map 1000-3000 Hz to temp range
)
```

**Parameters:**
- `audio_sync`: AudioSync object (None for graceful degradation)
- `temperature_range`: Tuple of (cool_shift, warm_shift) in range [-1, 1] (default: (-0.2, 0.2))
- `centroid_range`: Tuple of (min_centroid, max_centroid) in Hz (default: (1000.0, 3000.0))

## Complete Example: Audio-Reactive Video

```python
from pathlib import Path
from api.library import generate_video_from_text
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType, BeatSync
from engine.effects import OnsetFlash, EnergyZoom, brightness, vignette

# Note: Audio-reactive effects need AudioSync from the planner
# This example shows the Scene setup; effects are applied during rendering

scene = Scene(
    clips=[
        ImageClip(
            source="images/photo1.jpg",
            duration=3.0,
            motion=MotionPreset.KEN_BURNS_ZOOM_IN,
            # Note: Audio-reactive effects are added by the renderer
            # after planning, when AudioSync is available
            effects=[
                brightness(0.1),
                vignette(intensity=0.4)
            ]
        ),
        ImageClip(
            source="images/photo2.jpg",
            duration=3.0,
            motion=MotionPreset.PAN_LEFT,
            effects=[brightness(0.05)]
        ),
        ImageClip(
            source="images/photo3.jpg",
            duration=3.0,
            motion=MotionPreset.ZOOM_OUT,
            effects=[vignette(intensity=0.3)]
        ),
    ],
    transitions=[
        Transition(
            type=TransitionType.CROSSFADE,
            duration=0.5,
            sync=BeatSync.NEAREST_BEAT  # Snap to beats
        ),
        Transition(
            type=TransitionType.SLIDE_LEFT,
            duration=0.8,
            sync=BeatSync.BEAT_GRID  # Rhythm-locked
        ),
    ],
    audio="audio/music.mp3",  # Audio file for analysis
    resolution=(1920, 1080),
    fps=30
)

# Generate video with audio-reactive features
text = "Watch as visuals dance to the music."
video_path = generate_video_from_text(
    text=text,
    output_dir=Path("output/audio_reactive"),
    scene=scene
)
```

## Advanced Usage: Manual Audio-Reactive Effects

For advanced users who want direct control over audio-reactive effects:

```python
from engine.scene import Scene, ImageClip
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader
from engine.effects import OnsetFlash, EnergyZoom, EnergyBrightness

# Create scene with audio
scene = Scene(
    clips=[
        ImageClip("image1.jpg", duration=3.0),
        ImageClip("image2.jpg", duration=3.0),
    ],
    audio="audio/music.mp3",
    resolution=(1920, 1080),
    fps=30
)

# Plan scene (this analyzes audio and creates AudioSync)
planner = ScenePlanner()
timeline = planner.plan(scene)

# Now we have timeline.audio_sync available
# Create audio-reactive effects with AudioSync
onset_flash = OnsetFlash(
    audio_sync=timeline.audio_sync,
    flash_duration=0.2,
    intensity=0.6
)

energy_zoom = EnergyZoom(
    audio_sync=timeline.audio_sync,
    zoom_range=(1.0, 1.15),
    energy_range=(0.0, 0.8)
)

# Add effects to clips in timeline
for clip in timeline.clips:
    clip.effects.append(onset_flash)
    clip.effects.append(energy_zoom)

# Render with audio-reactive effects
image_loader = ImageLoader()
renderer = FrameRenderer(timeline, image_loader)

frames = []
total_frames = int(timeline.total_duration * scene.fps)
for frame_idx in range(total_frames):
    t = frame_idx / scene.fps
    frame = renderer.render_frame(t)
    frames.append(frame)

# Export video
from moviepy.editor import ImageSequenceClip, AudioFileClip

video_clip = ImageSequenceClip(frames, fps=scene.fps)
audio_clip = AudioFileClip(str(scene.audio))
final_clip = video_clip.set_audio(audio_clip)
final_clip.write_videofile("output/audio_reactive.mp4", codec='libx264')
```

## Graceful Degradation

Phase 3 is designed to degrade gracefully when audio features are unavailable:

### Without Librosa

If librosa is not installed:
- System logs warning: "Audio analysis disabled: librosa not installed"
- Scene planning continues without audio analysis
- Beat sync uses declared timings
- Audio-reactive effects return frames unchanged

### Without Audio File

If Scene.audio is None or file doesn't exist:
- No audio analysis is performed
- Beat sync uses declared timings
- Audio-reactive effects return frames unchanged

### Effect Behavior

All audio-reactive effects check for None AudioSync:

```python
def apply(self, frame, t, progress):
    if self.audio_sync is None:
        return frame  # No modification
    # ... apply effect
```

This ensures backward compatibility and allows mixing audio-reactive and non-audio-reactive clips.

## Performance

### Audio Analysis

- **10-second audio file**: ~0.5-1.0 seconds to analyze
- **Analysis overhead**: <10% of audio duration
- **Memory usage**: <100MB for typical audio files

### Rendering with Audio Effects

- **Onset effects**: <5ms overhead per frame (only when onset active)
- **Energy effects**: <10ms overhead per frame (continuous)
- **Spectral effects**: <8ms overhead per frame (continuous)
- **Total overhead**: <20% compared to Phase 2 rendering

### Optimization Tips

- Audio analysis happens once during planning (not per-frame)
- AudioSync uses linear interpolation for fast queries
- Effects cache AudioSync reference for efficient access
- Use lower FPS for testing, full FPS for final export

## Troubleshooting

### Librosa Not Found

```
ImportError: librosa is required for audio analysis
```

**Solution**: Install librosa with `pip install librosa`

Or continue without audio features (system will log warning and proceed).

### Audio File Not Found

```
FileNotFoundError: Audio file not found: audio/music.mp3
```

**Solution**: Check audio file path is correct and file exists.

### No Beats Detected

If beat synchronization doesn't work as expected:
- Check audio file has clear rhythmic content
- Try different audio files with stronger beats
- Use BeatSync.NONE to disable beat snapping
- Check logs for warnings about beat detection

### Effects Not Responding to Audio

If audio-reactive effects don't seem to work:
- Verify librosa is installed: `python -c "import librosa; print('OK')"`
- Check Scene.audio is set to valid audio file path
- Verify AudioSync is not None in timeline: `print(timeline.audio_sync)`
- Check effect parameters (energy_range, zoom_range, etc.) are appropriate for your audio

### Beat Sync Creates Invalid Timings

```
Warning: Beat snapping would create negative duration, using declared timing
```

This happens when beat-snapped transitions would overlap or create invalid clip durations.

**Solution**:
- Use longer clip durations
- Use shorter transition durations
- Use BeatSync.NONE for problematic transitions
- Adjust audio file or use different beat detection settings

## Tips and Best Practices

### Beat Synchronization

- **Music videos**: Use BEAT_GRID for rhythm-locked editing
- **Narration with background music**: Use NEAREST_BEAT for subtle sync
- **No music**: Use NONE (default)
- Test with different BeatSync modes to find what works best

### Audio-Reactive Effects

- **Onset effects**: Great for percussive music, speech, dramatic moments
- **Energy effects**: Best for continuous music with varying loudness
- **Spectral effects**: Subtle, works well with tonal music
- **Combine effects**: Use multiple effects together for rich visuals

### Effect Intensity

- Start subtle and increase gradually
- OnsetFlash intensity: 0.3-0.6 for subtle, 0.6-1.0 for dramatic
- EnergyZoom range: (1.0, 1.1) subtle, (1.0, 1.3) dramatic
- EnergyBrightness range: (0.9, 1.1) subtle, (0.7, 1.3) dramatic
- EnergyShake range: (0, 5) subtle, (0, 15) dramatic

### Audio File Selection

- Use high-quality audio files (WAV, FLAC preferred)
- Ensure audio has clear features (beats, onsets, dynamics)
- Match audio duration to video duration
- Test with different audio files to find best results

## What's Next: Phase 4-6 (Planned)

- **Phase 4**: Text overlays and animated typography
- **Phase 5**: Advanced compositing (layers, masks, blend modes)
- **Phase 6**: 3D transforms and perspective effects

## Reference

- **Phase 1 Implementation**: `.kiro/specs/video-engine-phase-1/`
- **Phase 2 Implementation**: `.kiro/specs/video-engine-phase-2/`
- **Phase 3 Implementation**: `.kiro/specs/video-engine-phase-3/`
- **Test Examples**: `tests/test_phase3_integration.py`
- **Audio Analysis**: `engine/audio/analyzer.py`
- **Audio Sync**: `engine/audio/sync.py`
- **Audio-Reactive Effects**: `engine/effects.py` (Phase 3 section)

## Support

For issues or questions:
1. Check test files for working examples
2. Review `.kiro/specs/video-engine-phase-3/design.md` for technical details
3. Examine integration tests for usage patterns
4. Check logs for warnings about audio analysis or beat sync

