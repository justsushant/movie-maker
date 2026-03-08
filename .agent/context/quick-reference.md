---
inclusion: always
---

# Quick Reference

## Common Commands

### Setup and Installation

```bash
# Setup development environment
make setup

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Running the Pipeline

```bash
# Generate video from files/input.txt
make run

# Output: output/run_YYYYMMDD_HHMMSS/
```

### Testing

```bash
# Run all tests
make test

# Run unit tests only (fast)
make test-unit

# Run integration tests (slower)
make test-integration

# Run stress tests
make test-stress

# Run specific test file
pytest tests/test_renderer.py -v

# Run specific test with output
pytest tests/test_renderer.py::test_render_frame -v -s

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html
```

### Cleanup

```bash
# Clean output directory
make clean

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

## Key File Locations

### Core Modules

| File/Directory | Purpose |
|----------------|---------|
| `main.py` | CLI entry point |
| `api/` | Programmatic API |
| `config.py` | Configuration management |
| `engine/` | Video engine (motion, transitions, effects) |
| `subtitle/` | Subtitle system |
| `tts/` | Text-to-speech |
| `pipeline/` | Pipeline orchestration |
| `processing/` | Text processing |
| `rendering/` | Video composition |

### Tests

| Directory | Purpose |
|-----------|---------|
| `tests/` | All test files |
| `tests/fixtures/` | Test fixtures (text, images, audio) |
| `tests/test_output/` | Test output directory |

### Documentation

| File | Purpose |
|------|---------|
| `docs/README.md` | Documentation index |
| `docs/getting_started.md` | Installation and first steps |
| `docs/video_engine.md` | Video engine documentation |
| `docs/subtitles.md` | Subtitle configuration |
| `docs/architecture.md` | System architecture |
| `docs/how_it_works.md` | Pipeline walkthrough |

### Configuration

| File | Purpose |
|------|---------|
| `config.py` | Configuration classes |
| `requirements.txt` | Python dependencies |
| `Makefile` | Build commands |

### Context Files (For AI Agents)

| File | Purpose |
|------|---------|
| `.kiro/steering/product.md` | Product overview |
| `.kiro/steering/structure.md` | Project structure |
| `.kiro/steering/tech.md` | Tech stack |
| `.kiro/steering/agents.md` | Agent guidelines |
| `.kiro/steering/development-workflow.md` | Development workflows |
| `.kiro/steering/quick-reference.md` | This file |
| `.opencoderules` | Project context rules |

## Key Classes and Functions

### Video Engine

```python
# Scene DSL
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType

# Create a scene
scene = Scene(
    clips=[...],
    transitions=[...],
    fps=30,
    width=1920,
    height=1080
)

# Create an image clip
clip = ImageClip(
    path="path/to/image.jpg",
    duration=5.0,
    motion=MotionPreset.KEN_BURNS,
    effects=[...]
)

# Motion presets
MotionPreset.KEN_BURNS    # Zoom and pan
MotionPreset.PAN_LEFT     # Pan left
MotionPreset.PAN_RIGHT    # Pan right
MotionPreset.PAN_UP       # Pan up
MotionPreset.PAN_DOWN     # Pan down
MotionPreset.ZOOM_IN      # Zoom in
MotionPreset.ZOOM_OUT     # Zoom out
MotionPreset.ZOOM_IN_LEFT # Zoom in while panning left
MotionPreset.ZOOM_IN_RIGHT # Zoom in while panning right
```

### Effects

```python
from engine.effects import (
    # Color effects
    brightness,
    contrast,
    saturation,
    # Cinematic effects
    vignette,
    film_grain,
    # Audio-reactive effects (Phase 3)
    OnsetFlash,
    OnsetZoomPulse,
    EnergyZoom,
    EnergyBrightness,
    EnergyShake,
    SpectralColorShift
)

# Simple effect (function)
def custom_effect(frame, t, progress):
    return frame  # Your logic here

# Audio-reactive effect (class)
class CustomAudioEffect:
    def __init__(self, audio_sync: AudioSync):
        self.audio_sync = audio_sync
        self.intensity = 0.5

    def __call__(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Your logic here
        return frame
```

### Transitions

```python
from engine.transitions import TransitionType

# Blend transitions
TransitionType.CROSSFADE
TransitionType.FADE_THROUGH_BLACK
TransitionType.FADE_THROUGH_WHITE
TransitionType.FADE_THROUGH_COLOR

# Geometric transitions
TransitionType.SLIDE_LEFT
TransitionType.SLIDE_RIGHT
TransitionType.SLIDE_UP
TransitionType.SLIDE_DOWN
TransitionType.PUSH_LEFT
TransitionType.PUSH_RIGHT
TransitionType.PUSH_UP
TransitionType.PUSH_DOWN
TransitionType.WIPE_LEFT
TransitionType.WIPE_RIGHT
TransitionType.WIPE_UP
TransitionType.WIPE_DOWN

# Shape transitions
TransitionType.IRIS_IN
TransitionType.IRIS_OUT
TransitionType.CLOCK_WIPE
TransitionType.DIAMOND_WIPE
TransitionType.BLINDS

# Animated transitions
TransitionType.ZOOM_THROUGH
TransitionType.WHIP_PAN
TransitionType.PIXELATE
TransitionType.GLITCH
```

### Subtitle System

```python
from subtitle.composer import SubtitleFrameComposer
from subtitle.source import JsonSubtitleSource
from subtitle.layouts import (
    SentenceLayout,
    WordOnlyLayout,
    WordHighlightLayout,
    StackingLayout
)
from subtitle.renderer import PillowSubtitleRenderer

# Create subtitle composer
composer = SubtitleFrameComposer(
    source=JsonSubtitleSource("path/to/subtitle.json"),
    layout=WordHighlightLayout(config),
    renderer=PillowSubtitleRenderer(config)
)

# Render subtitle on frame
frame_with_subtitle = composer.render_subtitle(frame, timestamp)
```

### TTS

```python
from tts.kokoro_tts import KokoroTTSEngine, TTSConfig
from pipeline.ttspipeline import TTSPipeline

# Create TTS engine
tts_engine = KokoroTTSEngine(TTSConfig())

# Generate audio
audio, word_timestamps = tts_engine.generate("Your text here")
```

### Configuration

```python
from config import get_config, get_test_config

# Get default configuration
config = get_config()

# Get test configuration
test_config = get_test_config()

# Key config attributes
config.fps              # Frames per second
config.width            # Frame width
config.height           # Frame height
config.output_dir       # Output directory
config.subtitle_config  # Subtitle configuration
```

## Common Patterns

### Creating a Simple Video

```python
from engine.scene import Scene, ImageClip, MotionPreset
from config import get_config

config = get_config()

scene = Scene(
    clips=[
        ImageClip(path="image1.jpg", duration=5.0, motion=MotionPreset.KEN_BURNS),
        ImageClip(path="image2.jpg", duration=5.0, motion=MotionPreset.ZOOM_IN),
    ],
    fps=config.fps,
    width=config.width,
    height=config.height
)
```

### Adding Effects to a Clip

```python
from engine.scene import ImageClip
from engine.effects import brightness, contrast, vignette

clip = ImageClip(
    path="image.jpg",
    duration=5.0,
    motion=MotionPreset.PAN_LEFT,
    effects=[
        lambda f, t, p: brightness(f, t, p, factor=1.2),
        lambda f, t, p: contrast(f, t, p, factor=1.1),
        lambda f, t, p: vignette(f, t, p, intensity=0.3),
    ]
)
```

### Creating a Transition

```python
from engine.scene import Transition, TransitionType

transition = Transition(
    type=TransitionType.CROSSFADE,
    duration=1.0
)

# Beat-synchronized transition (Phase 3)
beat_sync = Transition(
    type=TransitionType.CROSSFADE,
    duration=1.0,
    beat_sync=BeatSync.NEAREST_BEAT  # or BEAT_GRID
)
```

### Running the Full Pipeline

```python
from api.library import generate_video_from_text

# Generate video from text
generate_video_from_text(
    text="Your narration here",
    image_paths=["image1.jpg", "image2.jpg"],
    output_dir="output"
)
```

## Frame Format

- **Shape**: `(height, width, 3)`
- **Data Type**: `uint8`
- **Color Space**: RGB (not BGR!)
- **Example**: `np.zeros((1080, 1920, 3), dtype=np.uint8)`

## Testing Patterns

### Unit Test Example

```python
import pytest
import numpy as np
from engine.effects import brightness

def test_brightness():
    frame = np.ones((100, 100, 3), dtype=np.uint8) * 100
    result = brightness(frame, t=0.0, progress=0.5, factor=1.5)
    assert result.shape == frame.shape
    assert result.dtype == np.uint8
```

### Integration Test Example

```python
from engine.scene import Scene, ImageClip, MotionPreset
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer

def test_scene_rendering():
    scene = Scene(
        clips=[
            ImageClip(path="test.jpg", duration=2.0, motion=MotionPreset.KEN_BURNS),
        ],
        fps=30,
        width=1920,
        height=1080
    )
    planner = ScenePlanner()
    timeline = planner.plan(scene)
    renderer = FrameRenderer(timeline)
    frame = renderer.render_frame(0.5)
    assert frame.shape == (1080, 1920, 3)
```

## Troubleshooting

### Frame Color Issues

If colors look wrong, check if you're converting between BGR and RGB:
```python
# Convert BGR to RGB
frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
```

### Memory Issues

If running out of memory:
- Reduce resolution
- Check for memory leaks
- Process in smaller chunks

### TTS Issues

If TTS isn't working:
- Check Kokoro installation
- Verify model files are available
- Test with simple text

## Important Notes

- **Always** use RGB color space for frames
- **Never** commit secrets or credentials
- **Always** write tests for new code
- **Always** run `make test` before submitting changes
- **Always** update documentation when adding features
- **Never** make breaking changes without good reason
- **Always** follow SOLID principles
- **Always** use type hints

## Performance Benchmarks

From `docs/performance_benchmarks.md`:

- 1080p rendering: ~2-3ms per frame (no effects)
- With effects: ~5-10ms per effect
- Transitions: Blend <50ms, Geometric <100ms, Animated <150ms
- Audio analysis: ~0.5-1.0s for 10-second audio
- 10-second video: ~1-2 seconds to render + encoding time

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| kokoro | ≥0.9.4 | Text-to-speech |
| moviepy | latest | Video composition |
| pillow | latest | Image processing |
| numpy | latest | Array operations |
| opencv-python | latest | Image transforms |
| scipy | latest | Signal processing |
| librosa | optional | Audio analysis |
| pytest | latest | Testing |
| hypothesis | latest | Property-based testing |
