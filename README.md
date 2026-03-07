# PRISM

Generate narrated videos with **word-by-word subtitle highlighting** — powered by [Kokoro TTS](https://github.com/hexgrad/kokoro) and [MoviePy](https://zulko.github.io/moviepy/).

Write text → run one command → get a video with synced audio and highlighted subtitles.

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

## Quick Start (CLI)

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
output/run_20260302_045525/
├── input.txt              ← snapshot of what was used
├── output_moviepy.json    ← word-level timestamps
├── output_moviepy.wav     ← generated audio
├── output_moviepy_word.srt← standard SRT subtitles
└── output_video.mp4       ← final video
```

## Library API

PRISM can be used as a Python library for programmatic video generation:

### Generate Video from Text

```python
from pathlib import Path
from api.library import generate_video_from_text

# Generate video from text string
text = "Hello world! This is a test."
output_dir = Path("output/my_video")

video_path = generate_video_from_text(text, output_dir)
print(f"Video created at: {video_path}")
```

### Generate Video from File

```python
from pathlib import Path
from api.library import generate_video_from_file

# Generate video from text file
input_file = Path("files/input.txt")
output_dir = Path("output/my_video")

video_path = generate_video_from_file(input_file, output_dir)
print(f"Video created at: {video_path}")
```

### Custom Configuration

```python
from pathlib import Path
from api.library import generate_video_from_text
from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig, SubtitleMode

# Configure TTS
tts_config = TTSConfig(
    voice="af_heart",  # Kokoro voice ID
    speed=1.2,         # 20% faster speech
    lang_code="a"      # American English
)

# Configure video
video_config = VideoConfig(
    width=1280,
    height=720,
    fps=30,
    bg_color=(0, 0, 0)  # Black background
)

# Configure subtitles
subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
    font_size=36,
    text_color=(255, 255, 255),      # White text
    highlight_color=(255, 255, 0),   # Yellow highlight
    margin_bottom=100,
    vertical_align="bottom"
)

# Generate video with custom config
text = "This video uses custom settings!"
output_dir = Path("output/custom_video")

video_path = generate_video_from_text(
    text,
    output_dir,
    tts_config=tts_config,
    video_config=video_config,
    subtitle_config=subtitle_config
)
```

### Available Subtitle Modes

- `SubtitleMode.SENTENCE` — Show full sentences
- `SubtitleMode.WORD` — Show only the current word
- `SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT` — Show sentence with current word highlighted (default)
- `SubtitleMode.STACKING` — Stack words as they're spoken

## Migration Guide

### Upgrading from Pre-Refactoring API

If you were using the old `api.py` interface, here's how to migrate to the new library API:

#### Old API (Still Supported via `api.legacy`)

```python
from api import generate_video

# Old way: required pre-generated audio and JSON files
generate_video(
    json_file="output/subtitles.json",
    audio_file="output/audio.wav",
    output_video="output/video.mp4",
    width=1920,
    height=1080,
    fps=30,
    bg_color=(0, 0, 0),
    text_color=(255, 255, 255),
    highlight_color=(255, 255, 0)
)
```

#### New API (Recommended)

```python
from pathlib import Path
from api.library import generate_video_from_text
from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig

# New way: generate everything from text
text = "Your narration text here"
output_dir = Path("output/my_video")

video_path = generate_video_from_text(
    text,
    output_dir,
    tts_config=TTSConfig(voice="af_heart", speed=1.0),
    video_config=VideoConfig(width=1920, height=1080, fps=30, bg_color=(0, 0, 0)),
    subtitle_config=SubtitleConfig(
        text_color=(255, 255, 255),
        highlight_color=(255, 255, 0)
    )
)
```

#### Key Changes

1. **Text-first API**: The new API generates TTS audio automatically from text, eliminating the need to manage intermediate files
2. **Type-safe configuration**: Configuration is now split into domain-specific classes (`TTSConfig`, `VideoConfig`, `SubtitleConfig`) instead of a single dictionary
3. **Cleaner imports**: Import from `api.library` for the new API, or `api.legacy` for backward compatibility
4. **Path objects**: The new API uses `pathlib.Path` objects instead of strings for file paths
5. **Return value**: The new API returns the path to the generated video file

#### Backward Compatibility

The old API is still available for users who need to render videos from pre-existing audio and JSON files:

```python
from api.legacy import generate_video

# This still works exactly as before
generate_video(
    json_file="output/subtitles.json",
    audio_file="output/audio.wav",
    output_video="output/video.mp4"
)
```

### Configuration Migration

#### Old Config Dictionary

```python
config = {
    "voice": "af_heart",
    "speed": 1.0,
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "bg_color": (0, 0, 0),
    "font_size": 40,
    "text_color": (255, 255, 255),
    "highlight_color": (255, 255, 0)
}
```

#### New Config Classes

```python
from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig

tts_config = TTSConfig(
    voice="af_heart",
    speed=1.0,
    lang_code="a"
)

video_config = VideoConfig(
    width=1920,
    height=1080,
    fps=30,
    bg_color=(0, 0, 0)
)

subtitle_config = SubtitleConfig(
    font_size=40,
    text_color=(255, 255, 255),
    highlight_color=(255, 255, 0)
)
```

### CLI Usage (Unchanged)

The CLI interface remains the same:

```bash
# Edit files/input.txt, then run:
make run
```

The CLI automatically uses the new library API under the hood.

## Make Targets

```bash
make help             # Show all available targets
make setup            # Create venv + install deps
make install          # Install deps into existing venv
make run              # Run the full pipeline
make test             # Run all tests (unit + integration + stress)
make test-unit        # Run unit tests only (fast)
make test-integration # Run integration tests (with TTS)
make test-stress      # Run stress tests (resolutions/modes)
make test-all         # Run all tests with detailed output
make clean            # Delete all run outputs
make clean-test       # Delete test outputs only
```

## Testing

The project includes comprehensive unit and integration tests.

### Run All Tests

```bash
make test
```

This runs the complete test suite including unit tests, integration tests, and stress tests.

### Test Commands

```bash
make test              # Run all tests (recommended)
make test-unit         # Run unit tests only (fast, no TTS generation)
make test-integration  # Run integration tests (includes TTS generation)
make test-stress       # Run subtitle stress tests across resolutions/modes
make test-all          # Run all tests with detailed output
```

### Alternative: Direct pytest

You can also run tests directly with pytest:

```bash
# Activate venv first
source .venv/bin/activate  # or: . .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_library_api.py -v

# Run specific test
pytest tests/test_library_api.py::TestGenerateVideoFromTextUnit::test_creates_output_directory -v
```

### Test Coverage

- **Unit tests**: Test individual components (TTS engine, punctuation merger, sentence grouper, etc.)
- **Integration tests**: Test the complete pipeline with various text inputs and configurations
- **Stress tests**: Test multiple resolutions and subtitle modes to ensure rendering stability

### What Tests Cover

- Multiple text fixtures (`tests/fixtures/text/`): short, long, multi-paragraph, punctuation-heavy, unicode-like, and single-word
- Multiple video/subtitle variants: different resolutions and subtitle modes (`sentence`, `word`, `sentence_with_word_highlight`, `stacking`)
- Render sanity checks:
  - Output video file is created for each case
  - Output is non-empty
  - A frame sampled during subtitle visibility has pixels different from pure background (subtitle draw sanity check)
- Component isolation: Each processing component can be tested independently

## Configuration

Edit `config.py` to change default settings for CLI usage:

```python
# TTS
"voice": "af_heart",    # Kokoro voice ID
"speed": 1.0,           # Playback speed
"lang_code": "a",       # Language code (a = American English)

# Video
"width": 1920,           # Resolution
"height": 1080,
"fps": 30,
"bg_color": (0, 0, 0),         # Black background

# Subtitles
"font_size": 40,
"text_color": (255, 255, 255),  # White text
"highlight_color": (255, 255, 0), # Yellow highlight
```

For programmatic usage, pass configuration objects directly to the API functions (see Library API section above).

## Architecture

The project follows a modular, layered architecture:

```
Library API (api/library.py)
    ↓
Pipeline Orchestrator (pipeline/orchestrator.py)
    ↓
┌─────────────┬──────────────────┬─────────────────┐
│  TTS Engine │ Text Processors  │ Video Renderer  │
│             │                  │                 │
│ ITTSEngine  │ PunctuationMerger│ Subtitle System │
│ ↓           │ SentenceGrouper  │ (Source→Layout  │
│ Kokoro      │                  │  →Renderer)     │
└─────────────┴──────────────────┴─────────────────┘
```

Key design principles:

- **Dependency injection**: Components depend on interfaces, not concrete implementations
- **Single responsibility**: Each class has one clear purpose
- **Testability**: All components can be tested in isolation
- **Library-first**: Clean API for programmatic usage, with CLI as a thin wrapper

For detailed architecture documentation, see [docs/architecture.md](docs/architecture.md).

## Project Structure

```
prism/
├── api/
│   ├── library.py           ← New library API (generate_video_from_text, generate_video_from_file)
│   └── legacy.py            ← Legacy API (backward compatibility)
├── tts/
│   ├── interfaces.py        ← ITTSEngine interface
│   ├── kokoro_engine.py     ← Kokoro TTS implementation
│   └── config.py            ← TTSConfig
├── processing/
│   ├── models.py            ← Data models (TTSToken, WordToken, SentenceSegment)
│   ├── punctuation.py       ← PunctuationMerger
│   └── grouping.py          ← SentenceGrouper
├── pipeline/
│   └── orchestrator.py      ← TTSPipeline orchestrator
├── config/
│   └── video_config.py      ← VideoConfig
├── io_adapters/
│   ├── interfaces.py        ← I/O interfaces
│   └── implementations.py   ← File-based I/O implementations
├── subtitle/                ← Modular subtitle pipeline
│   ├── interfaces.py        ← ISubtitleSource, ISubtitleLayout, ISubtitleRenderer
│   ├── source.py            ← JsonSubtitleSource
│   ├── composer.py          ← SubtitleFrameComposer
│   ├── layouts.py           ← Layout strategies
│   └── renderer.py          ← PillowSubtitleRenderer
├── files/
│   └── input.txt            ← Your narration text (edit this for CLI)
├── output/                  ← Generated runs (gitignored)
│   └── run_YYYYMMDD_HHMMSS/
├── tests/                   ← Unit and integration tests
│   ├── conftest.py
│   ├── run_tests.sh
│   └── fixtures/
├── docs/
│   ├── architecture.md      ← Detailed architecture documentation
│   └── how_it_works.md      ← Technical pipeline walkthrough
├── main.py                  ← CLI entry point
├── config.py                ← Legacy config (CLI defaults)
├── renderer.py              ← Video rendering
├── subtitle_config.py       ← SubtitleConfig
├── Makefile                 ← Build & run shortcuts
└── requirements.txt         ← Dependencies
```

## How It Works (Summary)

1. **TTS Generation** — Kokoro generates audio and word-level timestamps from input text
2. **Punctuation Merging** — Standalone punctuation tokens are merged into adjacent words for clean display
3. **Sentence Grouping** — Words are grouped into sentences (split at `.!?` or 5s max duration)
4. **Video Rendering** — For each video frame at time `t`, the renderer finds the active sentence, draws all its words, and highlights the currently-spoken word

For a deep dive, see [docs/how_it_works.md](docs/how_it_works.md) and [docs/architecture.md](docs/architecture.md).

## Advanced Usage

### Custom TTS Engine

The architecture supports swapping TTS engines by implementing the `ITTSEngine` interface:

```python
from tts.interfaces import ITTSEngine, TTSResult, TTSToken

class MyCustomTTSEngine(ITTSEngine):
    def generate(self, text: str) -> TTSResult:
        # Your TTS implementation here
        pass
```

### Custom Subtitle Components

You can customize subtitle rendering by providing your own implementations:

```python
from api.legacy import generate_video
from subtitle.interfaces import ISubtitleLayout, ISubtitleRenderer

class MyCustomLayout(ISubtitleLayout):
    # Your layout logic here
    pass

class MyCustomRenderer(ISubtitleRenderer):
    # Your rendering logic here
    pass

generate_video(
    json_file="output/subtitles.json",
    audio_file="output/audio.wav",
    output_video="output/video.mp4",
    layout=MyCustomLayout(),
    renderer=MyCustomRenderer()
)
```

### In-Memory Testing

For testing without filesystem I/O:

```python
from io_adapters.implementations import InMemoryAudioWriter, InMemoryMetadataWriter
from pipeline.orchestrator import TTSPipeline
from tts.kokoro_engine import KokoroTTSEngine
from tts.config import TTSConfig
from processing.punctuation import PunctuationMerger
from processing.grouping import SentenceGrouper

# Create in-memory writers
audio_writer = InMemoryAudioWriter()
metadata_writer = InMemoryMetadataWriter()

# Create pipeline
pipeline = TTSPipeline(
    tts_engine=KokoroTTSEngine(TTSConfig()),
    punctuation_merger=PunctuationMerger(),
    sentence_grouper=SentenceGrouper(),
    audio_writer=audio_writer,
    metadata_writer=metadata_writer
)

# Process text
segments = pipeline.process("Test text")

# Access results in memory
audio_data = audio_writer.audio
subtitle_segments = metadata_writer.segments
```

## Iterating

The project is designed for fast iteration:

1. **Change text** → edit `files/input.txt` → `make run`
2. **Change voice/speed** → edit `config.py` → `make run`
3. **Change video look** → edit colors/resolution in `config.py` → `make run`

Every run is preserved in its own timestamped directory with a snapshot of the input text, so you can always compare or roll back.

For programmatic usage, simply call the API functions with different parameters — no file editing required.

## Documentation

- [Architecture Overview](docs/architecture.md) — Detailed architecture and design patterns
- [How It Works](docs/how_it_works.md) — Technical pipeline walkthrough
- [API Reference](api/library.py) — Library API documentation (see docstrings)
- [Legacy API](api/legacy.py) — Backward compatibility API

## Contributing

When contributing, please:

- Follow PEP 8 style guidelines
- Use type hints with `from __future__ import annotations`
- Write unit tests for new components
- Ensure all tests pass with `./tests/run_tests.sh`
- Update documentation for API changes

## License

See LICENSE file for details.
