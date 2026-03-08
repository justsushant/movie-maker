---
inclusion: always
---

# Project Structure

## Directory Layout

```
prism/
├── main.py                  # CLI entry point — orchestrates full TTS → video pipeline
├── api.py                   # Programmatic API — generate_video() for external callers
├── config.py                # Central configuration — get_config() / get_test_config()
├── tts_pipeline.py          # Kokoro TTS wrapper — speech generation + subtitle extraction
├── renderer.py              # Video builder — assembles frames with subtitles via MoviePy
├── subtitle_config.py       # SubtitleConfig dataclass and SubtitleMode enum
├── requirements.txt         # pip dependencies
├── Makefile                 # Task runner (setup, run, test-stress, clean)
│
├── engine/                  # Video engine — image composition with motion and effects
│   ├── __init__.py
│   ├── scene.py             # Scene DSL: Scene, ImageClip, Transition, MotionPreset, TransitionType, BeatSync
│   ├── easing.py            # Easing functions: linear, cubic variants, ease-in/out
│   ├── camera.py            # VirtualCamera, Rect, motion presets (Ken Burns, pan, zoom)
│   ├── planner.py           # ScenePlanner: resolves Scene into ResolvedTimeline with timings and audio analysis
│   ├── renderer.py          # FrameRenderer: generates frames from timeline with effects
│   ├── image_loader.py      # ImageLoader: loads and caches images as numpy arrays
│   ├── transitions.py       # Transition functions: crossfade, slides, wipes, iris, animated
│   ├── effects.py           # Effect functions: color grading, vignettes, film grain, audio-reactive effects
│   └── audio/               # Audio analysis module (Phase 3)
│       ├── __init__.py
│       ├── analyzer.py      # AudioAnalyzer: librosa-based audio feature extraction
│       └── sync.py          # AudioSync: maps audio features to video timeline
│
├── subtitle/                # Modular subtitle pipeline
│   ├── __init__.py
│   ├── interfaces.py        # Protocols & ABCs: ISubtitleSource, ISubtitleLayout, ISubtitleRenderer
│   ├── source.py            # JsonSubtitleSource — reads subtitle JSON produced by TTS
│   ├── composer.py          # SubtitleFrameComposer — wires source → layout → renderer
│   ├── layouts.py           # Layout strategies: Sentence, Word, WordHighlight, Stacking
│   └── renderer.py          # PillowSubtitleRenderer — draws positioned text onto PIL images
│
├── files/
│   └── input.txt            # User-provided narration text (pipeline input)
│
├── output/                  # Generated outputs (gitignored)
│   └── run_YYYYMMDD_HHMMSS/ # Each run gets its own timestamped directory
│       ├── output_moviepy.json
│       ├── output_moviepy.wav
│       ├── output_moviepy_word.srt
│       └── output_video.mp4
│
├── tests/
│   ├── conftest.py          # Pytest fixtures (project_root, fixture_text_dir, test_output_root)
│   ├── run_tests.sh         # Shell wrapper: activates venv, runs pytest
│   ├── test_subtitle_stress.py  # Parametrized stress tests across resolutions and modes
│   ├── fixtures/
│   │   ├── text/            # Test input files (short_single_sentence.txt, long_paragraph.txt, …)
│   │   ├── images/          # Test images for video engine (landscape, portrait, square, various formats)
│   │   └── audio/           # Test audio files for Phase 3 (synthetic beats, onsets, speech)
│   │
│   ├── Video Engine Tests (Phase 1 Complete):
│   │   ├── test_scene_dsl.py           # Scene, ImageClip, MotionPreset tests
│   │   ├── test_easing.py              # Easing function tests + property tests
│   │   ├── test_camera.py              # VirtualCamera, Rect, interpolation tests
│   │   ├── test_motion_presets.py      # Motion preset tests (Ken Burns, pan, zoom)
│   │   ├── test_image_loader.py        # Image loading, caching, format tests
│   │   ├── test_planner.py             # Scene planning, timeline resolution tests
│   │   ├── test_renderer.py            # Frame rendering tests
│   │   ├── test_integration_engine.py  # End-to-end pipeline tests
│   │   ├── test_visual_regression.py   # Visual consistency tests
│   │   ├── test_subtitle_overlay_integration.py  # Subtitle + engine integration
│   │   ├── test_library_api_scene.py   # API integration tests
│   │   ├── test_end_to_end.py          # Complete TTS + engine tests
│   │   ├── test_error_handling.py      # Error handling tests
│   │   └── test_performance.py         # Performance benchmarks
│   │
│   ├── Video Engine Tests (Phase 2 Complete):
│   │   ├── test_transitions.py         # Transition function tests
│   │   ├── test_effects.py             # Effect function tests
│   │   ├── test_planner_phase2.py      # Phase 2 planning tests
│   │   ├── test_renderer_phase2.py     # Phase 2 rendering tests
│   │   ├── test_phase2_integration.py  # Phase 2 integration tests
│   │   ├── test_error_handling_phase2.py  # Phase 2 error handling
│   │   └── test_backward_compatibility_phase2.py  # Backward compatibility tests
│   │
│   └── Video Engine Tests (Phase 3 Complete):
│       ├── test_audio_analyzer.py      # AudioAnalyzer unit tests
│       ├── test_audio_sync.py          # AudioSync unit tests
│       ├── test_planner_audio.py       # Audio analysis integration tests
│       ├── test_beat_sync.py           # Beat synchronization tests
│       ├── test_audio_effects.py       # Audio-reactive effect tests
│       ├── test_phase3_integration.py  # Phase 3 end-to-end tests
│       └── test_phase3_graceful_degradation.py  # Graceful degradation tests
│
└── docs/
    ├── how_it_works.md          # Technical pipeline walkthrough
    ├── subtitles.md             # Subtitle configuration and Python API reference
    └── video_engine_plan.md     # Video engine roadmap (Phases 1-6)
```

## Architecture: Video Engine + Subtitle System

### Video Engine Pipeline (Phases 1-3 Complete)

```
Scene DSL (with Audio) → ScenePlanner → Audio Analysis (optional) → ResolvedTimeline → FrameRenderer → Base Frames
                                              ↓                              ↓
                                         AudioSync                   Audio-Reactive Effects
                                                                            ↓
                                                                  SubtitleFrameComposer
                                                                            ↓
                                                                    Final Frames → MP4
```

**Data Flow:**
1. **Scene Definition**: User creates Scene with ImageClips, MotionPresets, and optional audio
2. **Audio Analysis** (Phase 3, optional): If audio provided, analyze beats, onsets, energy, spectral features
3. **Planning**: ScenePlanner resolves clip timings, computes camera paths, applies beat synchronization
4. **Frame Rendering**: For each frame at time t:
   - Identify active clip(s)
   - Load source image(s) (with caching)
   - Compute camera viewport using easing-interpolated path
   - Apply crop + resize transform
   - Apply effects (color grading, vignettes, grain, audio-reactive effects)
   - During transitions, blend two clips using transition functions
   - Return numpy array as base frame
5. **Subtitle Overlay**: SubtitleFrameComposer receives base frame and adds text
6. **Encoding**: MoviePy writes final video with audio

### Subtitle System (Unchanged)

The subtitle system follows a three-stage pipeline with injectable components:

1. **Source** (`ISubtitleSource`) — provides subtitle segments for a given timestamp
2. **Layout** (`ISubtitleLayout`) — converts segments into positioned text boxes with coordinates and colors
3. **Renderer** (`ISubtitleRenderer`) — draws positioned text onto a PIL image

`SubtitleFrameComposer` in `subtitle/composer.py` wires these together and is the single object the video renderer calls per frame.

### Phase 2 Architecture (Complete)

Phase 2 adds transitions and effects:

```
Scene DSL (with Transitions & Effects) → ScenePlanner → ResolvedTimeline (with TransitionRegions)
                                                                ↓
                                                        FrameRenderer
                                                                ↓
                                            Transition Region? ─┬─ No → Render Single Clip + Effects
                                                                │
                                                                └─ Yes → Render Both Clips + Effects
                                                                         → Blend with Transition Function
                                                                         → Blended Frame
                                                                ↓
                                                    SubtitleFrameComposer → Final Frame
```

**Key Concepts:**
- **Transitions**: Pure functions `(frame_a, frame_b, progress) -> frame` that blend two clips
- **Effects**: Pure functions `(frame, t, progress) -> frame` that transform a single frame (Phase 2) or class-based with AudioSync (Phase 3)
- **Effect Chain**: Effects apply sequentially per clip before transition blending
- **Transition Regions**: Time intervals where two clips overlap and require blending

### Phase 3 Architecture (Complete)

Phase 3 adds audio analysis and audio-reactive effects:

```
Scene DSL (with Audio) → ScenePlanner → Audio Analysis → AudioSync → ResolvedTimeline
                                              ↓
                                    Beats, Onsets, Energy, Spectral Features
                                              ↓
                                        FrameRenderer
                                              ↓
                                    Audio-Reactive Effects Query AudioSync
                                              ↓
                                    OnsetFlash, OnsetZoomPulse, EnergyZoom,
                                    EnergyBrightness, EnergyShake, SpectralColorShift
                                              ↓
                                        Final Frame
```

**Key Concepts:**
- **Audio Analysis**: Librosa extracts beats, onsets, energy envelope, spectral centroid from audio
- **AudioSync**: Maps audio features to video timeline with interpolation
- **Beat Synchronization**: Transitions can snap to musical beats (NONE, NEAREST_BEAT, BEAT_GRID)
- **Audio-Reactive Effects**: Class-based effects that query AudioSync at render time
- **Graceful Degradation**: All audio features are optional; system works without librosa or audio files

## Import Patterns

- Standard library imports first, then third-party, then local modules — follow PEP 8 grouping
- Use `from __future__ import annotations` at the top of modules that use forward references
- Use `TYPE_CHECKING` guards for imports only needed by type checkers (e.g., `from PIL import Image`)
- Video engine modules use numpy arrays (HxWx3 uint8) as the standard frame format

