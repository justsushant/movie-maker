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

## Duration Alignment (Scene vs Narration)

When combining a Scene with TTS narration via `generate_video_from_text()`, the
final video duration is `max(audio_duration, timeline_duration)`:

- **Scene shorter than narration** — the last frame is held as a freeze-frame
  until the narration finishes.  This looks unintentional.
- **Scene longer than narration** — the video continues with visuals after the
  speech ends.  This can work as a deliberate outro.

To avoid mismatches, size the scene so its effective timeline covers the
narration:

```
effective_duration = sum(clip.duration for clip in clips)
                   - sum(t.duration for t in transitions)
```

A practical approach: estimate narration length (~140 words per minute for
natural speech), then set clip durations so the effective duration is slightly
longer than the estimate.

```python
word_count = len(narration.split())
estimated_seconds = word_count / 140 * 60  # ~2.3 words/second
num_clips = 7
clip_duration = (estimated_seconds + 5) / num_clips  # small buffer
```

There is currently no automatic duration-stretch.  If you need exact alignment,
run TTS first (via `TTSPipeline`), measure the output audio length, then build
the Scene to match before calling `create_video()`.  See
`examples/engagement_benchmark.py` for a working pattern.

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



---

# Phase 4 Video Engine - Rich Visual Effects Library

## Overview

Phase 4 expands the effects library with **56+ professional visual effects** organized into four categories: color manipulation, blur and focus, texture overlays, and stylization. These effects enable everything from subtle color grading to dramatic artistic transformations.

## What's New in Phase 4

- **21 Color Effects**: Grayscale, sepia, hue shift, color temperature, tinting, gamma correction, and more
- **11 Blur Effects**: Box blur, Gaussian blur, motion blur, radial blur, tilt-shift, depth of field, and more
- **12 Texture Effects**: Scan lines, letterbox, vignette, gradients, watermarks, borders, light leaks, and more
- **12 Stylization Effects**: Edge detection, sketch, oil painting, emboss, chromatic aberration, glitch effects, and more
- **Text Overlay**: Add text labels, titles, and captions with customizable styling

All Phase 4 effects follow the same simple API pattern and can be chained together for complex looks.

## Effect Categories

### Category 1: Color Effects (21 effects)

Transform colors, adjust tones, and create color grades.

#### Basic Color Adjustments

```python
from engine.effects import grayscale, invert, sepia

# Convert to grayscale
grayscale()

# Invert all colors
invert()

# Apply sepia tone (vintage brown)
sepia()
```

#### Color Manipulation

```python
from engine.effects import hue_shift, color_temperature, tint, gamma_correction

# Shift hue around color wheel
hue_shift(shift=30.0)  # -180 to 180 degrees

# Adjust color temperature
color_temperature(kelvin=5000.0)  # <5000: warm, >6500: cool

# Apply color tint overlay
tint(color=(255, 200, 150), alpha=0.3)  # Warm tint

# Gamma correction (non-linear brightness)
gamma_correction(gamma=1.2)  # >1.0: darken, <1.0: brighten
```

#### Advanced Color Grading

```python
from engine.effects import (
    channel_mixer, duotone, cinematic_teal_orange,
    auto_white_balance, vibrance
)

# Cross-blend RGB channels
channel_mixer(
    red=(1.0, 0.0, 0.0),    # Red output from RGB inputs
    green=(0.0, 1.0, 0.0),  # Green output
    blue=(0.0, 0.0, 1.0)    # Blue output
)

# Two-color gradient mapping
duotone(
    dark_color=(20, 30, 50),      # Dark blue for shadows
    light_color=(255, 220, 180)   # Warm for highlights
)

# Cinematic teal-orange look
cinematic_teal_orange(intensity=1.0)  # 0.0 to 1.0

# Automatic white balance
auto_white_balance()

# Boost low-saturation colors
vibrance(amount=1.0)  # 0.0 to 2.0
```

#### Special Color Effects

```python
from engine.effects import (
    color_pulse, fade_to_color, thermal,
    posterize, solarize
)

# Pulsing color effect
color_pulse(
    frequency=2.0,           # Pulses per second
    color=(255, 100, 100),   # Red pulse
    amount=0.5               # Intensity
)

# Fade to color over time (progress-driven)
fade_to_color(color=(0, 0, 0))  # Fade to black

# Thermal/infrared false-color
thermal()

# Reduce color levels (posterization)
posterize(bits=4)  # 1 to 8 bits per channel

# Invert bright pixels (solarization)
solarize(threshold=128)  # 0 to 255
```

#### Custom Color Curves

```python
from engine.effects import curves_lut, tricolor, bleach_bypass, cross_process
import numpy as np

# Custom curves using lookup tables
lut_r = np.linspace(0, 255, 256).astype(np.uint8)  # Linear
lut_g = np.linspace(0, 255, 256).astype(np.uint8)
lut_b = np.linspace(0, 255, 256).astype(np.uint8)
curves_lut(lut_r=lut_r, lut_g=lut_g, lut_b=lut_b)

# Three-color gradient map
tricolor(
    color1=(20, 30, 50),      # Shadows
    color2=(150, 120, 100),   # Midtones
    color3=(255, 220, 180)    # Highlights
)

# Film processing effects
bleach_bypass()  # Desaturated, high-contrast
cross_process()  # Per-channel S-curve
```

### Category 2: Blur Effects (11 effects)

Control focus, create depth, and add motion blur.

#### Basic Blur

```python
from engine.effects import box_blur, gaussian_blur

# Uniform blur
box_blur(kernel_size=5)  # Odd number

# Gaussian blur (smoother)
gaussian_blur(kernel_size=5, sigma=0)  # sigma=0: auto
```

#### Directional Blur

```python
from engine.effects import motion_blur, radial_blur

# Motion blur (simulates camera movement)
motion_blur(angle=0, amount=15)  # angle: 0=horizontal

# Radial blur (from center)
radial_blur(amount=10)
```

#### Sharpening and Pixelation

```python
from engine.effects import sharpen, pixelate

# Sharpen using unsharp mask
sharpen(amount=1.0)

# Pixelation/mosaic effect
pixelate(block_size=8)
```

#### Advanced Blur

```python
from engine.effects import (
    bilateral_blur, tilt_shift, depth_of_field,
    zoom_blur, animated_blur
)

# Edge-preserving smoothing
bilateral_blur(d=9, sigma_color=75, sigma_space=75)

# Tilt-shift/miniature effect
tilt_shift(
    blur_amount=15,
    gradient_start=0.3,  # Sharp region start
    gradient_end=0.7     # Sharp region end
)

# Depth of field (simulates lens focus)
depth_of_field(
    focus_distance=0.5,  # 0.0 to 1.0
    aperture=5.0         # Larger = more blur
)

# Zoom blur effect
zoom_blur(strength=0.5)  # 0.0 to 1.0

# Animated blur (changes over time)
animated_blur(min_kernel=3, max_kernel=15)
```

### Category 3: Texture Effects (12 effects)

Add overlays, borders, and texture elements.

#### Screen Effects

```python
from engine.effects import scan_lines, letterbox, vignette_simple

# CRT scan lines
scan_lines(spacing=2, intensity=0.5)  # Every 2nd row

# Cinematic letterbox bars
letterbox(top=100, bottom=100, color=(0, 0, 0))

# Simple vignette (darken edges)
vignette_simple(intensity=0.5)  # 0.0 to 1.0
```

#### Overlays

```python
from engine.effects import (
    gradient_overlay, image_watermark, pattern_overlay
)

# Gradient overlay
gradient_overlay(
    color_start=(255, 0, 0),
    color_end=(0, 0, 255),
    direction="vertical",  # or "horizontal"
    alpha=0.3
)

# Image watermark
import numpy as np
watermark = np.zeros((100, 100, 4), dtype=np.uint8)  # RGBA
image_watermark(
    watermark_img=watermark,
    position="bottom-right",  # or "top-left", "center", etc.
    opacity=0.7,
    scale=0.1  # Relative to frame size
)

# Repeating pattern overlay
pattern = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
pattern_overlay(pattern=pattern, opacity=0.2)
```

#### Borders and Frames

```python
from engine.effects import border, progress_bar

# Border/frame effect
border(thickness=10, color=(255, 255, 255))

# Progress bar overlay
progress_bar(
    position="bottom",  # or "top"
    height=5,
    color=(255, 0, 0)
)
```

#### Artistic Overlays

```python
from engine.effects import (
    light_leak, bokeh_overlay, dust_scratches, lens_flare
)

# Light leak (colorful glow at edges)
light_leak(intensity=0.3)  # 0.0 to 1.0

# Bokeh circles overlay
bokeh_overlay(num_circles=20, max_radius=50)

# Dust and scratches
dust_scratches(density=0.001)  # 0.0 to 1.0

# Lens flare effect
lens_flare(x=None, y=None)  # None = center
```

### Category 4: Stylization Effects (12 effects)

Transform images into artistic styles.

#### Edge and Sketch Effects

```python
from engine.effects import edge_detection, sketch, emboss

# Canny edge detection
edge_detection(threshold1=100, threshold2=200)

# Pencil sketch effect
sketch()

# Emboss effect
emboss()
```

#### Artistic Styles

```python
from engine.effects import oil_painting, dithering, halftone

# Oil painting effect
oil_painting()

# Floyd-Steinberg dithering
dithering()

# Halftone effect
halftone(dot_size=4)
```

#### Glitch Effects

```python
from engine.effects import (
    chromatic_aberration, glitch_rgb_split,
    glitch_block_displacement, glitch_scan_line_shift,
    glitch_color_corruption
)

# Chromatic aberration (RGB channel offset)
chromatic_aberration(amount=3)  # Pixels

# RGB split with random offsets
glitch_rgb_split(max_offset=20)

# Block displacement glitch
glitch_block_displacement(block_size=20, displacement=10)

# Scan line shift glitch
glitch_scan_line_shift(intensity=0.5)  # 0.0 to 1.0

# Color corruption glitch
glitch_color_corruption(intensity=0.3)  # 0.0 to 1.0
```

#### Retro Effects

```python
from engine.effects import (
    threshold_bw, crt_retro, vhs_tape_distortion
)

# High contrast black and white
threshold_bw(threshold=128)  # 0 to 255

# CRT retro effect (scan lines + RGB blur)
crt_retro(scanline_intensity=0.1)  # 0.0 to 1.0

# VHS tape distortion
vhs_tape_distortion(intensity=0.3)  # 0.0 to 1.0
```

### Text Overlay

Add text labels, titles, and captions to your videos.

```python
from engine.effects import text_overlay

# Simple text overlay
text_overlay(
    text="My Video Title",
    position=(50, 50),           # Top-left corner
    font_scale=1.0,              # 0.5 to 3.0
    color=(255, 255, 255),       # White text
    thickness=2,                 # 1 to 5
    bg_color=(0, 0, 0),          # Black background
    bg_opacity=0.7,              # 0.0 to 1.0
    padding=10                   # Pixels
)

# Text without background
text_overlay(
    text="No Background",
    position=(100, 100),
    bg_color=None  # No background
)
```

## Usage Examples

### Example 1: Cinematic Color Grade

```python
from engine.scene import Scene, ImageClip, MotionPreset
from engine.effects import (
    cinematic_teal_orange, vignette_simple,
    film_grain, letterbox
)

clip = ImageClip(
    source="image.jpg",
    duration=5.0,
    motion=MotionPreset.KEN_BURNS_ZOOM_IN,
    effects=[
        cinematic_teal_orange(intensity=0.8),
        vignette_simple(intensity=0.4),
        film_grain(intensity=0.05),
        letterbox(top=80, bottom=80, color=(0, 0, 0))
    ]
)
```

### Example 2: Vintage Film Look

```python
from engine.effects import (
    sepia, dust_scratches, scan_lines, vignette_simple
)

clip = ImageClip(
    source="image.jpg",
    duration=5.0,
    effects=[
        sepia(),
        dust_scratches(density=0.002),
        scan_lines(spacing=3, intensity=0.3),
        vignette_simple(intensity=0.6)
    ]
)
```

### Example 3: Glitch Art

```python
from engine.effects import (
    glitch_rgb_split, glitch_block_displacement,
    chromatic_aberration, glitch_color_corruption
)

clip = ImageClip(
    source="image.jpg",
    duration=3.0,
    effects=[
        glitch_rgb_split(max_offset=15),
        glitch_block_displacement(block_size=30, displacement=20),
        chromatic_aberration(amount=5),
        glitch_color_corruption(intensity=0.2)
    ]
)
```

### Example 4: Dreamy Soft Focus

```python
from engine.effects import (
    gaussian_blur, light_leak, bokeh_overlay,
    color_temperature, vibrance
)

clip = ImageClip(
    source="image.jpg",
    duration=5.0,
    effects=[
        gaussian_blur(kernel_size=7, sigma=2),
        light_leak(intensity=0.4),
        bokeh_overlay(num_circles=15, max_radius=40),
        color_temperature(kelvin=7000.0),  # Cool
        vibrance(amount=1.3)
    ]
)
```

### Example 5: Dramatic Black and White

```python
from engine.effects import (
    grayscale, contrast, vignette_simple,
    sharpen, film_grain
)

clip = ImageClip(
    source="image.jpg",
    duration=5.0,
    effects=[
        grayscale(),
        contrast(1.4),
        vignette_simple(intensity=0.5),
        sharpen(amount=1.2),
        film_grain(intensity=0.08)
    ]
)
```

### Example 6: Tilt-Shift Miniature

```python
from engine.effects import (
    tilt_shift, saturation, contrast
)

clip = ImageClip(
    source="image.jpg",
    duration=5.0,
    motion=MotionPreset.PAN_LEFT,
    effects=[
        tilt_shift(blur_amount=20, gradient_start=0.35, gradient_end=0.65),
        saturation(1.4),  # Boost saturation
        contrast(1.2)
    ]
)
```

### Example 7: Retro VHS Look

```python
from engine.effects import (
    vhs_tape_distortion, crt_retro, scan_lines,
    color_temperature, film_grain
)

clip = ImageClip(
    source="image.jpg",
    duration=5.0,
    effects=[
        vhs_tape_distortion(intensity=0.4),
        crt_retro(scanline_intensity=0.15),
        scan_lines(spacing=2, intensity=0.4),
        color_temperature(kelvin=5500.0),
        film_grain(intensity=0.1)
    ]
)
```

### Example 8: Text Labels for Demo Videos

```python
from engine.effects import text_overlay, grayscale

# Label each effect in a demo video
clip1 = ImageClip(
    source="image.jpg",
    duration=3.0,
    effects=[
        grayscale(),
        text_overlay("Grayscale Effect", position=(50, 50))
    ]
)

clip2 = ImageClip(
    source="image.jpg",
    duration=3.0,
    effects=[
        sepia(),
        text_overlay("Sepia Tone", position=(50, 50))
    ]
)
```

## Effect Chaining and Composition

All Phase 4 effects can be chained together. Effects are applied in order:

```python
from engine.effects import (
    brightness, contrast, saturation,
    vignette_simple, film_grain, text_overlay
)

# Complex effect chain
clip = ImageClip(
    source="image.jpg",
    duration=5.0,
    effects=[
        # 1. Color adjustments
        brightness(0.1),
        contrast(1.2),
        saturation(1.1),
        
        # 2. Texture effects
        vignette_simple(intensity=0.4),
        film_grain(intensity=0.05),
        
        # 3. Text overlay (always last)
        text_overlay("My Title", position=(50, 50))
    ]
)
```

**Best Practice**: Apply effects in this order:
1. Color adjustments (brightness, contrast, saturation)
2. Color grading (cinematic looks, tints)
3. Blur/focus effects
4. Texture overlays (vignette, grain, light leaks)
5. Stylization (glitch, artistic effects)
6. Text overlays (always last)

## Performance Considerations

### Effect Performance at 1080p

| Effect Category | Typical Performance | Notes |
|----------------|---------------------|-------|
| Color Effects | 2-5ms per frame | Fast, mostly pixel operations |
| Simple Blur | 5-15ms per frame | Depends on kernel size |
| Advanced Blur | 15-50ms per frame | Bilateral, tilt-shift are slower |
| Texture Overlays | 3-10ms per frame | Fast, simple blending |
| Stylization | 10-30ms per frame | Edge detection, oil painting slower |
| Glitch Effects | 5-15ms per frame | Random operations add variance |
| Text Overlay | 2-5ms per frame | Fast, OpenCV rendering |

### Optimization Tips

1. **Test at lower resolution**: Use 720p or 480p for testing, 1080p for final export
2. **Reduce kernel sizes**: Smaller blur kernels = faster rendering
3. **Limit effect chains**: Each effect adds overhead; use 3-5 effects per clip
4. **Use simpler effects**: Gaussian blur is faster than bilateral blur
5. **Profile your pipeline**: Use `test_performance.py` to benchmark

### Memory Usage

- Most effects process frames in-place: minimal memory overhead
- Image watermarks and patterns are cached: one-time memory cost
- Large blur kernels may require temporary buffers
- Typical memory usage: <500MB for 1080p rendering

## Tips and Best Practices

### Color Grading

- Start with subtle adjustments (±0.1 brightness, 1.1-1.3 contrast)
- Use `cinematic_teal_orange()` for instant professional look
- Combine `vibrance()` with `saturation()` for natural color boost
- Use `auto_white_balance()` before other color adjustments

### Blur Effects

- Gaussian blur is smoother than box blur
- Use bilateral blur to preserve edges while smoothing
- Tilt-shift works best on aerial/elevated shots
- Motion blur angle: 0=horizontal, 90=vertical, 45=diagonal

### Texture Effects

- Vignette intensity: 0.3-0.5 for subtle, 0.6-0.8 for dramatic
- Film grain: 0.05-0.1 for subtle texture
- Light leaks: 0.2-0.4 intensity for natural look
- Letterbox: 80-120 pixels for cinematic 2.39:1 look

### Stylization

- Glitch effects work best with short durations (1-2 seconds)
- Combine multiple glitch effects for complex distortion
- Use `threshold_bw()` for high-contrast graphic look
- Oil painting and sketch effects remove fine detail

### Text Overlays

- Use semi-transparent backgrounds for readability
- Position text away from edges (50+ pixels margin)
- Font scale: 1.0 for body text, 1.5-2.0 for titles
- White text on dark background is most readable

## Complete Phase 4 Effects Reference

### Color Effects (21)

| Effect | Parameters | Description |
|--------|-----------|-------------|
| `grayscale()` | None | Convert to grayscale |
| `invert()` | None | Invert all colors |
| `sepia()` | None | Sepia tone (vintage brown) |
| `hue_shift(shift)` | shift: -180 to 180 | Rotate hue around color wheel |
| `color_temperature(kelvin)` | kelvin: 2000-10000 | Adjust warm/cool temperature |
| `tint(color, alpha)` | color: RGB, alpha: 0-1 | Color overlay tint |
| `gamma_correction(gamma)` | gamma: 0.5-2.0 | Non-linear brightness |
| `channel_mixer(r, g, b)` | r/g/b: RGB weights | Cross-blend RGB channels |
| `duotone(dark, light)` | dark/light: RGB | Two-color gradient map |
| `cinematic_teal_orange(intensity)` | intensity: 0-1 | Teal shadows, orange highlights |
| `auto_white_balance()` | None | Gray-world white balance |
| `vibrance(amount)` | amount: 0-2 | Boost low-saturation colors |
| `color_pulse(freq, color, amt)` | freq: Hz, color: RGB, amt: 0-1 | Pulsing color effect |
| `fade_to_color(color)` | color: RGB | Fade to color (progress-driven) |
| `thermal()` | None | Thermal/infrared false-color |
| `posterize(bits)` | bits: 1-8 | Reduce color levels |
| `solarize(threshold)` | threshold: 0-255 | Invert bright pixels |
| `curves_lut(r, g, b)` | r/g/b: 256-value LUTs | Custom color curves |
| `tricolor(c1, c2, c3)` | c1/c2/c3: RGB | Three-color gradient map |
| `bleach_bypass()` | None | Desaturated film look |
| `cross_process()` | None | Per-channel S-curve |

### Blur Effects (11)

| Effect | Parameters | Description |
|--------|-----------|-------------|
| `box_blur(kernel_size)` | kernel_size: odd int | Uniform blur |
| `gaussian_blur(kernel, sigma)` | kernel: odd int, sigma: float | Smooth Gaussian blur |
| `motion_blur(angle, amount)` | angle: degrees, amount: int | Directional motion blur |
| `radial_blur(amount)` | amount: int | Radial blur from center |
| `pixelate(block_size)` | block_size: int | Pixelation/mosaic |
| `sharpen(amount)` | amount: float | Unsharp mask sharpening |
| `bilateral_blur(d, sc, ss)` | d: int, sc/ss: float | Edge-preserving blur |
| `tilt_shift(blur, start, end)` | blur: int, start/end: 0-1 | Miniature effect |
| `depth_of_field(focus, aperture)` | focus: 0-1, aperture: float | Lens focus simulation |
| `zoom_blur(strength)` | strength: 0-1 | Zoom blur effect |
| `animated_blur(min, max)` | min/max: int | Time-varying blur |

### Texture Effects (12)

| Effect | Parameters | Description |
|--------|-----------|-------------|
| `scan_lines(spacing, intensity)` | spacing: int, intensity: 0-1 | CRT scan lines |
| `letterbox(top, bottom, color)` | top/bottom: pixels, color: RGB | Cinematic bars |
| `vignette_simple(intensity)` | intensity: 0-1 | Darken edges |
| `gradient_overlay(start, end, dir, alpha)` | start/end: RGB, dir: str, alpha: 0-1 | Gradient overlay |
| `image_watermark(img, pos, opacity, scale)` | img: array, pos: str, opacity: 0-1, scale: float | Image watermark |
| `border(thickness, color)` | thickness: pixels, color: RGB | Border/frame |
| `pattern_overlay(pattern, opacity)` | pattern: array, opacity: 0-1 | Repeating pattern |
| `light_leak(intensity)` | intensity: 0-1 | Colorful edge glow |
| `bokeh_overlay(num, radius)` | num: int, radius: int | Blurred circles |
| `dust_scratches(density)` | density: 0-1 | Dust and scratches |
| `lens_flare(x, y)` | x/y: pixels or None | Lens flare effect |
| `progress_bar(pos, height, color)` | pos: str, height: pixels, color: RGB | Progress bar overlay |

### Stylization Effects (12)

| Effect | Parameters | Description |
|--------|-----------|-------------|
| `edge_detection(t1, t2)` | t1/t2: int | Canny edge detection |
| `sketch()` | None | Pencil sketch effect |
| `oil_painting()` | None | Oil painting style |
| `emboss()` | None | Emboss effect |
| `chromatic_aberration(amount)` | amount: pixels | RGB channel offset |
| `glitch_rgb_split(max_offset)` | max_offset: pixels | Random RGB split |
| `glitch_block_displacement(size, disp)` | size/disp: pixels | Block displacement |
| `threshold_bw(threshold)` | threshold: 0-255 | High contrast B&W |
| `dithering()` | None | Floyd-Steinberg dithering |
| `halftone(dot_size)` | dot_size: pixels | Halftone effect |
| `glitch_scan_line_shift(intensity)` | intensity: 0-1 | Scan line shift glitch |
| `glitch_color_corruption(intensity)` | intensity: 0-1 | Color corruption glitch |
| `crt_retro(scanline_intensity)` | scanline_intensity: 0-1 | CRT retro effect |
| `vhs_tape_distortion(intensity)` | intensity: 0-1 | VHS distortion |

### Text Overlay (1)

| Effect | Parameters | Description |
|--------|-----------|-------------|
| `text_overlay(text, pos, scale, color, thickness, bg_color, bg_opacity, padding)` | text: str, pos: (x,y), scale: 0.5-3, color: RGB, thickness: 1-5, bg_color: RGB or None, bg_opacity: 0-1, padding: pixels | Add text with optional background |

## Troubleshooting

### Effect Not Visible

If an effect doesn't seem to work:
- Check parameter ranges (e.g., intensity should be 0.0-1.0, not 0-100)
- Verify effect is in the effects list
- Try increasing effect intensity
- Check if effect is being overridden by later effects

### Performance Issues

If rendering is slow:
- Reduce resolution for testing
- Use smaller blur kernel sizes
- Limit number of effects per clip (3-5 recommended)
- Profile with `test_performance.py`

### Memory Errors

If running out of memory:
- Reduce video resolution
- Shorten clip durations
- Remove memory-intensive effects (large blurs, oil painting)
- Process video in segments

### Color Space Issues

If colors look wrong:
- Ensure images are RGB (not BGR)
- Check if effect expects specific color range
- Verify input images are valid

## What's Next: Phase 5-6 (Planned)

- **Phase 5**: Advanced compositing (layers, masks, blend modes, alpha channels)
- **Phase 6**: 3D transforms and perspective effects (rotation, skew, perspective)

## Reference

- **Phase 4 Implementation**: `.kiro/specs/video-engine-phase4-verification/`
- **Effect Source Code**: `engine/effects.py`
- **Test Examples**: `tests/test_phase4_effects_unit.py`
- **Demo Scripts**: `examples/demo_phase4_rich_effects.py`
- **Showcase Examples**: `examples/PHASE4_SHOWCASE.md`

## Support

For issues or questions:
1. Check example scripts in `examples/` directory
2. Review test files for working examples
3. Examine `engine/effects.py` for implementation details
4. Check `.kiro/specs/video-engine-phase4-verification/design.md` for technical details
