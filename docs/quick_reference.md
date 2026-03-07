# Quick Start - Phase 2 Video Engine

## 30-Second Setup

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run demo
python demo_phase2_showcase.py
```

## Minimal Example

```python
from pathlib import Path
from api.library import generate_video_from_text
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType

# Create scene
scene = Scene(
    clips=[
        ImageClip("image1.jpg", duration=3.0, motion=MotionPreset.ZOOM_IN),
        ImageClip("image2.jpg", duration=3.0, motion=MotionPreset.PAN_LEFT),
    ],
    transitions=[
        Transition(type=TransitionType.CROSSFADE, duration=0.5)
    ],
    resolution=(1920, 1080),
    fps=30
)

# Generate video
video_path = generate_video_from_text(
    text="Your narration here.",
    output_dir=Path("output/my_video"),
    scene=scene
)
```

## What You Need

1. **Images**: Any JPEG/PNG files
2. **Text**: Narration script (optional)
3. **Python**: Virtual environment activated

## Available Features

### Motion (Phase 1)
- `STATIC`, `ZOOM_IN`, `ZOOM_OUT`
- `PAN_LEFT`, `PAN_RIGHT`, `PAN_UP`, `PAN_DOWN`
- `KEN_BURNS_ZOOM_IN`, `KEN_BURNS_ZOOM_OUT`

### Transitions (Phase 2)
- **Blend**: `CROSSFADE`, `FADE_THROUGH_BLACK`, `FADE_THROUGH_WHITE`
- **Slides**: `SLIDE_LEFT`, `SLIDE_RIGHT`, `SLIDE_UP`, `SLIDE_DOWN`
- **Pushes**: `PUSH_LEFT`, `PUSH_RIGHT`, `PUSH_UP`, `PUSH_DOWN`
- **Wipes**: `WIPE_LEFT`, `WIPE_RIGHT`, `WIPE_UP`, `WIPE_DOWN`
- **Shapes**: `IRIS_OPEN`, `IRIS_CLOSE`, `CLOCK_WIPE`, `DIAMOND_WIPE`, `BLINDS_HORIZONTAL`, `BLINDS_VERTICAL`
- **Animated**: `ZOOM_THROUGH`, `WHIP_PAN`, `PIXELATE`, `GLITCH`

### Effects (Phase 2)
```python
from engine.effects import brightness, contrast, saturation, vignette, film_grain

# Color grading
brightness(0.1)              # -1.0 to 1.0
contrast(1.2)                # 0.0 to 2.0
saturation(0.9)              # 0.0 to 2.0

# Cinematic
vignette(intensity=0.4, radius=0.8)
film_grain(intensity=0.05)

# Animated
fade_in(1.0)
fade_out(1.0)
```

## Common Patterns

### Cinematic Look
```python
from engine.effects import chain_effects, brightness, contrast, vignette

cinematic = chain_effects(
    brightness(0.05),
    contrast(1.2),
    vignette(intensity=0.5)
)

clip = ImageClip("image.jpg", duration=3.0, effects=[cinematic])
```

### Smooth Transitions
```python
transitions = [
    Transition(type=TransitionType.CROSSFADE, duration=0.8),
    Transition(type=TransitionType.SLIDE_LEFT, duration=1.0),
]
```

### Vintage Film
```python
from engine.effects import saturation, film_grain, chain_effects

vintage = chain_effects(
    saturation(0.7),
    film_grain(intensity=0.08)
)
```

## Demo Scripts

| Script | Description |
|--------|-------------|
| `demo_phase2_showcase.py` | Full demo with TTS, subtitles, all features |
| `demo_phase2_simple.py` | Visual-only demo, no TTS |
| `test_real_video.py` | Original Phase 1 demo |

## Troubleshooting

**Images not found?**
```python
from pathlib import Path
source=Path("images/photo.jpg").absolute()
```

**Transition too long?**
```
Transition duration must be ≤ min(clip durations)
```

**Slow rendering?**
- Reduce FPS to 15-20 for testing
- Use simpler transitions (crossfade)
- Lower resolution (1280x720)

## Next Steps

1. Run `demo_phase2_showcase.py` to see all features
2. Modify the demo with your own images
3. Read `PHASE2_USAGE_GUIDE.md` for detailed documentation
4. Check `tests/test_phase2_integration.py` for more examples

## File Locations

- **Demo scripts**: `demo_phase2_*.py`
- **Test images**: `tests/fixtures/images/`
- **Output**: `output/phase2_*/`
- **Full guide**: `PHASE2_USAGE_GUIDE.md`
