# PRISM

Generate narrated videos with **word-by-word subtitle highlighting** over **image sequences with motion effects and transitions** — powered by [Kokoro TTS](https://github.com/hexgrad/kokoro) and [MoviePy](https://zulko.github.io/moviepy/).

Write text + add images → run one command → get a professional video with synced audio, animated subtitles, and cinematic effects.

## ✨ Features

- 🎙️ **Text-to-Speech** - Natural narration with word-level timestamps
- 🎬 **Video Engine** - Motion effects, transitions, and visual effects
- 📝 **Karaoke Subtitles** - Word-by-word highlighting in multiple styles
- 🎨 **Cinematic Effects** - Color grading, vignettes, film grain
- 🔄 **24 Transitions** - Crossfades, slides, wipes, animated effects
- 🎯 **Simple API** - Declarative Scene DSL for video composition

## Installation

### Requirements

- Python 3.10 or higher
- GPU recommended for faster TTS generation (CPU works but is slower)

### Setup

```bash
make setup
```

This creates a `.venv` with Python 3.10 and installs all dependencies from `requirements.txt`:

- `kokoro>=0.9.4` — Text-to-speech engine with word-level timestamps
- `soundfile` — Audio file I/O
- `moviepy` — Video composition and rendering
- `pillow` — Subtitle text rendering
- `numpy` — Audio and video array processing
- `pytest` — Testing framework

> **First run:** Kokoro will automatically download the TTS model weights (~300 MB) and the spaCy English model.

## 🚀 Quick Start

### 30-Second Demo

### 1. Write Your Text

Edit `files/input.txt` with the text you want narrated:

```
Good morning everyone!

Today is a new beginning.
We've faced challenges, but we are still standing.
```

### 2. Run

```bash
make run
```

### 3. Outputs

Each run creates a **timestamped directory** under `output/` — nothing gets overwritten:

```
output/run_20260308_123456/
├── output_video.mp4       ← Final video ✨
├── output_moviepy.wav     ← Generated audio
├── output_moviepy.json    ← Word-level timestamps
└── output_moviepy_word.srt← SRT subtitles
```

## 📖 Documentation

**Complete documentation is in the [`docs/`](docs/) directory:**

- **[Getting Started](docs/getting_started.md)** - Installation, first video, basic usage
- **[Video Engine](docs/video_engine.md)** - Motion effects, transitions, visual effects
- **[Quick Reference](docs/quick_reference.md)** - 30-second cheat sheet
- **[Requirements](docs/requirements.md)** - What you need
- **[Architecture](docs/architecture.md)** - System design
- **[How It Works](docs/how_it_works.md)** - Technical details

**[📚 Full Documentation Index →](docs/README.md)**

## 🎬 Examples

Working examples are in the [`examples/`](examples/) directory:

```bash
# Full feature showcase with TTS
python examples/demo_phase2_showcase.py

# Quick visual demo (no TTS)
python examples/demo_phase2_simple.py

# Dragon legends example
python examples/dragon/create_dragon_video.py
```

## 🎨 Video Engine Features

### Motion Effects (Phase 1)
- Ken Burns zoom in/out
- Pan (left, right, up, down)
- Zoom in/out
- Static

### Transitions (Phase 2)
- **Blend**: Crossfade, fade through black/white
- **Geometric**: Slides, pushes, wipes (4 directions each)
- **Shapes**: Iris, clock, diamond, blinds
- **Animated**: Zoom through, whip pan, pixelate, glitch

### Visual Effects (Phase 2)
- **Color**: Brightness, contrast, saturation
- **Cinematic**: Vignette, film grain
- **Animated**: Fade in/out, pulse
- **Chainable**: Combine multiple effects

### Example with Video Engine

```python
from pathlib import Path
from api.library import generate_video_from_text
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.effects import brightness, vignette, chain_effects

# Create cinematic scene
scene = Scene(
    clips=[
        ImageClip(
            source="images/photo1.jpg",
            duration=3.0,
            motion=MotionPreset.KEN_BURNS_ZOOM_IN,
            effects=[
                chain_effects(
                    brightness(0.1),
                    vignette(intensity=0.4)
                )
            ]
        ),
        ImageClip(
            source="images/photo2.jpg",
            duration=3.0,
            motion=MotionPreset.PAN_LEFT,
            effects=[brightness(0.05)]
        ),
    ],
    transitions=[
        Transition(type=TransitionType.CROSSFADE, duration=0.8)
    ],
    resolution=(1920, 1080),
    fps=30
)

# Generate video
text = "Watch as images come to life with motion and effects."
video_path = generate_video_from_text(
    text=text,
    output_dir=Path("output/cinematic"),
    scene=scene
)
```

**[📖 Full Video Engine Documentation →](docs/video_engine.md)**

## 🐍 Library API

PRISM can be used as a Python library for programmatic video generation.

### Basic Usage

```python
from pathlib import Path
from api.library import generate_video_from_text

# Simple text-to-video
text = "Hello world! This is PRISM."
video_path = generate_video_from_text(text, Path("output/hello"))
```

### From File

```python
from pathlib import Path
from api.library import generate_video_from_file

# From text file
video_path = generate_video_from_file(
    Path("files/input.txt"),
    Path("output/my_video")
)
```

### Custom Configuration

```python
from pathlib import Path
from api.library import generate_video_from_text
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig, SubtitleMode

# Custom styling
video_config = VideoConfig(width=1280, height=720, fps=30)
subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
    font_size=48,
    base_color=(255, 255, 255),
    highlight_color=(255, 200, 100)
)

video_path = generate_video_from_text(
    text="Custom styled video!",
    output_dir=Path("output/custom"),
    video_config=video_config,
    subtitle_config=subtitle_config
)
```

**[📖 Full API Documentation →](docs/getting_started.md#python-api-programmatic)**

## 🧪 Testing

```bash
make test              # Run all tests (278 passing)
make test-unit         # Unit tests only
make test-integration  # Integration tests with TTS
make test-stress       # Stress tests across resolutions
```

**Test Coverage:**
- 278 tests passing (62 Phase 2 + 216 Phase 1)
- Unit tests for all components
- Integration tests for complete pipeline
- Property-based tests for correctness
- Visual regression tests

## 🛠️ Make Commands

```bash
make help              # Show all commands
make setup             # Install everything
make run               # Generate video from files/input.txt
make test              # Run all tests
make clean             # Delete outputs
```

## 📁 Project Structure

```
prism/
├── api/               # Library API
├── engine/            # Video engine (motion, transitions, effects)
├── subtitle/          # Subtitle system
├── tts/               # Text-to-speech
├── docs/              # Documentation
├── examples/          # Working examples
├── tests/             # Test suite
└── files/             # Input files
```

## 🎯 Use Cases

### Content Creators
- Quick narrated videos from scripts
- Image slideshows with motion
- Social media content

### Developers
- Automated video generation in workflows
- Batch processing of content
- Custom video pipelines

### Video Producers
- Professional transitions and effects
- Cinematic color grading
- Rapid prototyping

## 🚀 What's New in Phase 2

- ✅ 24 transition types (crossfade, slides, wipes, animated)
- ✅ Visual effects (color grading, vignette, film grain)
- ✅ Effect chaining
- ✅ Full backward compatibility
- ✅ 278 tests passing

## 📊 Performance

- **1080p rendering**: ~2-3ms per frame (no effects)
- **With effects**: ~5-10ms per effect
- **Transitions**: Blend <50ms, Geometric <100ms, Animated <150ms
- **10-second video**: ~1-2 seconds to render + encoding time

**[📖 Performance Details →](docs/performance_benchmarks.md)**

## 🤝 Contributing

Contributions welcome! Please:

- Follow PEP 8 style guidelines
- Use type hints with `from __future__ import annotations`
- Write tests for new features
- Update documentation
- Ensure all tests pass: `make test`

## 📄 License

See LICENSE file for details.

---

**[📚 Full Documentation](docs/README.md)** | **[🎬 Examples](examples/)** | **[🚀 Getting Started](docs/getting_started.md)**
