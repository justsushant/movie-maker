---
inclusion: always
---

# Agent Guidelines

## How to Approach This Codebase

### First Steps When Working on a Task

1. **Check for existing specifications**: Look in `.kiro/specs/` for any relevant spec documents that define the task
2. **Read context files**: Review `.kiro/steering/product.md`, `structure.md`, and `tech.md` for project context
3. **Understand the pipeline**: The codebase is organized around three major pipelines:
   - TTS pipeline (`tts/`, `pipeline/`, `processing/`)
   - Video engine (`engine/`)
   - Subtitle system (`subtitle/`)
4. **Check tests**: Look at test files in `tests/` to understand expected behavior

### Key Architectural Principles

#### SOLID Principles Applied

1. **Single Responsibility**: Each class has one clear purpose
   - Example: `KokoroTTSEngine` only generates TTS, `PunctuationMerger` only merges punctuation

2. **Open/Closed**: Open for extension via interfaces
   - New TTS engines: implement `ITTSEngine`
   - New subtitle layouts: implement `ISubtitleLayout`
   - New effects: implement `EffectFunction` protocol

3. **Liskov Substitution**: Interchangeable implementations
   - Any `ITTSEngine` can replace `KokoroTTSEngine`
   - File and in-memory writers are interchangeable

4. **Interface Segregation**: Focused, minimal interfaces
   - `ITextReader` has only `read()`
   - `IAudioWriter` has only `write()`

5. **Dependency Inversion**: Depend on abstractions
   - Pipeline depends on `ITTSEngine`, not concrete implementations
   - Use dependency injection throughout

#### Design Patterns Used

- **Strategy Pattern**: Subtitle layout strategies (`ISubtitleLayout`)
- **Adapter Pattern**: I/O adapters for different storage backends
- **Template Method**: Pipeline orchestration with `process()` method
- **Factory Pattern**: Configuration creation via `get_config()`, `get_test_config()`
- **Protocol Pattern**: Effect functions, transition functions (duck typing)

### Code Style and Conventions

#### Type Hints

- Use `from __future__ import annotations` at top of files
- Return types are required for all public functions
- Use `TYPE_CHECKING` guard for imports only needed by type checkers
- Prefer concrete types over `Any` where possible

#### Naming Conventions

- Classes: `PascalCase` (e.g., `KokoroTTSEngine`, `SubtitleFrameComposer`)
- Functions: `snake_case` (e.g., `generate_video_from_text`, `process_text`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_FPS`, `MAX_WIDTH`)
- Private methods: `_snake_case` (e.g., `_load_image`, `_compute_camera_path`)

#### Import Organization

```python
# 1. Standard library
import os
from typing import List, Optional

# 2. Third-party
import numpy as np
from PIL import Image

# 3. Local modules
from config import get_config
from engine.scene import Scene, ImageClip
```

#### Frame Format (Critical!)

- All frames are numpy arrays: `np.ndarray` with shape `(height, width, 3)` and dtype `uint8`
- Color space is **RGB** (not BGR like OpenCV's default)
- Always convert OpenCV BGR to RGB when needed: `cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)`

### Testing Expectations

#### When to Write Tests

- **Always** write tests for new features
- **Always** add tests for bug fixes (include regression test)
- **Consider** property-based tests for functions with invariants
- **Use** integration tests for multi-component workflows

#### Test Organization

- Unit tests: Test single components in isolation
- Integration tests: Test component interactions
- Property-based tests: Use hypothesis for universal properties
- Visual regression tests: Compare rendered frames against references

#### Test Fixtures

Use fixtures from `tests/conftest.py`:
- `project_root`: Project root directory path
- `test_output_root`: Output directory for tests
- `real_world_fixture_dir`: Realistic test inputs
- `technical_fixture_dir`: Edge case test inputs

#### Running Tests

```bash
# All tests
make test

# Unit tests only (fast)
make test-unit

# Integration tests (slower, requires TTS)
make test-integration

# Stress tests
make test-stress
```

### Common Workflows

#### Adding a New TTS Engine

1. Implement `ITTSEngine` interface from `tts/itts_engine.py`
2. Add configuration class extending `TTSConfig` if needed
3. Update pipeline to support new engine via dependency injection
4. Write unit tests for the new engine
5. Write integration tests with the full pipeline

#### Adding a New Motion Preset

1. Add to `MotionPreset` enum in `engine/scene.py`
2. Implement the motion logic in `engine/camera.py`
3. Add property-based tests to verify motion paths
4. Add visual regression tests for new preset

#### Adding a New Transition Type

1. Add to `TransitionType` enum in `engine/scene.py`
2. Implement transition function in `engine/transitions.py`
3. Function signature: `(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray`
4. Add tests in `tests/test_transitions.py`

#### Adding a New Effect

1. If simple/pure function: implement in `engine/effects.py` with signature `(frame: np.ndarray, t: float, progress: float) -> np.ndarray`
2. If audio-reactive: create class implementing audio-reactive pattern with AudioSync
3. Add tests in `tests/test_effects.py` or `tests/test_audio_effects.py`

#### Adding a New Subtitle Layout

1. Implement `ISubtitleLayout` from `subtitle/interfaces.py`
2. Layout strategy: `LayoutStrategy` with `get_layout_segments()` method
3. Add tests in `tests/test_subtitle_layouts.py`
4. Example: see `subtitle/layouts.py` for existing implementations

### Error Handling Patterns

#### Validation

- Validate inputs early in functions
- Raise `ValueError` for invalid arguments with descriptive messages
- Use type hints for compile-time checking

#### Graceful Degradation

- Audio features: check if librosa is available, provide fallback
- Missing dependencies: raise clear error messages
- Missing files: raise `FileNotFoundError` with path

#### Testing Errors

- Test error paths with `pytest.raises`
- Test with invalid inputs
- Test with missing dependencies

### Performance Considerations

#### Image Loading

- Use `ImageLoader` with caching for repeated loads
- Cache is thread-safe and provides >10x speedup

#### Frame Rendering

- Process frames in-place when possible to minimize allocations
- Avoid unnecessary copies of numpy arrays
- Use vectorized operations where possible

#### Memory Management

- Large videos at high resolution may require significant RAM
- Consider intermediate output for very long videos
- Use generators for processing when streaming is beneficial

### Documentation Requirements

#### Code Comments

- Add docstrings to all public classes and functions
- Include parameter types and return types in docstrings
- Document non-obvious algorithms
- Keep comments concise and focused

#### Documentation Updates

- Update relevant docs in `docs/` when adding features
- Update `docs/quick_reference.md` for new API changes
- Update `docs/README.md` index if adding new docs

### Git Workflow

#### Branch Strategy

- Main branch: `main`
- Feature branches: descriptive names like `engine-phase3-glm`, `modular-refactor`

#### Commit Guidelines

- Commit only when explicitly asked by user
- Commit messages should be concise and focus on "why" not "what"
- NEVER run `git commit --amend` unless explicitly requested and conditions are met

#### When to Commit

- Only commit when user explicitly asks
- Verify with `git status` and `git diff` before committing
- Stage relevant files with `git add`

### Module-Specific Guidelines

#### Engine Module (`engine/`)

- Use pure functions for transitions and effects when possible
- Class-based effects for audio-reactive features
- Frame format: `(H, W, 3)` uint8 RGB numpy arrays
- Camera paths use easing functions for smooth motion

#### Subtitle Module (`subtitle/`)

- Follow three-stage pipeline: source → layout → renderer
- Implement interfaces for extensibility
- Layout strategies handle positioning and coloring
- Renderer handles only drawing

#### TTS Module (`tts/`)

- Implement `ITTSEngine` for new TTS backends
- Generate word-level timestamps for subtitle sync
- Output format: 24kHz WAV + JSON with word timings

#### Pipeline Module (`pipeline/`)

- Use dependency injection for all components
- Orchestrate TTS → processing → I/O
- Keep pipeline logic simple and linear

### Debugging Tips

#### Common Issues

1. **Frame color issues**: Check if BGR vs RGB conversion needed
2. **Memory errors**: Reduce resolution or check for memory leaks
3. **Timing issues**: Verify audio timestamps match video duration
4. **Missing audio features**: Check if librosa is installed

#### Debugging Commands

```bash
# Run specific test with verbose output
pytest tests/test_renderer.py::test_render_frame -v

# Run tests and show print statements
pytest tests/ -s

# Profile performance
python -m cProfile -o profile.stats your_script.py
```

### When to Ask for Clarification

Ask when:
- Requirements are ambiguous or incomplete
- Multiple implementation approaches are possible
- Performance vs. correctness trade-offs exist
- Breaking changes might be needed
- Unsure about testing strategy

### Priorities When Working on Tasks

1. **Correctness first**: Ensure code works as specified
2. **Test coverage**: Write tests for all new code
3. **Performance**: Optimize after correctness is verified
4. **Documentation**: Update docs for new features
5. **Backward compatibility**: Avoid breaking existing functionality
