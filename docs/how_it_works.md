# How It Works — Technical Deep Dive

This document explains the full pipeline from text input to final video output, covering the new modular architecture, data flow, key algorithms, and the dependency injection pattern.

## Architecture Overview

KokoroMoviePy follows a **layered, modular architecture** with clear separation of concerns. The refactored codebase uses dependency injection throughout, making components testable, swappable, and maintainable.

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Library API                            │
│                   (api/library.py)                          │
│  • generate_video_from_text()                               │
│  • generate_video_from_file()                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                Pipeline Orchestrator                        │
│               (pipeline/orchestrator.py)                    │
│                   TTSPipeline                               │
└─┬───────────────┬───────────────┬───────────────┬──────────┘
  │               │               │               │
  ▼               ▼               ▼               ▼
┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│   TTS   │  │   Text   │  │   I/O    │  │    Video     │
│ Engine  │  │Processing│  │ Writers  │  │  Renderer    │
└─────────┘  └──────────┘  └──────────┘  └──────────────┘
     │            │              │              │
     ▼            ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│ITTSEngine│ │Punctuation│ │IAudioWriter│ │   Subtitle   │
│         │  │  Merger  │  │IMetadata │  │    System    │
│Kokoro   │  │Sentence  │  │  Writer  │  │ (modular)    │
│Engine   │  │ Grouper  │  │          │  │              │
└─────────┘  └──────────┘  └──────────┘  └──────────────┘
```

### Key Architectural Principles

1. **Dependency Injection**: Components receive dependencies through constructors, not by importing concrete implementations
2. **Interface Segregation**: Small, focused interfaces (ITTSEngine, IAudioWriter, IMetadataWriter) that clients depend on
3. **Single Responsibility**: Each class has one clear purpose (e.g., PunctuationMerger only merges punctuation)
4. **Open/Closed**: New TTS engines or I/O implementations can be added without modifying existing code
5. **Testability**: All components can be tested in isolation using mock implementations

---

## Pipeline Flow

The complete pipeline follows these stages:

```
Input Text
    │
    ▼
┌─────────────────────────────────────────┐
│  Stage 1: TTS Generation                │
│  (ITTSEngine → KokoroTTSEngine)         │
│                                         │
│  • Split text into paragraphs           │
│  • Generate audio for each paragraph    │
│  • Extract word-level tokens            │
│  • Adjust timestamps across paragraphs  │
│                                         │
│  Output: TTSResult                      │
│    - audio: np.ndarray (24kHz)          │
│    - tokens: List[TTSToken]             │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Stage 2: Punctuation Merging           │
│  (PunctuationMerger)                    │
│                                         │
│  • Identify punctuation-only tokens     │
│  • Merge into preceding words           │
│  • Create clean word tokens             │
│                                         │
│  Output: List[WordToken]                │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Stage 3: Sentence Grouping             │
│  (SentenceGrouper)                      │
│                                         │
│  • Group words by sentence boundaries   │
│  • Split on punctuation (. ! ?)         │
│  • Split on duration limit (5 seconds)  │
│  • Preserve word-level timing           │
│                                         │
│  Output: List[SentenceSegment]          │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Stage 4: Output Writing                │
│  (IAudioWriter, IMetadataWriter)        │
│                                         │
│  • Write audio to WAV file              │
│  • Write subtitle JSON with hierarchy   │
│                                         │
│  Output: .wav, .json files              │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Stage 5: Video Rendering               │
│  (renderer.py + subtitle system)        │
│                                         │
│  • Load audio and subtitle JSON         │
│  • Generate frames with subtitles       │
│  • Highlight current word               │
│  • Export to MP4                        │
│                                         │
│  Output: .mp4 video                     │
└─────────────────────────────────────────┘
```

---

## Stage 1: TTS Generation (ITTSEngine)

### Interface Abstraction

The `ITTSEngine` interface defines the contract for all TTS engines:

```python
class ITTSEngine(ABC):
    @abstractmethod
    def generate(self, text: str) -> TTSResult:
        """Generate speech audio and word-level timing data."""
        pass
```

This abstraction allows swapping TTS engines without modifying downstream components. Want to use a different TTS provider? Just implement `ITTSEngine`.

### Kokoro Implementation

`KokoroTTSEngine` implements the interface using the Kokoro TTS library:

```python
from tts.interfaces import ITTSEngine, TTSResult, TTSToken
from tts.config import TTSConfig

class KokoroTTSEngine(ITTSEngine):
    def __init__(self, config: TTSConfig):
        self._config = config
        self._pipeline = KPipeline(lang_code=config.lang_code)
    
    def generate(self, text: str) -> TTSResult:
        # Split into paragraphs
        paragraphs = re.split(r'\n+', text.strip())
        
        audio_segments = []
        all_tokens = []
        
        for paragraph in paragraphs:
            # Generate audio for this paragraph
            generator = self._pipeline(
                paragraph,
                voice=self._config.voice,
                speed=self._config.speed
            )
            
            # Collect audio and tokens
            paragraph_audio = []
            paragraph_tokens = []
            
            for result in generator:
                paragraph_audio.append(result.audio.cpu().numpy())
                paragraph_tokens.extend(result.tokens)
            
            # Calculate time offset for this paragraph
            time_offset = sum(len(seg) for seg in audio_segments) / 24000
            
            # Convert to our token format with adjusted timestamps
            for token in paragraph_tokens:
                if token.start_ts is not None and token.end_ts is not None:
                    all_tokens.append(TTSToken(
                        text=token.text,
                        whitespace=token.whitespace,
                        start_ts=token.start_ts + time_offset,
                        end_ts=token.end_ts + time_offset
                    ))
            
            if paragraph_audio:
                audio_segments.append(np.concatenate(paragraph_audio))
        
        # Combine all audio
        audio = np.concatenate(audio_segments) if audio_segments else np.array([])
        
        return TTSResult(audio=audio, sample_rate=24000, tokens=all_tokens)
```

### Key Features

- **Multi-paragraph handling**: Each paragraph is processed separately, with timestamps adjusted to maintain global continuity
- **Token filtering**: Tokens with `None` timestamps (special characters) are skipped
- **24kHz audio**: Kokoro outputs at 24,000 Hz sample rate

### Output: TTSToken

```python
@dataclass
class TTSToken:
    text: str          # "The"
    whitespace: str    # " "
    start_ts: float    # 0.225
    end_ts: float      # 0.325
```

---

## Stage 2: Punctuation Merging

### The Problem

Kokoro TTS sometimes emits punctuation as standalone tokens:

```
["Wait", ",", "\"", " ", "he", "said", "."]
```

If left as-is, the video would try to highlight a comma by itself, which looks broken.

### The Solution: PunctuationMerger

```python
class PunctuationMerger:
    def merge(self, tokens: List[TTSToken]) -> List[WordToken]:
        merged_words = []
        
        for token in tokens:
            text_content = token.text.strip()
            is_punctuation = not bool(re.search(r'[a-zA-Z0-9]', text_content))
            
            if is_punctuation and merged_words:
                # Append to previous word
                merged_words[-1].text += token.text + token.whitespace
            else:
                # Start new word
                merged_words.append(WordToken(
                    text=token.text + token.whitespace,
                    clean_word=text_content,
                    start_time=token.start_ts,
                    end_time=token.end_ts
                ))
        
        return merged_words
```

### Algorithm

1. For each token, check if it contains alphanumeric characters
2. If it's punctuation-only AND there's a previous word → append to previous word
3. Otherwise → create a new word token

### Before and After

**Before merging:**
```
["Wait", ",", "\"", " ", "he"]  ← 5 separate tokens
```

**After merging:**
```
["Wait,\" ", "he"]  ← 2 clean words
```

### Output: WordToken

```python
@dataclass
class WordToken:
    text: str          # "Wait,\" "
    clean_word: str    # "Wait,\""
    start_time: float  # 0.225
    end_time: float    # 0.450
```

---

## Stage 3: Sentence Grouping

### The Problem

Words need to be grouped into sentence-sized chunks for subtitle display. Each sentence becomes one "line" shown on screen.

### The Solution: SentenceGrouper

```python
class SentenceGrouper:
    def __init__(self, max_duration: float = 5.0):
        self._max_duration = max_duration
    
    def group(self, words: List[WordToken]) -> List[SentenceSegment]:
        sentences = []
        current_sentence_words = []
        start_time = words[0].start_time
        
        for i, word in enumerate(words):
            current_sentence_words.append(word)
            current_end_time = word.end_time
            
            # Check end conditions
            is_sentence_end = bool(re.search(r'[.!?](\s+)?$', word.text))
            is_duration_exceeded = (current_end_time - start_time) >= self._max_duration
            is_last_word = (i == len(words) - 1)
            
            if is_sentence_end or is_duration_exceeded or is_last_word:
                full_text = "".join(w.text for w in current_sentence_words).strip()
                
                if full_text:
                    sentences.append(SentenceSegment(
                        sentence_text=full_text,
                        start_time=start_time,
                        end_time=current_end_time,
                        words=current_sentence_words.copy()
                    ))
                
                # Reset for next sentence
                current_sentence_words = []
                if not is_last_word:
                    start_time = words[i + 1].start_time
        
        return sentences
```

### Splitting Rules (Priority Order)

1. **Sentence-ending punctuation** — split after `.`, `!`, or `?`
2. **Duration limit** — split if a sentence exceeds 5 seconds (prevents very long lines)
3. **End of input** — the last word always closes the current sentence

### Output: SentenceSegment

```python
@dataclass
class SentenceSegment:
    sentence_text: str           # "Today is a new beginning!"
    start_time: float            # 2.5
    end_time: float              # 4.8
    words: List[WordToken]       # [WordToken("Today "), WordToken("is "), ...]
```

### JSON Format

The hierarchical structure is preserved in the JSON output:

```json
{
  "sentence_text": "Today is a new beginning!",
  "start_time": 2.5,
  "end_time": 4.8,
  "words": [
    {"text": "Today ", "clean_word": "Today", "start_time": 2.5, "end_time": 2.9},
    {"text": "is ", "clean_word": "is", "start_time": 2.9, "end_time": 3.0},
    {"text": "a ", "clean_word": "a", "start_time": 3.0, "end_time": 3.1},
    {"text": "new ", "clean_word": "new", "start_time": 3.1, "end_time": 3.5},
    {"text": "beginning!", "clean_word": "beginning!", "start_time": 3.5, "end_time": 4.8}
  ]
}
```

This hierarchical structure is what makes word-highlighting possible — the renderer knows both **which sentence to display** and **which word within it to highlight**.

---

## Stage 4: I/O Abstraction

### Interface-Based Design

The refactored architecture uses interfaces for all I/O operations, enabling testing without filesystem dependencies:

```python
class IAudioWriter(ABC):
    @abstractmethod
    def write(self, audio: np.ndarray, sample_rate: int) -> None:
        pass

class IMetadataWriter(ABC):
    @abstractmethod
    def write(self, segments: List[SentenceSegment]) -> None:
        pass
```

### Implementations

**FileAudioWriter** — writes to WAV files:
```python
class FileAudioWriter(IAudioWriter):
    def __init__(self, path: Path):
        self._path = path
    
    def write(self, audio: np.ndarray, sample_rate: int) -> None:
        import soundfile as sf
        sf.write(str(self._path), audio, sample_rate)
```

**JsonMetadataWriter** — writes subtitle JSON:
```python
class JsonMetadataWriter(IMetadataWriter):
    def __init__(self, path: Path):
        self._path = path
    
    def write(self, segments: List[SentenceSegment]) -> None:
        data = [
            {
                "sentence_text": seg.sentence_text,
                "start_time": seg.start_time,
                "end_time": seg.end_time,
                "words": [
                    {
                        "text": w.text,
                        "clean_word": w.clean_word,
                        "start_time": w.start_time,
                        "end_time": w.end_time
                    }
                    for w in seg.words
                ]
            }
            for seg in segments
        ]
        
        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
```

### Testing Benefits

For tests, use in-memory implementations:

```python
class InMemoryAudioWriter(IAudioWriter):
    def __init__(self):
        self.audio = None
        self.sample_rate = None
    
    def write(self, audio: np.ndarray, sample_rate: int) -> None:
        self.audio = audio
        self.sample_rate = sample_rate
```

---

## Stage 5: Video Rendering (Modular Subtitles)

The video rendering stage uses the existing **modular subtitle system** (unchanged by the refactoring):

### Subtitle Pipeline

```
JsonSubtitleSource → Layout Strategy → PillowSubtitleRenderer
```

- **Source** (`JsonSubtitleSource`): Loads subtitle segments from JSON
- **Layout** (sentence, word-highlight, word-only, stacking): Converts segments + time into positioned text
- **Renderer** (`PillowSubtitleRenderer`): Draws positioned text onto PIL images

### Frame Generation

For each frame at time `t`:

1. `SubtitleFrameComposer` calls `source.get_segments_for_time(t)`
2. Layout strategy positions the text based on mode (e.g., sentence_with_word_highlight)
3. Renderer draws the positioned text onto the frame
4. Current word is highlighted in a different color

### Configuration

All behavior is controlled via `SubtitleConfig`:

```python
@dataclass
class SubtitleConfig:
    mode: SubtitleMode = SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT
    font_size: int = 48
    text_color: Tuple[int, int, int] = (255, 255, 255)  # White
    highlight_color: Tuple[int, int, int] = (255, 255, 0)  # Yellow
    vertical_position: str = "bottom"
    margin: int = 50
```

See **docs/subtitles.md** for complete configuration options.

---

## Pipeline Orchestrator

The `TTSPipeline` class coordinates all stages using dependency injection:

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
    
    def process(self, text: str) -> List[SentenceSegment]:
        # Stage 1: Generate TTS
        tts_result = self._tts_engine.generate(text)
        
        # Stage 2: Merge punctuation
        words = self._punctuation_merger.merge(tts_result.tokens)
        
        # Stage 3: Group into sentences
        sentences = self._sentence_grouper.group(words)
        
        # Stage 4: Write outputs
        self._audio_writer.write(tts_result.audio, tts_result.sample_rate)
        self._metadata_writer.write(sentences)
        
        return sentences
```

### Benefits of This Design

- **Testable**: Each component can be tested in isolation with mocks
- **Flexible**: Swap any component without modifying the orchestrator
- **Clear**: The process() method shows the complete pipeline flow in ~10 lines
- **Maintainable**: Each component has a single responsibility

---

## Library API

The refactored codebase provides a clean, library-first API:

### generate_video_from_text()

```python
from pathlib import Path
from api.library import generate_video_from_text
from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig

# Generate video with custom configuration
video_path = generate_video_from_text(
    text="Hello world! This is a test.",
    output_dir=Path("output/my_video"),
    tts_config=TTSConfig(voice="af_heart", speed=1.0),
    video_config=VideoConfig(width=1920, height=1080, fps=30),
    subtitle_config=SubtitleConfig(mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT)
)

print(f"Video created at: {video_path}")
```

### generate_video_from_file()

```python
from pathlib import Path
from api.library import generate_video_from_file

# Generate video from text file (uses defaults)
video_path = generate_video_from_file(
    input_file=Path("files/input.txt"),
    output_dir=Path("output/my_video")
)
```

### Configuration Classes

The new architecture uses domain-specific configuration classes instead of a single config dictionary:

**TTSConfig** — TTS engine settings:
```python
@dataclass
class TTSConfig:
    lang_code: str = "a"           # Language code
    voice: str = "af_heart"        # Voice name
    speed: float = 1.0             # Speech speed
```

**VideoConfig** — Video rendering settings:
```python
@dataclass
class VideoConfig:
    width: int = 1920
    height: int = 1080
    fps: int = 30
    bg_color: Tuple[int, int, int] = (0, 0, 0)
```

**SubtitleConfig** — Subtitle appearance (existing):
```python
@dataclass
class SubtitleConfig:
    mode: SubtitleMode = SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT
    font_size: int = 48
    text_color: Tuple[int, int, int] = (255, 255, 255)
    highlight_color: Tuple[int, int, int] = (255, 255, 0)
```

---

## Data Flow Diagram

```
files/input.txt
      │
      ▼
┌─────────────────────────────────────────┐
│  Library API                            │
│  (api/library.py)                       │
│                                         │
│  generate_video_from_file()             │
│    │                                    │
│    ▼                                    │
│  generate_video_from_text()             │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│  Pipeline Orchestrator                  │
│  (pipeline/orchestrator.py)             │
│                                         │
│  TTSPipeline.process(text)              │
│    │                                    │
│    ├─► ITTSEngine.generate()            │
│    │     └─► TTSResult                  │
│    │           (audio + tokens)         │
│    │                                    │
│    ├─► PunctuationMerger.merge()        │
│    │     └─► List[WordToken]            │
│    │                                    │
│    ├─► SentenceGrouper.group()          │
│    │     └─► List[SentenceSegment]      │
│    │                                    │
│    ├─► IAudioWriter.write()             │
│    │     └─► output_moviepy.wav         │
│    │                                    │
│    └─► IMetadataWriter.write()          │
│          └─► output_moviepy.json        │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│  Video Renderer                         │
│  (renderer.py)                          │
│                                         │
│  create_video()                         │
│    │                                    │
│    ├─► Load audio + JSON                │
│    │                                    │
│    ├─► SubtitleFrameComposer            │
│    │     │                              │
│    │     ├─► JsonSubtitleSource         │
│    │     ├─► Layout (word-highlight)    │
│    │     └─► PillowSubtitleRenderer     │
│    │                                    │
│    └─► Export to MP4                    │
│          └─► output_video.mp4           │
└─────────────────────────────────────────┘
```

---

## Why This Architecture?

| Design Choice | Reason |
|---|---|
| **Interface-based TTS** | Enables swapping TTS engines without modifying downstream code |
| **Separate processing components** | Each component (punctuation, grouping) can be tested and modified independently |
| **Dependency injection** | Components receive dependencies through constructors, making them testable with mocks |
| **Domain-specific configs** | Clear what configuration each component needs (vs. one giant config dict) |
| **I/O abstractions** | Testing without filesystem dependencies; easy to add new output formats |
| **Hierarchical JSON** | Need sentence context + per-word timing simultaneously for highlighting |
| **Pipeline orchestrator** | Single class coordinates the flow, making the process clear and maintainable |
| **Library-first API** | Clean programmatic interface with CLI as a thin wrapper |

---

## Testing Strategy

The new architecture enables comprehensive testing at multiple levels:

### Unit Tests

Each component can be tested in isolation:

```python
# Test PunctuationMerger
def test_punctuation_merger():
    tokens = [
        TTSToken("Hello", " ", 0.0, 0.5),
        TTSToken(",", "", 0.5, 0.6),
        TTSToken("world", "", 0.6, 1.0)
    ]
    
    merger = PunctuationMerger()
    words = merger.merge(tokens)
    
    assert len(words) == 2
    assert words[0].text == "Hello, "
    assert words[1].text == "world"
```

### Integration Tests

Test the complete pipeline with mock I/O:

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
    
    sentences = pipeline.process("Hello world!")
    
    assert audio_writer.audio is not None
    assert len(metadata_writer.segments) > 0
```

### End-to-End Tests

The existing `test_subtitle_stress.py` validates the complete system across different resolutions and subtitle modes.

---

## Migration from Old Architecture

The old `tts_pipeline.py` with `MoviePySubtitleExtractor` has been deprecated. The new architecture provides:

- **Better separation**: TTS, punctuation, and grouping are now separate classes
- **Testability**: Each component can be tested independently
- **Flexibility**: Swap TTS engines or I/O implementations without touching other code
- **Clarity**: The pipeline flow is explicit in `TTSPipeline.process()`

The legacy API in `api.py` has been updated to use the new components while maintaining backward compatibility.
