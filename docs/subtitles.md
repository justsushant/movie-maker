# Modular Subtitle System

This document describes the configurable subtitle pipeline: configuration options, interfaces, and how to use the Python API.

## Overview

Subtitles are produced by a **source** (e.g. JSON file) → **layout** (sentence/word/stacking) → **renderer** (PIL drawing). All behavior is driven by `SubtitleConfig` and optional custom implementations of the source, layout, and renderer interfaces.

- **SubtitleConfig** — Colors, position, font, mode (sentence / word / sentence-with-word-highlight / stacking), and dimension adaptation.
- **ISubtitleSource** — Supplies segments for a given time (or all segments for stacking). Default: `JsonSubtitleSource(json_path)`.
- **ISubtitleLayout** — Turns segments + time into a list of `PositionedSubtitle` (text, x, y, color, font_size). Implementations: `SentenceLayout`, `WordHighlightLayout`, `WordOnlyLayout`, `StackingLayout`.
- **ISubtitleRenderer** — Draws `PositionedSubtitle` items onto a PIL image. Default: `PillowSubtitleRenderer`.

Layout is **dimension-aware**: `SubtitleLayoutContext.from_config(width, height, subtitle_config)` computes font size, margins, and line height from the video size and config (e.g. scale font with height, respect margins).

## SubtitleConfig

Create from the global config dict or directly in Python:

```python
from subtitle.config import SubtitleConfig, SubtitleMode

# From existing config dict (e.g. from config.get_config())
cfg = get_config()
subtitle_config = SubtitleConfig.from_dict(cfg)

# Or build directly
subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
    base_color=(255, 255, 255),
    highlight_color=(255, 255, 0),
    vertical_align="bottom",
    x_margin=0.05,
    y_margin=0.05,
    max_width_ratio=0.9,
    font_size=40,
    scale_font_to_height=True,
)
```

### Config options

| Option | Description | Default |
|--------|-------------|--------|
| `mode` | `sentence`, `word`, `sentence_with_word_highlight`, `stacking` | `sentence_with_word_highlight` |
| `base_color` | RGB for non-highlighted text | `(255, 255, 255)` |
| `highlight_color` | RGB for highlighted word | `(255, 255, 0)` |
| `vertical_align` | `bottom`, `center`, `top` | `bottom` |
| `x_margin`, `y_margin` | Fraction of width/height for margins | `0.05` |
| `max_width_ratio` | Max text width as fraction of width | `0.9` |
| `font_path` | Optional TTF path | None (system default) |
| `font_size` | Fixed size if set; else scaled by height | None |
| `scale_font_to_height` | Scale font with video height | True |
| `multiline_enabled` | Allow multiline wrapping in sentence mode | `False` |
| `overflow_strategy` | How to handle overflow when multiline is off | `chunk_single_line` |
| `min_words_per_chunk` | Minimum words per single-line chunk | `1` |
| `max_words_per_chunk` | Force break after N words (optional) | None |
| `prefer_break_on_punctuation` | Prefer chunk breaks after punctuation | `True` |
| `stacking.max_visible_lines` | Lines shown in stacking mode | 3 |
| `stacking.direction` | `up` or `down` | `up` |

In the global config dict you can put a `subtitle` key with these options; `SubtitleConfig.from_dict(cfg)` reads that and falls back to top-level `text_color`, `highlight_color`, `font_size`.

## Subtitle modes

- **SENTENCE** — One sentence at a time in base color. When `multiline_enabled` is `False` (the default), long sentences are automatically split into timed single-line chunks derived from word timings so they never overflow the screen. When `multiline_enabled` is `True`, text wraps into multiple lines instead.
- **SENTENCE_WITH_WORD_HIGHLIGHT** — Same sentence with the current word in `highlight_color` (default behavior).
- **WORD** — Only the current word, larger and centered.
- **STACKING** — Last N sentences visible; newest at bottom, older ones stacked above.

## Python API

Use `api.generate_video` when you have existing JSON + audio and want to control subtitles:

```python
from subtitle.config import SubtitleConfig, SubtitleMode
from api import generate_video

subtitle_config = SubtitleConfig(
    mode=SubtitleMode.SENTENCE,
    base_color=(200, 200, 200),
    vertical_align="center",
)

generate_video(
    json_file="output/run_001/output_moviepy.json",
    audio_file="output/run_001/output_moviepy.wav",
    output_video="output/run_001/output_video.mp4",
    width=1920,
    height=1080,
    fps=30,
    subtitle_config=subtitle_config,
)
```

Optional custom components:

```python
from subtitle.source import JsonSubtitleSource
from subtitle.layouts import SentenceLayout
from subtitle.renderer import PillowSubtitleRenderer

generate_video(
    ...,
    subtitle_config=subtitle_config,
    subtitle_source=JsonSubtitleSource("/path/to/custom.json"),
    layout=SentenceLayout(),
    renderer=PillowSubtitleRenderer(),
)
```

Or use `renderer.create_video(config, subtitle_source=..., layout=..., renderer=...)` with the full config dict and the same optional injections.

## Dependency injection

All subtitle components are injected via constructors or function arguments:

- `main.py` gets config and calls `create_video(cfg)` (or you call `generate_video(..., subtitle_config=..., layout=...)`).
- `create_video` builds `SubtitleConfig`, `JsonSubtitleSource`, mode-based layout, and `PillowSubtitleRenderer`, then constructs `SubtitleFrameComposer` and passes it to MoviePy as the frame generator.
- You can replace any of source, layout, or renderer with your own implementations of the interfaces without changing the rest of the pipeline.
