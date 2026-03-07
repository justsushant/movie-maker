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
