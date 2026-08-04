# PRISM Examples

Working examples demonstrating all video engine phases (1-4).

## 📁 Available Examples

### General Demos

**`demo_phase2_showcase.py`** - Phase 1 & 2 feature showcase
- Full TTS narration with subtitles
- All Phase 1 motion effects
- All Phase 2 transitions and effects
- Uses test images from `tests/fixtures/images/`
- Duration: ~15 seconds

**`demo_phase2_simple.py`** - Quick Phase 1 & 2 visual demo
- No TTS, just video engine
- Fast rendering for testing
- Same visual features as showcase
- Duration: ~6 seconds

**`demo_phase3_audio_reactive.py`** - Phase 3 audio-reactive demo
- Beat-synchronized transitions
- Audio-reactive effects (OnsetFlash, EnergyZoom, EnergyBrightness)
- Spectral color shifting
- Requires librosa and an audio file

**`demo_phase4_rich_effects.py`** - Phase 4 rich effects demo
- 56+ visual effects across 4 categories
- Color effects, blur effects, texture overlays, stylization
- Advanced transitions showcase
- Effect chain combinations
- No TTS required (uses generated test images)

### Project Examples

**`dragon/`** - Dragon Legends Epic
- 10 dragon-themed images
- Epic cinematic color grading
- Dramatic transitions
- Fantasy/mythical theme
- Full narration about dragon legends
- Phase 4 variant: `create_dragon_video_phase4.py` (7 styled versions)

**`mahabharata/`** - The Great War of Dharma
- 12 Mahabharata epic images
- Three thematic color grades (war, divine, wisdom)
- Cultural saffron/gold subtitle colors
- Epic narration about dharma vs adharma
- Phase 4 variant: `create_mahabharata_video_phase4.py` (8 styled versions)

## 🚀 Running Examples

### From Project Root

All examples should be run from the project root directory:

```bash
# Activate virtual environment
source .venv/bin/activate

# Phase 1 & 2 demos
python examples/demo_phase2_showcase.py
python examples/demo_phase2_simple.py

# Phase 3 audio-reactive demo
python examples/demo_phase3_audio_reactive.py

# Phase 4 rich effects demo
python examples/demo_phase4_rich_effects.py

# Project examples
python examples/dragon/create_dragon_video.py
python examples/dragon/create_dragon_video_phase4.py
python examples/mahabharata/create_mahabharata_video.py
python examples/mahabharata/create_mahabharata_video_phase4.py
```

### Quick Test

```bash
# Fastest test (no TTS, no audio)
python examples/demo_phase2_simple.py

# Phase 4 effects test (no TTS required)
python examples/demo_phase4_rich_effects.py
```

## 📖 Example Structure

```
examples/
├── demo_phase2_showcase.py      # Phase 1 & 2 showcase
├── demo_phase2_simple.py        # Quick Phase 1 & 2 test
├── demo_phase3_audio_reactive.py  # Phase 3 audio-reactive
├── demo_phase4_rich_effects.py  # Phase 4 rich effects
├── PHASE4_SHOWCASE.md           # Phase 4 showcase guide
├── TEXT_OVERLAY_USAGE.md        # Text overlay usage guide
├── dragon/
│   ├── create_dragon_video.py
│   ├── create_dragon_video_simple.py
│   ├── create_dragon_video_phase4.py  # 7 Phase 4 styled versions
│   └── README_PHASE4.md
└── mahabharata/
    ├── create_mahabharata_video.py
    ├── create_mahabharata_video_simple.py
    └── create_mahabharata_video_phase4.py  # 8 Phase 4 styled versions
```

## 🎨 What Each Example Demonstrates

### Phase 1 Features (All Examples)
- ✅ Image-based video composition
- ✅ Motion effects (Ken Burns, pan, zoom)
- ✅ Virtual camera system
- ✅ Smooth easing functions

### Phase 2 Features (Phase 2+ Examples)
- ✅ 24 transition types
- ✅ Visual effects (color grading, vignette, film grain)
- ✅ Effect chaining
- ✅ Cinematic color grading

### Phase 3 Features (`demo_phase3_audio_reactive.py`)
- ✅ Beat-synchronized transitions
- ✅ OnsetFlash — brightens on audio transients
- ✅ EnergyZoom — scales with audio loudness
- ✅ EnergyBrightness — brightness follows energy
- ✅ EnergyShake — camera shake from audio
- ✅ SpectralColorShift — color temperature from spectral centroid
- ✅ Graceful degradation without librosa

### Phase 4 Features (`demo_phase4_rich_effects.py`, dragon/mahabharata phase4 scripts)
- ✅ 21 color effects (grayscale, sepia, hue shift, cinematic teal-orange, etc.)
- ✅ 11 blur effects (motion blur, tilt-shift, depth of field, zoom blur, etc.)
- ✅ 12 texture effects (scan lines, letterbox, light leak, bokeh overlay, etc.)
- ✅ 12 stylization effects (sketch, glitch variants, CRT retro, VHS distortion, etc.)
- ✅ Text overlay with customizable styling
- ✅ Effect chain composition

### TTS & Subtitles (Main Scripts Only)
- ✅ Kokoro TTS narration
- ✅ Word-by-word subtitle highlighting
- ✅ Custom subtitle colors
- ✅ Synchronized audio

## 🎬 Output Locations

Each example creates its own output directory:

```
output/
├── phase2_showcase/         # demo_phase2_showcase.py
├── phase2_simple/           # demo_phase2_simple.py
├── phase3_audio_reactive/   # demo_phase3_audio_reactive.py
├── phase4_demo/             # demo_phase4_rich_effects.py
├── dragon_legends/          # dragon/create_dragon_video.py
├── dragon_simple/           # dragon/create_dragon_video_simple.py
├── dragon_phase4/           # dragon/create_dragon_video_phase4.py (7 videos)
├── mahabharata_epic/        # mahabharata/create_mahabharata_video.py
├── mahabharata_simple/      # mahabharata/create_mahabharata_video_simple.py
└── mahabharata_phase4/      # mahabharata/create_mahabharata_video_phase4.py (8 videos)
```

## 🔧 Customization

All examples are fully customizable. Common modifications:

### Change Clip Duration
```python
clip_duration = 3.0  # seconds per image
```

### Change Transitions
```python
Transition(type=TransitionType.CROSSFADE, duration=0.5)
# Change to any of 24+ transition types
```

### Change Phase 2 Effects
```python
effects=[brightness(0.1), vignette(intensity=0.4)]
```

### Change Phase 4 Effects
```python
from engine.effects import (
    cinematic_teal_orange, vignette_simple,
    glitch_rgb_split, tilt_shift, sepia
)

effects=[
    cinematic_teal_orange(intensity=0.8),
    vignette_simple(intensity=0.4),
    tilt_shift(blur_amount=15, gradient_start=0.3, gradient_end=0.7),
]
```

### Add Text Overlay
```python
from engine.effects import text_overlay

effects=[
    sepia(),
    text_overlay("Vintage Look", position=(50, 50), font_scale=1.5)
]
```

### Change Subtitle Colors
```python
subtitle_config = SubtitleConfig(
    base_color=(255, 255, 255),      # White
    highlight_color=(255, 200, 100)  # Gold
)
```

## 📊 Performance

Typical rendering times (on modern hardware):

| Example | Duration | Rendering Time | Output Size |
|---------|----------|----------------|-------------|
| demo_phase2_simple | ~6s | 10-20s | ~2-3 MB |
| demo_phase2_showcase | ~15s | 2-3 min | ~5-8 MB |
| demo_phase3_audio_reactive | ~15s | 2-3 min | ~5-8 MB |
| demo_phase4_rich_effects | ~30s | 3-5 min | ~10-20 MB |
| dragon (simple) | ~24s | 30-60s | ~8-12 MB |
| dragon (full) | ~36s | 2-3 min | ~12-18 MB |
| dragon phase4 (7 videos) | ~30s each | 7-14 min total | ~20-50 MB each |
| mahabharata (simple) | ~27s | 30-60s | ~10-15 MB |
| mahabharata (full) | ~35s | 2-3 min | ~15-20 MB |
| mahabharata phase4 (8 videos) | ~30s each | 8-16 min total | ~20-50 MB each |

## 🎯 Use Cases

### Learning
- Start with `demo_phase2_simple.py` to see basic features
- Progress to `demo_phase2_showcase.py` for full pipeline
- Try `demo_phase4_rich_effects.py` to explore all 56+ effects
- Study project examples for real-world usage

### Testing
- Use simple versions for quick visual tests
- Use `demo_phase4_rich_effects.py` to verify Phase 4 effects work
- Test different transitions and effects
- Verify installation and setup

### Templates
- Copy project examples as templates
- Customize for your own content
- Mix and match features from different phases

## 📝 Creating Your Own Example

1. **Create directory**: `examples/your_project/`
2. **Add images**: Place in `files/your_project/`
3. **Write script**: Copy and modify an existing example
4. **Add narration**: Create `files/your_project/input.txt`
5. **Run**: `python examples/your_project/create_video.py`

### Template Structure (Phase 4)

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.library import generate_video_from_text
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.effects import (
    cinematic_teal_orange, vignette_simple,
    film_grain, letterbox, text_overlay
)

# Define clips with Phase 4 effects
clips = [
    ImageClip(
        source="files/your_project/image1.jpg",
        duration=4.0,
        motion=MotionPreset.KEN_BURNS_ZOOM_IN,
        effects=[
            cinematic_teal_orange(intensity=0.8),
            vignette_simple(intensity=0.4),
            film_grain(intensity=0.05),
            letterbox(top=80, bottom=80),
            text_overlay("Scene 1", position=(50, 50)),
        ]
    ),
    ImageClip(
        source="files/your_project/image2.jpg",
        duration=4.0,
        motion=MotionPreset.PAN_LEFT,
        effects=[
            cinematic_teal_orange(intensity=0.8),
            vignette_simple(intensity=0.4),
        ]
    ),
]

scene = Scene(
    clips=clips,
    transitions=[
        Transition(type=TransitionType.PUSH_LEFT, duration=0.8),
    ],
    resolution=(1920, 1080),
    fps=30
)

video_path = generate_video_from_text(
    text="Your narration here.",
    output_dir=Path("output/your_project"),
    scene=scene
)
```

## 🐛 Troubleshooting

### ModuleNotFoundError
Always run from project root:
```bash
# Wrong
cd examples/dragon
python create_dragon_video.py

# Correct
python examples/dragon/create_dragon_video.py
```

### Images Not Found
Use absolute paths or ensure images are in correct location:
```python
image_path = Path("files/your_project/image.jpg").absolute()
```

### Slow Rendering
- Use simple versions first
- Reduce FPS to 20 for testing
- Lower resolution to 1280x720
- Use fewer effects (3-5 per clip recommended)

### Phase 3: Librosa Not Found
```bash
pip install librosa
```
Or continue without it — audio-reactive effects degrade gracefully.

### Phase 4: Effect Not Visible
- Check parameter ranges (intensity: 0.0-1.0, not 0-100)
- Try increasing effect intensity
- Verify effect is in the effects list

## 📚 Documentation

- **[Video Engine Guide](../docs/video_engine.md)** - Complete feature guide (all phases)
- **[Phase 4 Showcase Guide](PHASE4_SHOWCASE.md)** - Phase 4 styled video scripts
- **[Text Overlay Usage](TEXT_OVERLAY_USAGE.md)** - Text overlay reference
- **[Main README](../README.md)** - Project overview

## 🎓 Next Steps

1. **Run the demos** to see what's possible
2. **Read project READMEs** for detailed examples
3. **Customize** an example for your content
4. **Create** your own video project

---

**Ready to create?** Start with `python examples/demo_phase2_simple.py` or jump straight to Phase 4 with `python examples/demo_phase4_rich_effects.py` 🎬
