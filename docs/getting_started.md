# Getting Started with PRISM

## Quick Start (30 seconds)

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Edit your text
echo "Hello world! This is a test." > files/input.txt

# 3. Generate video
make run

# 4. Watch your video
open output/run_*/output_video.mp4
```

## What You Need

### Essential Requirements

1. **Python 3.10+** with virtual environment
2. **Text script** (plain text file or string)
3. **Images** (optional, for video engine features)

### Optional Requirements

- **GPU** - Recommended for faster TTS (CPU works but slower)
- **FFmpeg** - Usually installed with MoviePy

## Installation

### First Time Setup

```bash
# Clone the repository
git clone <repository-url>
cd prism

# Create virtual environment and install dependencies
make setup

# Verify installation
source .venv/bin/activate
python -c "import kokoro; print('✓ Kokoro installed')"
```

### What Gets Installed

- `kokoro>=0.9.4` - Text-to-speech engine
- `moviepy` - Video composition
- `pillow` - Image processing and subtitle rendering
- `numpy` - Array processing
- `opencv-python` - Image transforms (for video engine)
- `soundfile` - Audio I/O
- `pytest` - Testing framework
- `hypothesis` - Property-based testing

> **Note:** First run downloads TTS model weights (~300 MB) and spaCy English model automatically.

## Basic Usage

### CLI Mode (Simplest)

1. **Edit your text:**
   ```bash
   nano files/input.txt
   ```

2. **Run the pipeline:**
   ```bash
   make run
   ```

3. **Find your video:**
   ```
   output/run_YYYYMMDD_HHMMSS/output_video.mp4
   ```

### Python API (Programmatic)

```python
from pathlib import Path
from api.library import generate_video_from_text

# Generate video from text
text = "Hello world! This is a test."
output_dir = Path("output/my_video")

video_path = generate_video_from_text(text, output_dir)
print(f"Video created: {video_path}")
```

## Your First Video

### Example 1: Simple Narration

```python
from pathlib import Path
from api.library import generate_video_from_text

text = """
Welcome to PRISM.
This tool generates narrated videos with word-by-word subtitle highlighting.
It's powered by Kokoro TTS and MoviePy.
"""

video_path = generate_video_from_text(
    text=text,
    output_dir=Path("output/welcome")
)
```

**Output:** Video with TTS narration and karaoke-style subtitles

### Example 2: Custom Styling

```python
from pathlib import Path
from api.library import generate_video_from_text
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig, SubtitleMode

text = "This video has custom styling!"

video_config = VideoConfig(
    width=1280,
    height=720,
    fps=30,
    bg_color=(20, 20, 40)  # Dark blue background
)

subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
    font_size=48,
    base_color=(255, 255, 255),      # White text
    highlight_color=(255, 200, 100),  # Golden highlight
    y_margin=0.15,
    vertical_align="bottom"
)

video_path = generate_video_from_text(
    text=text,
    output_dir=Path("output/custom"),
    video_config=video_config,
    subtitle_config=subtitle_config
)
```

### Example 3: Video with Images (Phase 1 & 2)

```python
from pathlib import Path
from api.library import generate_video_from_text
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.effects import brightness, vignette

text = "Watch as images come to life with motion and transitions."

scene = Scene(
    clips=[
        ImageClip(
            source="images/photo1.jpg",
            duration=3.0,
            motion=MotionPreset.KEN_BURNS_ZOOM_IN,
            effects=[brightness(0.1)]
        ),
        ImageClip(
            source="images/photo2.jpg",
            duration=3.0,
            motion=MotionPreset.PAN_LEFT,
            effects=[vignette(intensity=0.4)]
        ),
    ],
    transitions=[
        Transition(type=TransitionType.CROSSFADE, duration=0.5)
    ],
    resolution=(1920, 1080),
    fps=30
)

video_path = generate_video_from_text(
    text=text,
    output_dir=Path("output/with_images"),
    scene=scene
)
```

## Configuration Options

### TTS Configuration

```python
from tts.config import TTSConfig

tts_config = TTSConfig(
    voice="af_heart",    # Voice ID (af_heart, af_bella, etc.)
    speed=1.0,           # Speech speed (0.5 to 2.0)
    lang_code="a"        # Language: "a" (American), "b" (British)
)
```

### Video Configuration

```python
from config.video_config import VideoConfig

video_config = VideoConfig(
    width=1920,          # Video width
    height=1080,         # Video height
    fps=30,              # Frame rate
    bg_color=(0, 0, 0)   # Background color (R, G, B)
)
```

### Subtitle Configuration

```python
from subtitle.config import SubtitleConfig, SubtitleMode

subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,  # Subtitle mode
    font_size=48,                    # Font size in pixels
    base_color=(255, 255, 255),      # Text color (R, G, B)
    highlight_color=(255, 255, 0),   # Highlight color (R, G, B)
    y_margin=0.1,                    # Vertical margin (0.0 to 1.0)
    vertical_align="bottom"          # Position: "top", "center", "bottom"
)
```

### Subtitle Modes

- `SENTENCE` - Show full sentences
- `WORD` - Show only current word
- `SENTENCE_WITH_WORD_HIGHLIGHT` - Sentence with word highlighted (default)
- `STACKING` - Stack words as they're spoken

## Output Files

Each run creates a timestamped directory:

```
output/run_20260308_123456/
├── input.txt              # Snapshot of input text
├── output_moviepy.json    # Word-level timestamps
├── output_moviepy.wav     # Generated audio
├── output_moviepy_word.srt # SRT subtitle file
└── output_video.mp4       # Final video ✨
```

## Common Tasks

### Change Voice

```python
from tts.config import TTSConfig

# Available voices: af_heart, af_bella, af_sarah, etc.
tts_config = TTSConfig(voice="af_bella")
```

### Change Speed

```python
from tts.config import TTSConfig

# 1.5x faster
tts_config = TTSConfig(speed=1.5)

# 0.8x slower
tts_config = TTSConfig(speed=0.8)
```

### Change Resolution

```python
from config.video_config import VideoConfig

# 720p
video_config = VideoConfig(width=1280, height=720)

# 4K
video_config = VideoConfig(width=3840, height=2160)
```

### Change Subtitle Position

```python
from subtitle.config import SubtitleConfig

# Top of screen
subtitle_config = SubtitleConfig(vertical_align="top", y_margin=0.1)

# Center of screen
subtitle_config = SubtitleConfig(vertical_align="center")

# Bottom of screen (default)
subtitle_config = SubtitleConfig(vertical_align="bottom", y_margin=0.1)
```

## Next Steps

- **Video Engine Features**: See [video_engine.md](video_engine.md) for motion effects and transitions
- **API Reference**: See [api_reference.md](api_reference.md) for complete API documentation
- **Examples**: Check `demo_phase2_showcase.py` for advanced examples
- **Architecture**: Read [architecture.md](architecture.md) to understand the system design

## Troubleshooting

### Virtual Environment Not Activated

```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Missing Dependencies

```bash
make setup  # Reinstall everything
```

### TTS Model Download Fails

The model downloads automatically on first run. If it fails:
- Check internet connection
- Ensure sufficient disk space (~300 MB)
- Try running again (downloads resume)

### Video Generation Fails

1. Check that input text is not empty
2. Verify output directory is writable
3. Ensure FFmpeg is installed (comes with MoviePy)
4. Check logs for specific error messages

### Slow Performance

- **TTS**: Use GPU if available, or reduce text length
- **Video**: Lower resolution or FPS for testing
- **Effects**: Reduce number of effects or use simpler transitions

## Getting Help

1. **Check documentation**: Browse `docs/` directory
2. **Run tests**: `make test` to verify installation
3. **Review examples**: See demo scripts in root directory
4. **Read source**: Code is well-documented with docstrings

## Quick Reference

```bash
# Setup
make setup              # Install everything
make install            # Install deps only

# Running
make run                # CLI mode
python your_script.py   # API mode

# Testing
make test               # Run all tests
make test-unit          # Unit tests only
make test-integration   # Integration tests

# Cleanup
make clean              # Delete all outputs
make clean-test         # Delete test outputs
```

Ready to create your first video? Start with the CLI mode or jump to [video_engine.md](video_engine.md) for advanced features!
