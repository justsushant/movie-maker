# KokoroMoviePy

Generate narrated videos with **word-by-word subtitle highlighting** — powered by [Kokoro TTS](https://github.com/hexgrad/kokoro) and [MoviePy](https://zulko.github.io/moviepy/).

Write text → run one command → get a video with synced audio and highlighted subtitles.

## Quick Start

### 1. Set Up the Environment

```bash
make setup
```

This creates a `.venv` with Python 3.10 and installs all dependencies from `requirements.txt`.

> **First run:** Kokoro will automatically download the TTS model weights (~300 MB) and the spaCy English model.

### 2. Write Your Text

Edit `files/input.txt` with the text you want narrated:

```
Good morning everyone!

Today is a new beginning.
We've faced challenges, but we are still standing.
```

### 3. Run

```bash
make run
```

### 4. Outputs

Each run creates a **timestamped directory** under `output/` — nothing gets overwritten:

```
output/run_20260302_045525/
├── input.txt              ← snapshot of what was used
├── output_moviepy.json    ← word-level timestamps
├── output_moviepy.wav     ← generated audio
├── output_moviepy_word.srt← standard SRT subtitles
└── output_video.mp4       ← final video
```

## Make Targets

```bash
make help      # Show all available targets
make setup     # Create venv + install deps
make install   # Install deps into existing venv
make run       # Run the full pipeline
make clean     # Delete all run outputs
```

## Stress Testing Subtitles

Stress tests are under `tests/` and write outputs to `output/test/`.

### Run stress tests

```bash
./tests/run_tests.sh
```

The runner activates your venv first (`.venv` or `venv`) and then runs:

```bash
python -m pytest tests/ -v
```

### What stress tests cover

- Multiple text fixtures (`tests/fixtures/text/`): short, long, multi-paragraph, punctuation-heavy, unicode-like, and single-word.
- Multiple video/subtitle variants: different resolutions and subtitle modes (`sentence`, `word`, `sentence_with_word_highlight`, `stacking`).
- Render sanity checks:
  - Output video file is created for each case.
  - Output is non-empty.
  - A frame sampled during subtitle visibility has pixels different from pure background (subtitle draw sanity check).

## Configuration

Edit `config.py` to change any setting — no other files need to be modified:

```python
# TTS
"voice": "af_heart",    # Kokoro voice ID
"speed": 1.0,           # Playback speed

# Video
"width": 1920,           # Resolution
"height": 1080,
"fps": 30,
"font_size": 40,
"bg_color": (0, 0, 0),         # Black background
"text_color": (255, 255, 255),  # White text
"highlight_color": (255, 255, 0), # Yellow highlight
```

## Project Structure

```
kokoromoviepy/
├── files/
│   └── input.txt          ← Your narration text (edit this)
├── output/                ← Generated runs (gitignored)
│   └── run_YYYYMMDD_HHMMSS/
├── config.py              ← All settings in one place
├── tts_pipeline.py        ← TTS engine + subtitle extraction
├── renderer.py            ← Video frame generation
├── main.py                ← Orchestrator (run this)
├── Makefile               ← Build & run shortcuts
├── docs/
│   └── how_it_works.md    ← Detailed technical explanation
└── requirements.txt
```

## How It Works (Summary)

1. **TTS Pipeline** — Kokoro generates audio and exposes word-level timestamps
2. **Punctuation Merging** — Standalone punctuation tokens are merged into adjacent words
3. **Sentence Grouping** — Words are grouped into sentences (split at `.!?` or 5s max)
4. **Frame Rendering** — For each video frame at time `t`, the renderer finds the active sentence, draws all its words, and highlights the currently-spoken word in yellow

For a deep dive, see [docs/how_it_works.md](docs/how_it_works.md).

## Iterating

The project is designed for fast iteration:

1. **Change text** → edit `files/input.txt` → `make run`
2. **Change voice/speed** → edit `config.py` → `make run`
3. **Change video look** → edit colors/resolution in `config.py` → `make run`

Every run is preserved in its own timestamped directory with a snapshot of the input text, so you can always compare or roll back.
