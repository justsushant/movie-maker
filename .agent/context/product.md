---
inclusion: always
---

# Product Overview

## Purpose

PRISM generates narrated videos with word-by-word karaoke-style subtitle highlighting over image sequences with motion effects and transitions. Users provide plain text and images, and the pipeline produces a finished MP4 with synced TTS audio, animated subtitles, and professional visual effects — no manual editing required.

## Target Users

- Content creators who need quick narrated video generation from scripts and images
- Developers integrating automated video narration into larger workflows via the Python API
- Video producers who want to add motion and transitions to static images

## Key Features

### Audio & Subtitles
- **Text-to-Speech with word-level timestamps** — powered by Kokoro TTS, producing natural speech with precise per-word timing data
- **Multiple subtitle modes** — sentence, word-only, sentence-with-word-highlight, and stacking layouts to suit different video styles
- **Configurable appearance** — font sizes, colors, margins, vertical alignment, and overflow strategies are all adjustable through a single config dictionary

### Video Engine (Phases 1-3 Complete)
- **Image-based video composition** — stitch multiple images into a timeline with configurable durations
- **Motion effects** — Ken Burns zoom, pan (left/right/up/down), zoom in/out with smooth easing
- **Transitions** — crossfades, slides, wipes, iris, and animated transitions between clips with optional beat synchronization
- **Visual effects** — color grading (brightness, contrast, saturation), vignettes, film grain
- **Audio-reactive effects** (Phase 3) — visual effects driven by audio analysis (onset flashes, energy-driven zoom/brightness/shake, spectral color shifts)
- **Beat synchronization** (Phase 3) — transitions can snap to musical beats for rhythm-aligned editing
- **Scene DSL** — declarative Python API for describing video compositions with optional audio integration

### Integration
- **Programmatic API** — `api.generate_video()` accepts pre-generated audio, subtitle JSON, and Scene objects for integration into external pipelines
- **CLI pipeline** — single `make run` command reads `files/input.txt` and outputs a complete video to a timestamped directory

## Pipeline Flow

1. **TTS** — Kokoro converts input text into speech audio and word-level timestamps
2. **Punctuation merging** — punctuation tokens are merged into adjacent words for clean display
3. **Sentence grouping** — words are grouped into subtitle segments by sentence boundaries or ~5-second chunks
4. **Audio Analysis** (Phase 3, optional) — If Scene includes audio, librosa analyzes beats, onsets, energy, and spectral features
5. **Scene Planning** — Scene DSL is resolved into a timeline with clip timings, camera paths, transition overlaps, and optional beat-synced transitions
6. **Frame Rendering** — For each frame:
   - Video engine generates base frame from image with motion effects
   - Effects are applied (color grading, vignettes, grain, audio-reactive effects)
   - During transitions, two clips are blended using transition functions
   - Subtitles are composited on top with word highlighting
7. **Encoding** — MoviePy writes final MP4 with synced audio

## Design Goals

- Keep the pipeline simple and reproducible — one config dict drives the entire run
- Each run writes to its own timestamped `output/run_YYYYMMDD_HHMMSS/` directory so previous results are never overwritten
- The subtitle system is modular (source → layout → renderer) so individual components can be swapped without touching the rest of the pipeline
- The video engine uses pure functions (transitions, effects) for easy testing and composition
- Audio-reactive effects follow a class-based pattern with graceful degradation when audio is unavailable
- Declarative Scene DSL hides complexity — users describe what they want, not how to render it
- Backward compatibility — videos without Scene objects use solid-color backgrounds (original behavior); audio features are optional and degrade gracefully
