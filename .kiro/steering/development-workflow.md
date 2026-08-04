---
inclusion: always
---

# Development Workflows

## Common Tasks and Workflows

### Setting Up Development Environment

```bash
# Create virtual environment and install dependencies
make setup

# Activate virtual environment
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

### Running the Full Pipeline

```bash
# Generate video from files/input.txt
make run

# Output goes to: output/run_YYYYMMDD_HHMMSS/
```

### Testing Workflow

```bash
# Run all tests
make test

# Run unit tests only (fast)
make test-unit

# Run integration tests (slower, requires TTS)
make test-integration

# Run stress tests
make test-stress

# Run specific test file
pytest tests/test_renderer.py -v

# Run specific test with debug output
pytest tests/test_renderer.py::test_render_frame -v -s
```

### Debugging Workflow

#### 1. Understand the Problem

- Check if there are relevant specifications in `.kiro/specs/`
- Look at existing tests for similar functionality
- Read relevant documentation in `docs/`

#### 2. Reproduce the Issue

```bash
# Run specific test that fails
pytest tests/test_failing_module.py -v

# Run with verbose output
pytest tests/ -v -s

# Check test output directory
ls tests/test_output/
```

#### 3. Isolate the Component

- Check which module is failing
- Look at the test file for clues
- Read the module's source code

#### 4. Fix the Issue

- Write the fix
- Add or update tests
- Verify tests pass

#### 5. Verify Fix

```bash
# Run related tests
pytest tests/test_related_module.py -v

# Run all tests to ensure no regressions
make test
```

### Adding a New Feature Workflow

#### Phase 1: Planning

1. **Check for existing specs**: Look in `.kiro/specs/`
2. **Read relevant docs**: `docs/video_engine.md`, `docs/architecture.md`
3. **Understand existing patterns**: Look at similar features
4. **Ask clarifying questions** if needed

#### Phase 2: Implementation

1. **Create or update spec**: If needed, create spec in `.kiro/specs/feature-name/`
2. **Implement the feature**: Follow existing patterns
3. **Write tests**: Unit tests first, then integration tests
4. **Update documentation**: Add to relevant docs in `docs/`

#### Phase 3: Verification

```bash
# Run all tests
make test

# Run specific feature tests
pytest tests/test_feature.py -v

# Check performance if applicable
pytest tests/test_performance.py -v
```

#### Phase 4: Documentation

- Update relevant documentation files
- Add examples if needed
- Update `docs/README.md` if new docs added

### Refactoring Workflow

#### 1. Identify Refactoring Target

- Look for code duplication
- Identify complex functions that could be simplified
- Check for SOLID principle violations

#### 2. Write Tests First

```bash
# Write tests for existing behavior
pytest tests/test_module_to_refactor.py -v
```

#### 3. Make Incremental Changes

- Refactor in small steps
- Run tests after each change
- Ensure no regressions

#### 4. Verify All Tests Pass

```bash
# Run all tests
make test

# Run integration tests
make test-integration
```

### Bug Fixing Workflow

#### 1. Understand the Bug

- Read the bug report or issue description
- Try to reproduce the bug
- Identify which component is affected

#### 2. Write Reproduction Test

```bash
# Write a test that reproduces the bug
# Example: pytest tests/test_bug_reproduction.py -v
```

#### 3. Debug the Issue

- Add debug prints if needed
- Use debugger or logging
- Check edge cases

#### 4. Fix the Bug

- Make minimal changes
- Ensure fix addresses root cause
- Update tests if needed

#### 5. Verify Fix

```bash
# Run reproduction test
pytest tests/test_bug_reproduction.py -v

# Run all tests
make test

# Run integration tests
make test-integration
```

#### 6. Add Regression Test

- Ensure the test stays in the test suite
- Document the bug fix

### Performance Optimization Workflow

#### 1. Profile the Code

```bash
# Profile with cProfile
python -m cProfile -o profile.stats your_script.py

# Analyze profile
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

#### 2. Identify Bottlenecks

- Look for hot spots in profiling output
- Check for unnecessary allocations
- Identify slow algorithms

#### 3. Optimize

- Use vectorized operations
- Implement caching
- Optimize algorithms

#### 4. Measure Improvement

```bash
# Run performance tests
pytest tests/test_performance.py -v

# Compare before and after
```

#### 5. Verify Correctness

```bash
# Run all tests
make test

# Run integration tests
make test-integration
```

### Code Review Workflow

#### When Reviewing Code

1. **Check correctness**: Does the code work as intended?
2. **Check tests**: Are tests comprehensive?
3. **Check style**: Does code follow project conventions?
4. **Check documentation**: Is code well-documented?
5. **Check performance**: Is performance acceptable?
6. **Check edge cases**: Are edge cases handled?

#### What to Look For

- Type hints are present and correct
- Error handling is appropriate
- Dependencies are minimal and justified
- Code follows SOLID principles
- Tests are included
- Documentation is updated

### Release Workflow

#### 1. Update Version

- Update version number in appropriate files
- Update CHANGELOG if it exists

#### 2. Run Full Test Suite

```bash
# Run all tests
make test

# Run integration tests
make test-integration

# Run stress tests
make test-stress
```

#### 3. Update Documentation

- Ensure all docs are current
- Update examples if needed
- Update README

#### 4. Create Release Notes

- Document new features
- Document bug fixes
- Document breaking changes

### Working with OpenSpec Workflow

This project uses OpenSpec for managing changes. See `.kiro/steering/product.md` for context.

#### Explore Mode

When exploring ideas or investigating problems:

```bash
# Load explore mode skill
# (This is done automatically by the skill system)
```

#### Propose Change

When describing a new feature or change:

```bash
# Load propose mode skill
# (This is done automatically by the skill system)
```

#### Apply Change

When implementing tasks from a spec:

```bash
# Load apply change skill
# (This is done automatically by the skill system)
```

#### Archive Change

When finalizing a completed change:

```bash
# Load archive change skill
# (This is done automatically by the skill system)
```

### Working with Video Engine

#### Creating a Simple Scene

```python
from engine.scene import Scene, ImageClip, MotionPreset
from config import get_config

config = get_config()

scene = Scene(
    clips=[
        ImageClip(
            path="path/to/image1.jpg",
            duration=5.0,
            motion=MotionPreset.KEN_BURNS
        ),
        ImageClip(
            path="path/to/image2.jpg",
            duration=5.0,
            motion=MotionPreset.ZOOM_IN
        ),
    ],
    fps=config.fps,
    width=config.width,
    height=config.height
)
```

#### Adding Effects

```python
from engine.scene import ImageClip
from engine.effects import (
    brightness,
    contrast,
    saturation,
    vignette
)

clip = ImageClip(
    path="path/to/image.jpg",
    duration=5.0,
    motion=MotionPreset.PAN_LEFT,
    effects=[
        lambda frame, t, p: brightness(frame, t, p, factor=1.2),
        lambda frame, t, p: contrast(frame, t, p, factor=1.1),
        lambda frame, t, p: saturation(frame, t, p, factor=1.3),
        lambda frame, t, p: vignette(frame, t, p, intensity=0.3),
    ]
)
```

#### Adding Transitions

```python
from engine.scene import Scene, ImageClip, Transition, TransitionType

scene = Scene(
    clips=[
        ImageClip(
            path="image1.jpg",
            duration=5.0,
            motion=MotionPreset.KEN_BURNS
        ),
        ImageClip(
            path="image2.jpg",
            duration=5.0,
            motion=MotionPreset.ZOOM_IN
        ),
    ],
    transitions=[
        Transition(
            type=TransitionType.CROSSFADE,
            duration=1.0
        ),
    ],
    fps=30,
    width=1920,
    height=1080
)
```

#### Adding Audio-Reactive Effects

```python
from engine.scene import Scene, ImageClip
from engine.effects import (
    OnsetFlash,
    EnergyZoom,
    EnergyBrightness
)
from engine.audio.analyzer import AudioAnalyzer
import librosa

# Load and analyze audio
audio_path = "path/to/audio.wav"
y, sr = librosa.load(audio_path, sr=24000)
analyzer = AudioAnalyzer(y, sr)
audio_features = analyzer.analyze()

clip = ImageClip(
    path="image.jpg",
    duration=5.0,
    motion=MotionPreset.KEN_BURNS,
    effects=[
        OnsetFlash(intensity=0.5),
        EnergyZoom(scale=1.2),
        EnergyBrightness(factor=1.3),
    ],
    audio=audio_features
)
```

### Working with Subtitle System

#### Creating a Subtitle Renderer

```python
from subtitle.composer import SubtitleFrameComposer
from subtitle.source import JsonSubtitleSource
from subtitle.layouts import WordHighlightLayout
from subtitle.renderer import PillowSubtitleRenderer
from config import get_config

config = get_config()

# Create components
source = JsonSubtitleSource("path/to/subtitle.json")
layout = WordHighlightLayout(config)
renderer = PillowSubtitleRenderer(config)

# Compose
composer = SubtitleFrameComposer(source, layout, renderer)

# Render frame with subtitle at timestamp
frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
timestamp = 2.5
frame_with_subtitle = composer.render_subtitle(frame, timestamp)
```

#### Using Different Layouts

```python
from subtitle.layouts import (
    SentenceLayout,
    WordOnlyLayout,
    WordHighlightLayout,
    StackingLayout
)

# Sentence-level subtitles
layout1 = SentenceLayout(config)

# Word-only subtitles
layout2 = WordOnlyLayout(config)

# Word-by-word highlighting
layout3 = WordHighlightLayout(config)

# Stacking subtitles
layout4 = StackingLayout(config)
```

### Working with TTS

#### Using the TTS Pipeline

```python
from pipeline.ttspipeline import TTSPipeline
from tts.kokoro_tts import KokoroTTSEngine, TTSConfig
from io_adapters import (
    InMemoryTextReader,
    FileAudioWriter,
    FileMetadataWriter
)
from config import get_config

config = get_config()

# Create components
tts_engine = KokoroTTSEngine(TTSConfig())
text_reader = InMemoryTextReader("Your text here")
audio_writer = FileAudioWriter("output/audio.wav")
metadata_writer = FileMetadataWriter("output/metadata.json")

# Create and run pipeline
pipeline = TTSPipeline(
    tts_engine=tts_engine,
    text_reader=text_reader,
    audio_writer=audio_writer,
    metadata_writer=metadata_writer
)

# Process text
result = pipeline.process()
```

### Troubleshooting Workflow

#### Issue: Tests Failing

1. Check test output for error messages
2. Look at test code to understand what's being tested
3. Run individual test with verbose output
4. Check if dependencies are installed correctly

#### Issue: Performance Problems

1. Profile the code to identify bottlenecks
2. Check for unnecessary allocations
3. Look for opportunities to use caching
4. Consider vectorizing operations

#### Issue: Memory Issues

1. Check resolution settings
2. Reduce number of concurrent operations
3. Check for memory leaks
4. Consider processing in chunks

#### Issue: TTS Not Working

1. Check if Kokoro is installed
2. Verify Kokoro model files are available
3. Check GPU availability if using GPU acceleration
4. Test with simple text first

#### Issue: Video Output Issues

1. Check frame format (should be RGB, not BGR)
2. Verify dimensions are correct
3. Check for memory issues
4. Verify MoviePy installation

### Getting Help Workflow

When you need help:

1. **Check existing documentation**: Look in `docs/`
2. **Check similar code**: Look at existing implementations
3. **Check tests**: Test files often show usage examples
4. **Ask specific questions**: Be clear about what you need

### Clean Up Workflow

```bash
# Clean output directory
make clean

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Clean test outputs
rm -rf tests/test_output/*

# Clean virtual environment (be careful!)
rm -rf .venv/
```
