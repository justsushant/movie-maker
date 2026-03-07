# PRISM Examples

Working examples demonstrating Phase 1 and Phase 2 video engine features.

## 📁 Available Examples

### General Demos

**`demo_phase2_showcase.py`** - Complete feature showcase
- Full TTS narration with subtitles
- All Phase 1 motion effects
- All Phase 2 transitions and effects
- Uses test images from `tests/fixtures/images/`
- Duration: ~15 seconds

**`demo_phase2_simple.py`** - Quick visual demo
- No TTS, just video engine
- Fast rendering for testing
- Same visual features as showcase
- Duration: ~6 seconds

### Project Examples

**`dragon/`** - Dragon Legends Epic
- 10 dragon-themed images
- Epic cinematic color grading
- Dramatic transitions
- Fantasy/mythical theme
- Full narration about dragon legends

**`mahabharata/`** - The Great War of Dharma
- 12 Mahabharata epic images
- Three thematic color grades (war, divine, wisdom)
- Cultural saffron/gold subtitle colors
- Epic narration about dharma vs adharma

## 🚀 Running Examples

### From Project Root

All examples should be run from the project root directory:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run any example
python examples/demo_phase2_showcase.py
python examples/demo_phase2_simple.py
python examples/dragon/create_dragon_video.py
python examples/mahabharata/create_mahabharata_video.py
```

### Quick Test

```bash
# Fastest test (no TTS)
python examples/demo_phase2_simple.py

# Output: output/phase2_simple/showcase.mp4
```

## 📖 Example Structure

Each project example includes:
- **Main script** - Full video with TTS narration
- **Simple script** - Visual-only for quick testing
- **README.md** - Complete documentation

```
examples/
├── demo_phase2_showcase.py      # General showcase
├── demo_phase2_simple.py        # Quick test
├── dragon/
│   ├── create_dragon_video.py
│   ├── create_dragon_video_simple.py
│   └── README.md
└── mahabharata/
    ├── create_mahabharata_video.py
    ├── create_mahabharata_video_simple.py
    └── README.md
```

## 🎨 What Each Example Demonstrates

### Phase 1 Features (All Examples)
- ✅ Image-based video composition
- ✅ Motion effects (Ken Burns, pan, zoom)
- ✅ Virtual camera system
- ✅ Smooth easing functions

### Phase 2 Features (All Examples)
- ✅ 24 transition types
- ✅ Visual effects (color grading, vignette, film grain)
- ✅ Effect chaining
- ✅ Cinematic color grading

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
├── dragon_legends/          # dragon/create_dragon_video.py
├── dragon_simple/           # dragon/create_dragon_video_simple.py
├── mahabharata_epic/        # mahabharata/create_mahabharata_video.py
└── mahabharata_simple/      # mahabharata/create_mahabharata_video_simple.py
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
# Change to any of 24 transition types
```

### Change Effects
```python
effects=[brightness(0.1), vignette(intensity=0.4)]
# Mix and match any effects
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
| dragon (simple) | ~24s | 30-60s | ~8-12 MB |
| dragon (full) | ~36s | 2-3 min | ~12-18 MB |
| mahabharata (simple) | ~27s | 30-60s | ~10-15 MB |
| mahabharata (full) | ~35s | 2-3 min | ~15-20 MB |

## 🎯 Use Cases

### Learning
- Start with `demo_phase2_simple.py` to see basic features
- Progress to `demo_phase2_showcase.py` for full pipeline
- Study project examples for real-world usage

### Testing
- Use simple versions for quick visual tests
- Test different transitions and effects
- Verify installation and setup

### Templates
- Copy project examples as templates
- Customize for your own content
- Mix and match features

## 📝 Creating Your Own Example

1. **Create directory**: `examples/your_project/`
2. **Add images**: Place in `files/your_project/`
3. **Write script**: Copy and modify an existing example
4. **Add narration**: Create `files/your_project/input.txt`
5. **Run**: `python examples/your_project/create_video.py`

### Template Structure

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.library import generate_video_from_text
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.effects import brightness, vignette, chain_effects

# Your configuration here
# ...

# Generate video
video_path = generate_video_from_text(
    text=your_text,
    output_dir=Path("output/your_project"),
    scene=your_scene
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
- Use fewer effects

## 📚 Documentation

- **[Getting Started](../docs/getting_started.md)** - Installation and basics
- **[Video Engine](../docs/video_engine.md)** - Complete feature guide
- **[Quick Reference](../docs/quick_reference.md)** - Cheat sheet
- **[Main README](../README.md)** - Project overview

## 🎓 Next Steps

1. **Run the demos** to see what's possible
2. **Read project READMEs** for detailed examples
3. **Customize** an example for your content
4. **Create** your own video project

---

**Ready to create?** Start with `python examples/demo_phase2_simple.py` 🎬
