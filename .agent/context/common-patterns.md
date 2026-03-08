---
inclusion: always
---

# Common Patterns

## Implementation Patterns Used in PRISM

### 1. Dependency Injection Pattern

#### Description
Pass dependencies through constructor rather than creating them inside classes.

#### Example
```python
from tts.itts_engine import ITTSEngine
from io_adapters import IAudioWriter, IMetadataWriter

class TTSPipeline:
    def __init__(
        self,
        tts_engine: ITTSEngine,
        audio_writer: IAudioWriter,
        metadata_writer: IMetadataWriter
    ):
        self.tts_engine = tts_engine
        self.audio_writer = audio_writer
        self.metadata_writer = metadata_writer

    def process(self):
        # Use injected dependencies
        audio, timestamps = self.tts_engine.generate("text")
        self.audio_writer.write(audio)
        self.metadata_writer.write(timestamps)
```

#### Benefits
- Easy to test with mock dependencies
- Flexible configuration
- Clear dependencies

### 2. Strategy Pattern

#### Description
Interchangeable algorithms or behaviors via interfaces.

#### Example: Subtitle Layouts
```python
from subtitle.interfaces import ISubtitleLayout
from subtitle.layouts import SentenceLayout, WordHighlightLayout

class SubtitleFrameComposer:
    def __init__(self, source, layout: ISubtitleLayout, renderer):
        self.layout = layout  # Any ISubtitleLayout implementation

    def render_subtitle(self, frame, timestamp):
        segments = self.source.get_segments(timestamp)
        layout_strategy = self.layout.get_layout_strategy(segments)
        # Use strategy to position text
        return self.renderer.render(frame, layout_strategy)

# Usage with different strategies
composer1 = SubtitleFrameComposer(source, SentenceLayout(config), renderer)
composer2 = SubtitleFrameComposer(source, WordHighlightLayout(config), renderer)
```

#### Benefits
- Easy to add new strategies
- Swap behavior at runtime
- Test each strategy independently

### 3. Protocol/Duck Typing Pattern

#### Description
Use protocols (or duck typing) for function signatures.

#### Example: Effect Functions
```python
from typing import Protocol

class EffectFunction(Protocol):
    def __call__(
        self,
        frame: np.ndarray,
        t: float,
        progress: float
    ) -> np.ndarray:
        ...

# Any function matching this signature works
def custom_effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
    return frame * progress

# Class-based effect
class CustomClassEffect:
    def __call__(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        return frame * progress
```

#### Benefits
- Flexible function signatures
- Mix functions and classes
- Type checking with mypy

### 4. Builder Pattern

#### Description
Construct complex objects step by step.

#### Example: Scene DSL
```python
from engine.scene import Scene, ImageClip, Transition, TransitionType

scene = (Scene(fps=30, width=1920, height=1080)
    .add_clip(ImageClip(path="img1.jpg", duration=5.0))
    .add_clip(ImageClip(path="img2.jpg", duration=5.0))
    .add_transition(Transition(TransitionType.CROSSFADE, 1.0))
    .build())
```

#### Benefits
- Clear object construction
- Readable code
- Optional parameters

### 5. Pipeline Pattern

#### Description
Process data through a series of stages.

#### Example: Text Processing Pipeline
```python
from processing.punctuation import PunctuationMerger
from processing.grouping import SentenceGrouper

def process_text(tokens):
    # Stage 1: Merge punctuation
    tokens = PunctuationMerger().merge(tokens)
    
    # Stage 2: Group into sentences
    segments = SentenceGrouper().group(tokens)
    
    return segments
```

#### Benefits
- Clear data flow
- Easy to add stages
- Each stage is testable

### 6. Adapter Pattern

#### Description
Convert interface of a class into another interface.

#### Example: I/O Adapters
```python
from io_adapters import IAudioWriter

class FileAudioWriter(IAudioWriter):
    def __init__(self, path: str):
        self.path = path
    
    def write(self, audio_data: np.ndarray):
        import soundfile as sf
        sf.write(self.path, audio_data, 24000)

class InMemoryAudioWriter(IAudioWriter):
    def __init__(self):
        self.data = None
    
    def write(self, audio_data: np.ndarray):
        self.data = audio_data
```

#### Benefits
- Swap implementations easily
- Test with in-memory versions
- Add new I/O backends

### 7. Factory Pattern

#### Description
Create objects without specifying exact class.

#### Example: Configuration Factory
```python
from config import Config, SubtitleConfig

def get_config() -> Config:
    return Config(
        fps=30,
        width=1920,
        height=1080,
        subtitle_config=SubtitleConfig(
            font_size=48,
            font_color=(255, 255, 255)
        )
    )

def get_test_config() -> Config:
    return Config(
        fps=10,  # Faster for tests
        width=640,
        height=480,
        subtitle_config=SubtitleConfig(
            font_size=24,
            font_color=(255, 255, 255)
        )
    )
```

#### Benefits
- Centralized object creation
- Easy to change configuration
- Separate test config

### 8. Template Method Pattern

#### Description
Define algorithm skeleton, let subclasses override steps.

#### Example: Pipeline Base Class
```python
class PipelineBase:
    def process(self):
        # Template method - defines steps
        input_data = self.read_input()
        processed_data = self.process_data(input_data)
        self.write_output(processed_data)
    
    def read_input(self):
        raise NotImplementedError
    
    def process_data(self, data):
        raise NotImplementedError
    
    def write_output(self, data):
        raise NotImplementedError

class TTSPipeline(PipelineBase):
    def read_input(self):
        return self.text_reader.read()
    
    def process_data(self, text):
        return self.tts_engine.generate(text)
    
    def write_output(self, audio):
        self.audio_writer.write(audio)
```

#### Benefits
- Reuse algorithm structure
- Customize specific steps
- Consistent behavior

### 9. Decorator Pattern

#### Description
Add behavior to objects dynamically.

#### Example: Effect Chain
```python
from engine.effects import brightness, contrast, vignette

clip = ImageClip(
    path="image.jpg",
    duration=5.0,
    effects=[
        lambda f, t, p: brightness(f, t, p, factor=1.2),  # Decorator 1
        lambda f, t, p: contrast(f, t, p, factor=1.1),    # Decorator 2
        lambda f, t, p: vignette(f, t, p, intensity=0.3), # Decorator 3
    ]
)

# Effects are applied in order
```

#### Benefits
- Composable behavior
- Add/remove effects easily
- Each effect is independent

### 10. Observer Pattern

#### Description
Notify subscribers of changes.

#### Example: Frame Rendering
```python
class FrameRenderer:
    def __init__(self, timeline, observers=None):
        self.timeline = timeline
        self.observers = observers or []
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def render_frame(self, t):
        frame = self._generate_frame(t)
        
        # Notify all observers
        for observer in self.observers:
            observer.on_frame_rendered(frame, t)
        
        return frame

class ProgressObserver:
    def on_frame_rendered(self, frame, t):
        print(f"Rendered frame at t={t}")
```

#### Benefits
- Decouple components
- Add observers dynamically
- Event-driven architecture

## Testing Patterns

### 1. Test Fixture Pattern

#### Description
Setup common test data with fixtures.

#### Example
```python
import pytest
import numpy as np

@pytest.fixture
def sample_frame():
    return np.ones((100, 100, 3), dtype=np.uint8) * 128

@pytest.fixture
def sample_scene():
    return Scene(
        clips=[ImageClip(path="test.jpg", duration=2.0)],
        fps=30,
        width=640,
        height=480
    )

def test_effect(sample_frame):
    result = brightness(sample_frame, t=0, progress=0.5, factor=1.5)
    assert result.shape == sample_frame.shape
```

### 2. Property-Based Testing Pattern

#### Description
Test properties that should hold for all inputs.

#### Example
```python
from hypothesis import given, strategies as st

@given(
    frame=st.builds(
        lambda size: np.random.randint(0, 255, (size, size, 3), dtype=np.uint8),
        size=st.integers(min_value=10, max_value=100)
    ),
    factor=st.floats(min_value=0.5, max_value=2.0)
)
def test_brightness_property(frame, factor):
    result = brightness(frame, t=0, progress=0.5, factor=factor)
    
    # Property: output shape matches input
    assert result.shape == frame.shape
    
    # Property: output dtype matches input
    assert result.dtype == frame.dtype
```

### 3. Mock Dependency Pattern

#### Description
Use mocks to isolate components.

#### Example
```python
from unittest.mock import Mock

def test_pipeline_with_mock_tts():
    # Mock TTS engine
    mock_tts = Mock(spec=ITTSEngine)
    mock_tts.generate.return_value = (audio_data, timestamps)
    
    # Create pipeline with mock
    pipeline = TTSPipeline(
        tts_engine=mock_tts,
        audio_writer=mock_writer,
        metadata_writer=mock_metadata_writer
    )
    
    # Process
    pipeline.process()
    
    # Verify TTS was called
    mock_tts.generate.assert_called_once()
```

## Error Handling Patterns

### 1. Graceful Degradation Pattern

#### Description
Fall back to simpler behavior if advanced features unavailable.

#### Example: Audio Analysis
```python
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

class AudioAnalyzer:
    def __init__(self, audio_path):
        if not LIBROSA_AVAILABLE:
            # Fall back to no-op behavior
            self.features = {}
            return
        
        # Normal path with librosa
        self.audio, self.sr = librosa.load(audio_path)
        self.features = self._analyze()
```

### 2. Validation Pattern

#### Description
Validate inputs early with clear errors.

#### Example
```python
def validate_frame(frame: np.ndarray) -> None:
    if frame.ndim != 3:
        raise ValueError(f"Frame must be 3D, got {frame.ndim}D")
    
    if frame.shape[2] != 3:
        raise ValueError(f"Frame must have 3 channels, got {frame.shape[2]}")
    
    if frame.dtype != np.uint8:
        raise ValueError(f"Frame must be uint8, got {frame.dtype}")

def process_frame(frame: np.ndarray):
    validate_frame(frame)
    # Process frame...
```

## Performance Patterns

### 1. Caching Pattern

#### Description
Store expensive computations for reuse.

#### Example: Image Loader Cache
```python
class ImageLoader:
    def __init__(self):
        self.cache = {}
    
    def load(self, path: str) -> np.ndarray:
        if path in self.cache:
            return self.cache[path]
        
        # Load image (expensive)
        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Cache it
        self.cache[path] = image
        return image
```

### 2. Vectorization Pattern

#### Description
Use numpy vectorized operations instead of loops.

#### Example
```python
# Slow - Python loop
def slow_brightness(frame, factor):
    result = np.zeros_like(frame)
    for i in range(frame.shape[0]):
        for j in range(frame.shape[1]):
            for k in range(frame.shape[2]):
                result[i, j, k] = min(255, frame[i, j, k] * factor)
    return result

# Fast - Vectorized
def fast_brightness(frame, factor):
    return np.clip(frame * factor, 0, 255).astype(np.uint8)
```

### 3. Generator Pattern

#### Description
Use generators for memory-efficient iteration.

#### Example
```python
def render_frames(timeline, start_t, end_t, fps):
    dt = 1.0 / fps
    t = start_t
    while t < end_t:
        yield render_single_frame(timeline, t)
        t += dt

# Use without loading all frames into memory
for frame in render_frames(timeline, 0, 10, 30):
    process_frame(frame)
```

## Architectural Patterns

### 1. Layered Architecture

#### Description
Separate concerns into layers.

#### Example: PRISM Architecture
```
┌─────────────────────────────────┐
│     Presentation Layer          │  (CLI, API)
├─────────────────────────────────┤
│     Business Logic Layer        │  (Pipeline, Processing)
├─────────────────────────────────┤
│     Data Layer                  │  (TTS, I/O Adapters)
├─────────────────────────────────┤
│     Infrastructure Layer        │  (Engine, Rendering)
└─────────────────────────────────┘
```

### 2. Modular Architecture

#### Description
Separate into independent modules.

#### Example: PRISM Modules
```
prism/
├── tts/          # Text-to-speech
├── subtitle/     # Subtitle system
├── engine/       # Video engine
├── pipeline/     # Orchestration
├── processing/   # Text processing
└── rendering/    # Video composition
```

### 3. Plugin Architecture

#### Description
Allow extensions via plugins.

#### Example: Subtitle Layouts
```python
# Plugin interface
class ISubtitleLayout(Protocol):
    def get_layout_strategy(self, segments):
        ...

# Built-in plugins
subtitle.layouts.SentenceLayout
subtitle.layouts.WordHighlightLayout

# Custom plugin
class CustomLayout:
    def get_layout_strategy(self, segments):
        # Custom logic
        pass

# Register and use
composer = SubtitleFrameComposer(source, CustomLayout(), renderer)
```

## SOLID Principles in Practice

### Single Responsibility Principle
- Each class has one reason to change
- Example: `KokoroTTSEngine` only generates TTS

### Open/Closed Principle
- Open for extension, closed for modification
- Example: Add new TTS engines via `ITTSEngine` interface

### Liskov Substitution Principle
- Subtypes must be substitutable
- Example: Any `ITTSEngine` can replace `KokoroTTSEngine`

### Interface Segregation Principle
- Clients depend only on interfaces they use
- Example: `ITextReader` has only `read()` method

### Dependency Inversion Principle
- Depend on abstractions, not concretions
- Example: Pipeline depends on `ITTSEngine`, not `KokoroTTSEngine`
