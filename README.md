# movie-maker

Turn text and images into narrated videos with word-by-word subtitle highlighting, cinematic motion, transitions, and effects.

Powered by [Kokoro TTS](https://github.com/hexgrad/kokoro) and [MoviePy](https://zulko.github.io/moviepy/).

## Sample output

This video was generated entirely by movie-maker: TTS narration, karaoke subtitles, Ken Burns motion, transitions, and cinematic effects.

https://github.com/user-attachments/assets/52c6fc5e-d634-4562-b5fa-0886646c95bd

Recreate a similar result:

```bash
python examples/engagement_max_demo.py
```

Place your images in `examples/wolves/` (or point the script at another folder).

## Features

- **Text-to-speech** with word-level timestamps
- **Karaoke subtitles** in multiple layout styles
- **Motion presets** (Ken Burns, pan, zoom)
- **24+ transitions** (crossfade, slide, wipe, iris, glitch, and more)
- **60+ visual effects** including color grading, blur, stylization, and texture overlays
- **Audio-reactive visuals** (beat sync, onset flash, energy-driven zoom and brightness)
- **Declarative Scene DSL** for programmatic composition
- **Library API** for scripts, batch jobs, and custom pipelines

## Quick start

**Requirements:** Python 3.10+, GPU optional (faster TTS). Install [librosa](https://librosa.org/) for audio-reactive features.

```bash
make setup
```

Edit `files/input.txt`, then:

```bash
make run
```

Each run writes to a timestamped folder under `output/`:

```
output/run_20260308_123456/
├── output_video.mp4
├── output_moviepy.wav
├── output_moviepy.json
└── output_moviepy_word.srt
```

> First run downloads Kokoro model weights (~300 MB) and the spaCy English model automatically.

## Examples

| Command | What it shows |
|---------|---------------|
| `python examples/demo_phase2_simple.py` | Fast visual demo (no TTS) |
| `python examples/demo_phase2_showcase.py` | Full Phase 1 and 2 with narration |
| `python examples/demo_phase3_audio_reactive.py` | Beat sync and audio-reactive effects |
| `python examples/demo_phase4_rich_effects.py` | Phase 4 effect library showcase |
| `python examples/engagement_max_demo.py` | Maximum engagement preset (wolves demo) |
| `python examples/dragon/create_dragon_video_phase4.py` | 7 styled dragon videos |
| `python examples/mahabharata/create_mahabharata_video_phase4.py` | 8 styled epic videos |

See [`examples/README.md`](examples/README.md) for full details.

## Python API

```python
from pathlib import Path
from api.library import generate_video_from_text

video_path = generate_video_from_text(
    "Hello world! This is movie-maker.",
    Path("output/hello"),
)
```

For scenes with motion, transitions, and effects:

```python
from pathlib import Path
from api.library import generate_video_from_text
from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.effects import brightness, vignette, chain_effects

scene = Scene(
    clips=[
        ImageClip(
            source="images/photo1.jpg",
            duration=3.0,
            motion=MotionPreset.KEN_BURNS_ZOOM_IN,
            effects=[chain_effects(brightness(0.1), vignette(intensity=0.4))],
        ),
        ImageClip(
            source="images/photo2.jpg",
            duration=3.0,
            motion=MotionPreset.PAN_LEFT,
        ),
    ],
    transitions=[Transition(type=TransitionType.CROSSFADE, duration=0.8)],
    resolution=(1920, 1080),
    fps=30,
)

generate_video_from_text(
    text="Your narration here.",
    output_dir=Path("output/my_video"),
    scene=scene,
)
```

More in [Getting Started](docs/getting_started.md) and [Video Engine](docs/video_engine.md).

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/getting_started.md) | Install, first video, API usage |
| [Video Engine](docs/video_engine.md) | Motion, transitions, effects |
| [Quick Reference](docs/quick_reference.md) | Cheat sheet |
| [Architecture](docs/architecture.md) | System design |
| [How It Works](docs/how_it_works.md) | Pipeline internals |

Full index: [`docs/README.md`](docs/README.md)

## Development

```bash
make test              # Full test suite
make test-unit         # Unit tests only
make test-integration  # Integration tests with TTS
make clean             # Remove generated output/
```

The test suite covers unit, integration, property-based, visual regression, and Phase 4 edge-case tests.

## Project layout

```
movie-maker/
├── api/          Library entry points
├── engine/       Video engine (motion, transitions, effects)
├── subtitle/     Subtitle rendering
├── tts/          Text-to-speech
├── docs/         Documentation and sample video
├── examples/     Runnable demos
├── tests/        Test suite
└── files/        Default input text and sample images
```

## Contributing

Contributions welcome. Follow PEP 8, use type hints (`from __future__ import annotations`), add tests for new behavior, and run `make test` before opening a PR.

---

[Documentation](docs/README.md) · [Examples](examples/) · [Getting Started](docs/getting_started.md)
