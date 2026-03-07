# Architecture Documentation

## Overview

KokoroMoviePy follows a **layered, modular architecture** built on SOLID principles and dependency injection. The refactored codebase separates concerns into distinct layers (TTS, processing, I/O, rendering) with clear interfaces between components, enabling testability, extensibility, and maintainability.

This document explains the architectural principles applied throughout the codebase, the dependency injection pattern used, and how components interact to produce narrated videos.

## SOLID Principles Applied

### 1. Single Responsibility Principle (SRP)

**Definition:** Each class should have one, and only one, reason to change.

**Application in KokoroMoviePy:**

- **`KokoroTTSEngine`**: Responsible only for TTS generation using the Kokoro library
  - Does NOT handle punctuation merging, sentence grouping, or file I/O
  - Single reason to change: Kokoro API changes

- **`PunctuationMerger`**: Responsible only for merging punctuation tokens into adjacent words
  - Does NOT handle TTS generation or sentence grouping
  - Single reason to change: punctuation merging logic changes

- **`SentenceGrouper`**: Responsible only for grouping words into sentence segments
  - Does NOT handle punctuation merging or rendering
  - Single reason to change: sentence boundary detection logic changes

- **`TTSPipeline`**: Responsible only for orchestrating the pipeline flow
  - Does NOT implement TTS, processing, or I/O logic itself
  - Single reason to change: pipeline flow changes

**Contrast with original code:** The original `MoviePySubtitleExtractor` class violated SRP by mixing TTS generation, punctuation merging, sentence grouping, and file I/O in a single class.

### 2. Open/Closed Principle (OCP)

**Definition:** Software entities should be open for extension but closed for modification.

**Application in KokoroMoviePy:**

- **Adding new TTS engines**: Create a new class implementing `ITTSEngine` without modifying existing code
  ```python
  class GoogleTTSEngine(ITTSEngine):
      def generate(self, text: str) -> TTSResult:
          # Google TTS implementation
          pass
  ```

- **Adding new I/O destinations**: Implement `IAudioWriter` or `IMetadataWriter` for new storage backends
  ```python
  class S3AudioWriter(IAudioWriter):
      def write(self, audio: np.ndarray, sample_rate: int) -> None:
          # Upload to S3
          pass
  ```

- **Adding new subtitle layouts**: The existing subtitle system already follows OCP with `ISubtitleLayout` interface

**Key insight:** Interfaces act as extension points. New implementations extend functionality without modifying the core pipeline.

### 3. Liskov Substitution Principle (LSP)

**Definition:** Objects of a superclass should be replaceable with objects of a subclass without breaking the application.

**Application in KokoroMoviePy:**

- **TTS Engine substitution**: Any `ITTSEngine` implementation can replace `KokoroTTSEngine`
  ```python
  # Both work identically in the pipeline
  engine = KokoroTTSEngine(config)
  engine = GoogleTTSEngine(config)  # Hypothetical
  
  pipeline = TTSPipeline(tts_engine=engine, ...)
  ```

- **I/O Writer substitution**: File-based and in-memory writers are interchangeable
  ```python
  # Production: write to file
  audio_writer = FileAudioWriter(path)
  
  # Testing: write to memory
  audio_writer = InMemoryAudioWriter()
  
  # Both work identically in the pipeline
  pipeline = TTSPipeline(audio_writer=audio_writer, ...)
  ```

**Contract enforcement:** All implementations must honor the interface contract:
- `ITTSEngine.generate()` must return `TTSResult` with valid audio and tokens
- `IAudioWriter.write()` must accept audio array and sample rate
- Implementations cannot add preconditions or weaken postconditions

### 4. Interface Segregation Principle (ISP)

**Definition:** Clients should not be forced to depend on interfaces they don't use.

**Application in KokoroMoviePy:**

- **Focused interfaces**: Each interface defines only the methods needed by its clients
  - `ITextReader` has only `read()` - no unnecessary write methods
  - `IAudioWriter` has only `write()` - no unnecessary read methods
  - `ITTSEngine` has only `generate()` - no configuration or lifecycle methods

- **Separate I/O interfaces**: Instead of a single `IFileHandler` with read/write methods, we have:
  - `ITextReader` for reading text
  - `IAudioWriter` for writing audio
  - `IMetadataWriter` for writing metadata
  
  This allows components to depend only on the operations they need.

**Contrast with fat interfaces:** A single `IFileHandler` interface would force read-only components to implement write methods and vice versa.

### 5. Dependency Inversion Principle (DIP)

**Definition:** High-level modules should not depend on low-level modules. Both should depend on abstractions.

**Application in KokoroMoviePy:**

- **Pipeline depends on abstractions, not concretions:**
  ```python
  class TTSPipeline:
      def __init__(
          self,
          tts_engine: ITTSEngine,          # Abstract interface
          punctuation_merger: PunctuationMerger,
          sentence_grouper: SentenceGrouper,
          audio_writer: IAudioWriter,      # Abstract interface
          metadata_writer: IMetadataWriter # Abstract interface
      ):
          # Pipeline depends on interfaces, not concrete implementations
  ```

- **Library API constructs concrete implementations:**
  ```python
  def generate_video_from_text(...):
      # Concrete implementations are created here
      tts_engine = KokoroTTSEngine(tts_config)
      audio_writer = FileAudioWriter(audio_file)
      metadata_writer = JsonMetadataWriter(json_file)
      
      # Injected into pipeline as abstractions
      pipeline = TTSPipeline(
          tts_engine=tts_engine,
          audio_writer=audio_writer,
          metadata_writer=metadata_writer,
          ...
      )
  ```

**Benefits:**
- Pipeline can be tested with mock implementations
- TTS engine can be swapped without modifying pipeline
- I/O destinations can be changed without modifying pipeline

## Dependency Injection Pattern

### What is Dependency Injection?

Dependency Injection (DI) is a design pattern where a component receives its dependencies from external sources rather than creating them internally. This inverts the control of dependency creation.

### DI in KokoroMoviePy

#### Constructor Injection

All dependencies are injected through constructors:

```python
class TTSPipeline:
    def __init__(
        self,
        tts_engine: ITTSEngine,
        punctuation_merger: PunctuationMerger,
        sentence_grouper: SentenceGrouper,
        audio_writer: IAudioWriter,
        metadata_writer: IMetadataWriter
    ):
        self._tts_engine = tts_engine
        self._punctuation_merger = punctuation_merger
        self._sentence_grouper = sentence_grouper
        self._audio_writer = audio_writer
        self._metadata_writer = metadata_writer
```

**Benefits:**
- Dependencies are explicit and visible in the constructor signature
- Immutable after construction (dependencies stored in private attributes)
- Easy to test by injecting mocks

#### Dependency Graph

```
generate_video_from_text()
    ↓ creates and injects
TTSPipeline
    ├── ITTSEngine → KokoroTTSEngine(TTSConfig)
    ├── PunctuationMerger()
    ├── SentenceGrouper()
    ├── IAudioWriter → FileAudioWriter(Path)
    └── IMetadataWriter → JsonMetadataWriter(Path)
```

#### Testing with DI

DI enables easy testing with mock implementations:

```python
def test_pipeline_flow():
    # Create mock implementations
    mock_engine = MockTTSEngine()
    mock_audio_writer = InMemoryAudioWriter()
    mock_metadata_writer = InMemoryMetadataWriter()
    
    # Inject mocks into pipeline
    pipeline = TTSPipeline(
        tts_engine=mock_engine,
        punctuation_merger=PunctuationMerger(),
        sentence_grouper=SentenceGrouper(),
        audio_writer=mock_audio_writer,
        metadata_writer=mock_metadata_writer
    )
    
    # Test pipeline without filesystem or real TTS
    result = pipeline.process("Test text")
    
    # Verify interactions
    assert mock_audio_writer.audio is not None
    assert len(mock_metadata_writer.segments) > 0
```

### Configuration Injection

Configuration objects are also injected:

```python
# TTS engine receives configuration
tts_engine = KokoroTTSEngine(tts_config)

# Configuration is injected, not hard-coded
class KokoroTTSEngine:
    def __init__(self, config: TTSConfig):
        self._config = config
        self._pipeline = KPipeline(lang_code=config.lang_code)
```

This allows:
- Different configurations for different use cases
- Testing with custom configurations
- Runtime configuration changes

## Component Interaction

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Library API                          │
│                   (api/library.py)                          │
│  • generate_video_from_text()                               │
│  • generate_video_from_file()                               │
└────────────────────┬────────────────────────────────────────┘
                     │ orchestrates
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    Pipeline Orchestrator                     │
│                  (pipeline/orchestrator.py)                  │
│                      TTSPipeline                             │
└─┬───────────┬───────────┬──────────────┬────────────────────┘
  │           │           │              │
  ↓           ↓           ↓              ↓
┌────────┐ ┌────────┐ ┌────────┐ ┌──────────────┐
│  TTS   │ │  Text  │ │  Text  │ │     I/O      │
│ Engine │ │Process │ │Process │ │   Adapters   │
│        │ │  #1    │ │  #2    │ │              │
└────────┘ └────────┘ └────────┘ └──────────────┘
    │           │           │              │
    ↓           ↓           ↓              ↓
┌────────┐ ┌────────┐ ┌────────┐ ┌──────────────┐
│Kokoro  │ │Punctua-│ │Sentence│ │ File/Memory  │
│  TTS   │ │ tion   │ │Grouper │ │   Writers    │
│ Engine │ │ Merger │ │        │ │              │
└────────┘ └────────┘ └────────┘ └──────────────┘
```

### Data Flow Diagram

```
Input Text
    ↓
┌─────────────────────────────────────────┐
│ 1. TTS Generation (ITTSEngine)          │
│    Input: str                            │
│    Output: TTSResult                     │
│      • audio: np.ndarray                 │
│      • sample_rate: int                  │
│      • tokens: List[TTSToken]            │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 2. Punctuation Merging                  │
│    Input: List[TTSToken]                 │
│    Output: List[WordToken]               │
│      • Merges punctuation into words     │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 3. Sentence Grouping                    │
│    Input: List[WordToken]                │
│    Output: List[SentenceSegment]         │
│      • Groups by punctuation/duration    │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 4. Output Writing                       │
│    • Audio → WAV file                    │
│    • Metadata → JSON file                │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 5. Video Rendering (existing system)    │
│    • Subtitle system (source/layout/    │
│      renderer)                           │
│    • MoviePy composition                 │
└─────────────────┬───────────────────────┘
                  ↓
            Output Video
```

### Sequence Diagram: Video Generation

```
User → Library API: generate_video_from_text(text, output_dir, configs)
    Library API → TTSPipeline: __init__(engine, merger, grouper, writers)
    Library API → TTSPipeline: process(text)
        TTSPipeline → ITTSEngine: generate(text)
            ITTSEngine → KokoroTTSEngine: generate(text)
                KokoroTTSEngine → Kokoro: KPipeline(text, voice, speed)
                Kokoro → KokoroTTSEngine: audio + tokens
            KokoroTTSEngine → ITTSEngine: TTSResult
        ITTSEngine → TTSPipeline: TTSResult
        
        TTSPipeline → PunctuationMerger: merge(tokens)
        PunctuationMerger → TTSPipeline: List[WordToken]
        
        TTSPipeline → SentenceGrouper: group(words)
        SentenceGrouper → TTSPipeline: List[SentenceSegment]
        
        TTSPipeline → IAudioWriter: write(audio, sample_rate)
        TTSPipeline → IMetadataWriter: write(segments)
    TTSPipeline → Library API: List[SentenceSegment]
    
    Library API → Renderer: create_video(config, subtitle_config)
        Renderer → SubtitleSystem: compose frames
        Renderer → MoviePy: render video
    Renderer → Library API: success
Library API → User: Path to video file
```

### Module Structure

```
kokoromoviepy/
├── api/                      # Library entry points
│   ├── library.py            # Main API: generate_video_from_*()
│   └── legacy.py             # Backward compatibility wrapper
│
├── tts/                      # TTS abstraction layer
│   ├── interfaces.py         # ITTSEngine, TTSToken, TTSResult
│   ├── config.py             # TTSConfig
│   └── kokoro_engine.py      # KokoroTTSEngine implementation
│
├── processing/               # Text processing components
│   ├── models.py             # WordToken, SentenceSegment
│   ├── punctuation.py        # PunctuationMerger
│   └── grouping.py           # SentenceGrouper
│
├── io_adapters/              # I/O abstraction layer
│   ├── interfaces.py         # ITextReader, IAudioWriter, IMetadataWriter
│   └── implementations.py    # File and in-memory implementations
│
├── pipeline/                 # Pipeline orchestration
│   └── orchestrator.py       # TTSPipeline
│
├── config/                   # Configuration classes
│   ├── video_config.py       # VideoConfig
│   └── io_config.py          # IOConfig
│
├── subtitle/                 # Subtitle rendering (unchanged)
│   ├── interfaces.py         # ISubtitleSource, ISubtitleLayout, ISubtitleRenderer
│   ├── source.py             # JsonSubtitleSource
│   ├── layouts.py            # Layout strategies
│   ├── renderer.py           # PillowSubtitleRenderer
│   └── composer.py           # SubtitleFrameComposer
│
├── renderer.py               # Video rendering with MoviePy
├── main.py                   # CLI entry point
└── tts_pipeline.py           # Legacy code (deprecated)
```

## Design Patterns

### 1. Strategy Pattern

**Used in:** Subtitle system

The subtitle system uses the Strategy pattern to allow different layout strategies:

```python
# Different strategies for subtitle layout
layout = SentenceLayout()           # Strategy 1
layout = WordLayout()                # Strategy 2
layout = WordHighlightLayout()      # Strategy 3

# Strategy is injected into composer
composer = SubtitleFrameComposer(source, layout, renderer)
```

### 2. Adapter Pattern

**Used in:** I/O adapters

The I/O adapters adapt different storage mechanisms to a common interface:

```python
# File system adapter
audio_writer = FileAudioWriter(path)

# Memory adapter (for testing)
audio_writer = InMemoryAudioWriter()

# Both adapt to IAudioWriter interface
```

### 3. Template Method Pattern

**Used in:** Pipeline orchestration

The `TTSPipeline.process()` method defines the algorithm skeleton:

```python
def process(self, text: str) -> List[SentenceSegment]:
    # Template method defines the algorithm structure
    tts_result = self._tts_engine.generate(text)      # Step 1
    words = self._punctuation_merger.merge(...)        # Step 2
    sentences = self._sentence_grouper.group(...)      # Step 3
    self._audio_writer.write(...)                      # Step 4
    self._metadata_writer.write(...)                   # Step 5
    return sentences
```

### 4. Factory Pattern

**Used in:** Configuration creation

Configuration classes provide factory methods for backward compatibility:

```python
# Factory method creates config from legacy dict
tts_config = TTSConfig.from_dict(legacy_config)
video_config = VideoConfig.from_dict(legacy_config)
```

## Testing Strategy

### Unit Testing

Each component is tested in isolation:

```python
# Test TTS engine independently
def test_kokoro_engine_single_paragraph():
    config = TTSConfig(voice="af_heart", speed=1.0)
    engine = KokoroTTSEngine(config)
    result = engine.generate("Hello world")
    assert result.sample_rate == 24000
    assert len(result.tokens) > 0

# Test punctuation merger independently
def test_punctuation_merger():
    tokens = [
        TTSToken("Hello", " ", 0.0, 0.5),
        TTSToken(",", " ", 0.5, 0.6),
        TTSToken("world", "", 0.6, 1.0)
    ]
    merger = PunctuationMerger()
    words = merger.merge(tokens)
    assert words[0].text == "Hello, "
    assert words[1].text == "world"
```

### Integration Testing

The pipeline is tested end-to-end with mock I/O:

```python
def test_pipeline_integration():
    # Use in-memory writers for testing
    audio_writer = InMemoryAudioWriter()
    metadata_writer = InMemoryMetadataWriter()
    
    pipeline = TTSPipeline(
        tts_engine=KokoroTTSEngine(TTSConfig()),
        punctuation_merger=PunctuationMerger(),
        sentence_grouper=SentenceGrouper(),
        audio_writer=audio_writer,
        metadata_writer=metadata_writer
    )
    
    result = pipeline.process("Hello world. This is a test.")
    
    # Verify outputs
    assert audio_writer.audio is not None
    assert len(metadata_writer.segments) >= 1
```

### Stress Testing

The existing `test_subtitle_stress.py` validates the complete system across different configurations:

```python
@pytest.mark.parametrize("resolution", [(1920, 1080), (1280, 720)])
@pytest.mark.parametrize("mode", ["sentence", "word", "sentence_with_word_highlight"])
def test_video_generation(resolution, mode):
    # Test complete pipeline with various configurations
    ...
```

## Benefits of This Architecture

### 1. Testability

- Components can be tested in isolation with unit tests
- Pipeline can be tested without filesystem using in-memory implementations
- Mock implementations enable fast, reliable tests

### 2. Extensibility

- New TTS engines can be added by implementing `ITTSEngine`
- New I/O destinations can be added by implementing writer interfaces
- New processing steps can be inserted into the pipeline

### 3. Maintainability

- Each component has a single, clear responsibility
- Changes to one component don't affect others
- Dependencies are explicit and visible

### 4. Flexibility

- TTS engine can be swapped at runtime
- I/O destinations can be configured per use case
- Configuration can be customized without code changes

### 5. Backward Compatibility

- Legacy API in `api/legacy.py` maintains compatibility
- Configuration factory methods support old config dictionaries
- Existing file formats and naming conventions preserved

## Migration from Legacy Code

### Before (Monolithic)

```python
# Old: Everything in one class
class MoviePySubtitleExtractor:
    def __init__(self, config):
        self.config = config
        self.pipeline = KPipeline(...)  # Hard-coded dependency
    
    def generate_subtitles(self, text):
        # TTS generation
        # Punctuation merging
        # Sentence grouping
        # File writing
        # All mixed together
```

### After (Modular)

```python
# New: Separated concerns with dependency injection
tts_engine = KokoroTTSEngine(tts_config)
punctuation_merger = PunctuationMerger()
sentence_grouper = SentenceGrouper()
audio_writer = FileAudioWriter(path)
metadata_writer = JsonMetadataWriter(path)

pipeline = TTSPipeline(
    tts_engine=tts_engine,
    punctuation_merger=punctuation_merger,
    sentence_grouper=sentence_grouper,
    audio_writer=audio_writer,
    metadata_writer=metadata_writer
)

result = pipeline.process(text)
```

### Key Improvements

1. **Separation of Concerns**: Each component has one responsibility
2. **Dependency Injection**: Dependencies are explicit and injectable
3. **Interface-Based Design**: Components depend on abstractions
4. **Testability**: Each component can be tested independently
5. **Extensibility**: New implementations can be added without modification

## Conclusion

The KokoroMoviePy architecture demonstrates how SOLID principles and dependency injection create a maintainable, testable, and extensible codebase. By separating concerns into focused components with clear interfaces, the system achieves:

- **Modularity**: Components can be developed, tested, and maintained independently
- **Flexibility**: Implementations can be swapped without affecting other components
- **Testability**: Unit and integration tests validate behavior at all levels
- **Extensibility**: New features can be added by implementing interfaces

This architecture serves as a foundation for future enhancements while maintaining backward compatibility with existing code.
