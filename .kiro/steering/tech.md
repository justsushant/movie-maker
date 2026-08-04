---
inclusion: always
---

# Tech Stack

## Language

- **Python 3.10** — the Makefile defaults to `python3.10`; type hints with `from __future__ import annotations` are used throughout

## Core Dependencies

| Package      | Min Version | Role                                              |
|-------------|-------------|----------------------------------------------------|
| kokoro      | ≥ 0.9.4     | Text-to-speech engine with word-level timestamps   |
| soundfile   | latest       | Reading and writing WAV audio files                |
| moviepy     | latest       | Video composition, audio/video muxing, MP4 export  |
| pillow      | latest       | Drawing subtitle text onto frames                  |
| numpy       | latest       | Audio sample arrays and video frame arrays         |
| opencv-python | latest    | Image transforms (crop, resize, blur), color space conversions, spatial effects |
| scipy       | latest       | Easing curve interpolation, signal smoothing for camera shake |
| librosa     | latest (optional) | Audio analysis for Phase 3 (beats, onsets, energy, spectral features) |

## Development & Testing

| Tool       | Role                          |
|-----------|-------------------------------|
| pytest    | Test runner                   |
| hypothesis | Property-based testing framework for correctness properties |
| Make      | Task runner (`setup`, `run`, `test-stress`, `clean`) |

## Build & Packaging

- **No pyproject.toml or setup.py** — the project is not packaged for distribution; dependencies are managed via `requirements.txt`
- Virtual environment lives in `.venv/` and is created with `make setup`

## Key Technical Constraints

- Kokoro TTS must be available in the environment (GPU recommended for speed, CPU works but is slower)
- MoviePy writes intermediate frames in memory; large videos at high resolution may require significant RAM
- OpenCV is required for video engine spatial transforms and effects
- Librosa is optional for Phase 3 audio-reactive features; system degrades gracefully without it
- The project has no web framework - library tool only

## Video Engine Technical Details

### Frame Format
- All frames are numpy arrays with shape `(height, width, 3)` and dtype `uint8`
- Color space is RGB (not BGR like OpenCV's default)
- Frames are processed in-place when possible to minimize memory allocation

### Performance Characteristics (Phase 1)
- Frame rendering at 1080p: ~2-3ms per frame without effects
- Frame rendering at 4K: ~10-20ms per frame without effects
- Image loader cache provides >10x speedup on repeated loads
- Effect chains add overhead proportional to number of effects

### Testing Strategy
- **Property-based tests**: Use hypothesis to validate universal correctness properties (36 properties defined in Phase 2 design)
- **Unit tests**: Validate specific examples and edge cases
- **Integration tests**: Validate end-to-end pipeline functionality
- **Visual regression tests**: Compare rendered frames against reference images
- **Performance tests**: Benchmark frame rendering and effect overhead
