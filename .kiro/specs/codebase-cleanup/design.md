# Design Document: Codebase Cleanup

## Overview

This design outlines a phased approach to cleaning up the KokoroMoviePy codebase by removing deprecated code, debug artifacts, and obsolete documentation. The cleanup is structured in four phases to minimize risk and ensure the codebase remains functional throughout the process.

The cleanup addresses technical debt accumulated during the refactoring from a monolithic architecture to a modular pipeline-based architecture. The new architecture uses:
- Modular packages: `tts/`, `processing/`, `pipeline/`
- New configuration classes: `TTSConfig`, `VideoConfig`, `SubtitleConfig`
- New library API: `api.library.generate_video_from_text()` and `api.library.generate_video_from_file()`

The cleanup will remove:
- 5 debug scripts used during development
- 3 bug analysis markdown documents
- Deprecated `tts_pipeline.py` module and its tests
- Legacy `api.legacy.py` module and its tests
- Legacy `config.py` module after CLI refactoring

## Architecture

### Cleanup Phases

The cleanup is organized into four sequential phases, each with specific goals and validation steps:

**Phase 1: Remove Debug Scripts and Analysis Documents**
- Target: Development artifacts with zero production dependencies
- Risk: Minimal (no code imports these files)
- Validation: Test suite continues to pass

**Phase 2: Remove Deprecated TTS Pipeline**
- Target: `tts_pipeline.py` and related tests
- Risk: Low (replaced by `tts/` package)
- Validation: Verify no imports reference the old module

**Phase 3: Remove Legacy API**
- Target: `api/legacy.py` and backward compatibility tests
- Risk: Medium (external users may depend on this)
- Validation: Ensure new API provides equivalent functionality

**Phase 4: Refactor CLI and Remove Legacy Config**
- Target: `config.py` module
- Risk: Medium (CLI currently depends on this)
- Validation: CLI behavior remains unchanged

### Dependency Analysis

Current dependency graph:
```
main.py
  ├─> config.py (legacy, to be removed)
  ├─> tts.config.TTSConfig (new)
  ├─> config.video_config.VideoConfig (new)
  ├─> subtitle_config.SubtitleConfig (new)
  └─> api.library.generate_video_from_file (new)

api/__init__.py
  ├─> api.library.* (new, keep)
  └─> api.legacy.generate_video (deprecated, to be removed)

tts_pipeline.py (deprecated, to be removed)
  └─> No production code imports this
```

After cleanup:
```
main.py
  ├─> tts.config.TTSConfig
  ├─> config.video_config.VideoConfig
  ├─> subtitle_config.SubtitleConfig
  └─> api.library.generate_video_from_file

api/__init__.py
  └─> api.library.* (only new API)
```

## Components and Interfaces

### Phase 1: File Deletion (Debug Scripts and Docs)

**Files to Delete:**
- `debug_audio_duration.py`
- `debug_renderer_width.py`
- `debug_subtitle_rendering.py`
- `debug_subtitle_rendering2.py`
- `debug_timestamp_issue.py`
- `BUG_ANALYSIS.md`
- `SUBTITLE_BUG_ANALYSIS.md`
- `CLEANUP_ANALYSIS.md`

**Validation:**
- Run `pytest` to ensure no tests reference these files
- Check for any imports (should be none)

### Phase 2: Deprecated TTS Pipeline Removal

**Files to Delete:**
- `tts_pipeline.py`
- `tests/test_tts_pipeline.py`
- `tests/test_tts_pipeline_deprecation.py`

**Validation Steps:**
1. Search codebase for `import tts_pipeline` or `from tts_pipeline`
2. Verify `tts/` package provides all needed functionality
3. Run full test suite

**Replacement Mapping:**
- Old: `tts_pipeline.MoviePySubtitleExtractor`
- New: `tts.engine.KokoroEngine` + `processing.punctuation_merger.PunctuationMerger` + `processing.sentence_grouper.SentenceGrouper`

### Phase 3: Legacy API Removal

**Files to Delete:**
- `api/legacy.py`
- `tests/test_api_backward_compatibility.py`

**Files to Modify:**
- `api/__init__.py`: Remove `generate_video` import and export

**Current `api/__init__.py` exports:**
```python
__all__ = [
    "generate_video_from_text",    # Keep
    "generate_video_from_file",    # Keep
    "generate_video",              # Remove (legacy)
    "TTSConfig",                   # Keep
    "VideoConfig",                 # Keep
    "SubtitleConfig",              # Keep
    "SubtitleMode",                # Keep
]
```

**After cleanup:**
```python
__all__ = [
    "generate_video_from_text",
    "generate_video_from_file",
    "TTSConfig",
    "VideoConfig",
    "SubtitleConfig",
    "SubtitleMode",
]
```

### Phase 4: CLI Refactoring and Legacy Config Removal

**Current CLI Flow (main.py):**
1. Import `config.py` using `importlib.util` to avoid naming conflict
2. Call `config_py.get_config()` to get legacy config dict
3. Convert dict to new config objects using `.from_dict()` methods
4. Pass config objects to `generate_video_from_file()`

**New CLI Flow:**
1. Define default configuration values directly in `main.py`
2. Construct `TTSConfig`, `VideoConfig`, `SubtitleConfig` objects directly
3. Pass config objects to `generate_video_from_file()`

**Configuration Defaults:**

The CLI needs to maintain these default values (currently in `config.py`):

```python
# TTS Configuration
voice = "af_sky"
speed = 1.0
lang = "en-us"

# Video Configuration
resolution = (1920, 1080)
fps = 30
background_color = (0, 0, 0)

# Subtitle Configuration
mode = SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT
font_size = 48
sentence_color = (255, 255, 255)
highlight_color = (255, 255, 0)
margin = 50
vertical_position = "bottom"
```

**Refactored `main.py` Structure:**
```python
from pathlib import Path
from datetime import datetime
from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle_config import SubtitleConfig, SubtitleMode
from api.library import generate_video_from_file

def get_default_tts_config() -> TTSConfig:
    """Return default TTS configuration for CLI."""
    return TTSConfig(
        voice="af_sky",
        speed=1.0,
        lang="en-us"
    )

def get_default_video_config() -> VideoConfig:
    """Return default video configuration for CLI."""
    return VideoConfig(
        resolution=(1920, 1080),
        fps=30,
        background_color=(0, 0, 0)
    )

def get_default_subtitle_config() -> SubtitleConfig:
    """Return default subtitle configuration for CLI."""
    return SubtitleConfig(
        mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
        font_size=48,
        sentence_color=(255, 255, 255),
        highlight_color=(255, 255, 0),
        margin=50,
        vertical_position="bottom"
    )

def create_run_directory() -> Path:
    """Create timestamped output directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path("output") / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir

def run_pipeline():
    """Run the full TTS → video pipeline."""
    # Configuration
    input_file = Path("files/input.txt")
    run_dir = create_run_directory()
    
    tts_config = get_default_tts_config()
    video_config = get_default_video_config()
    subtitle_config = get_default_subtitle_config()
    
    # Generate video
    video_path = generate_video_from_file(
        input_file=input_file,
        output_dir=run_dir,
        tts_config=tts_config,
        video_config=video_config,
        subtitle_config=subtitle_config
    )
    
    # Generate SRT (CLI-specific feature)
    generate_srt(run_dir / "output_moviepy.json", run_dir / "output_moviepy_word.srt")
    
    print(f"Done! Video: {video_path}")

def main():
    run_pipeline()

if __name__ == "__main__":
    main()
```

**Files to Delete After Refactoring:**
- `config.py`

**Validation:**
- Run `make run` and verify video generation works
- Run `python main.py` directly and verify it works
- Check that output files are created in timestamped directory
- Verify no other files import `config.py`

## Data Models

### Configuration Objects

The cleanup consolidates configuration into three dataclasses:

**TTSConfig** (defined in `tts/config.py`):
```python
@dataclass
class TTSConfig:
    voice: str = "af_sky"
    speed: float = 1.0
    lang: str = "en-us"
```

**VideoConfig** (defined in `config/video_config.py`):
```python
@dataclass
class VideoConfig:
    resolution: tuple[int, int] = (1920, 1080)
    fps: int = 30
    background_color: tuple[int, int, int] = (0, 0, 0)
```

**SubtitleConfig** (defined in `subtitle_config.py`):
```python
@dataclass
class SubtitleConfig:
    mode: SubtitleMode
    font_size: int
    sentence_color: tuple[int, int, int]
    highlight_color: tuple[int, int, int]
    margin: int
    vertical_position: str
```

### File Deletion Tracking

For validation purposes, we track which files are deleted in each phase:

```python
Phase1Files = [
    "debug_audio_duration.py",
    "debug_renderer_width.py",
    "debug_subtitle_rendering.py",
    "debug_subtitle_rendering2.py",
    "debug_timestamp_issue.py",
    "BUG_ANALYSIS.md",
    "SUBTITLE_BUG_ANALYSIS.md",
    "CLEANUP_ANALYSIS.md",
]

Phase2Files = [
    "tts_pipeline.py",
    "tests/test_tts_pipeline.py",
    "tests/test_tts_pipeline_deprecation.py",
]

Phase3Files = [
    "api/legacy.py",
    "tests/test_api_backward_compatibility.py",
]

Phase4Files = [
    "config.py",
]
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: File Deletion Completeness

*For any* file in the cleanup phase's deletion list, after executing that cleanup phase, the file should not exist in the filesystem.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1, 4.2, 6.1**

### Property 2: No Broken Imports After Deletion

*For any* deleted Python module, after cleanup, no Python files in the codebase should contain import statements referencing that module.

**Validates: Requirements 3.4, 6.2, 7.5**

### Property 3: Test Suite Integrity After Cleanup

*For any* cleanup phase, after completing that phase, running `pytest` should pass all tests with exit code 0.

**Validates: Requirements 1.6, 3.5, 4.6, 6.3, 7.1**

### Property 4: CLI Functional Equivalence

*For any* valid input text file, after refactoring the CLI, running `python main.py` should produce the same output files (audio, JSON, SRT, MP4) with equivalent content as before the refactoring.

**Validates: Requirements 5.4, 5.5, 6.4, 7.2, 7.6**

### Property 5: API Import Stability

*For any* Python script that imports from the `api` module, after Phase 3 cleanup, attempting to import `generate_video` from `api` should raise an `ImportError`, while importing `generate_video_from_text` and `generate_video_from_file` should succeed.

**Validates: Requirements 4.3, 4.4, 4.5**

### Property 6: Configuration Object Construction

*For any* configuration parameter (voice, speed, resolution, fps, etc.), after CLI refactoring, the configuration objects constructed in `main.py` should contain the same default values as the legacy `config.py` module.

**Validates: Requirements 5.1, 5.2**

### Property 7: Output File Completeness

*For any* successful CLI execution, the timestamped output directory should contain exactly four files: `output_moviepy.wav`, `output_moviepy.json`, `output_moviepy_word.srt`, and `output_video.mp4`.

**Validates: Requirements 7.3, 7.7**

### Property 8: Library API Functionality

*For any* valid text input, after all cleanup phases, calling `api.library.generate_video_from_text()` should successfully generate a video file and return its path.

**Validates: Requirements 7.4**

## Error Handling

### File Deletion Errors

**Scenario:** A file scheduled for deletion does not exist or cannot be deleted due to permissions.

**Handling:**
- Check if file exists before attempting deletion
- If file doesn't exist, log a warning but continue (idempotent operation)
- If deletion fails due to permissions, raise an error and halt cleanup
- Provide clear error message indicating which file failed to delete

### Import Detection Errors

**Scenario:** Grep search for imports fails or produces false positives.

**Handling:**
- Use Python's AST parsing instead of regex for reliable import detection
- Parse each `.py` file and check the import statements in the AST
- Handle syntax errors in Python files gracefully (log and skip)
- Report all files that import deleted modules before proceeding with deletion

### Test Failure After Cleanup

**Scenario:** Test suite fails after a cleanup phase.

**Handling:**
- Immediately halt the cleanup process
- Report which tests failed and their error messages
- Provide rollback instructions (restore from git)
- Investigate the failure before proceeding to next phase

### CLI Behavior Change

**Scenario:** Refactored CLI produces different output than original.

**Handling:**
- Compare output files byte-by-byte (audio, video) or structurally (JSON, SRT)
- If differences detected, report what changed
- Allow for acceptable differences (timestamps, metadata) vs. unacceptable (content)
- Provide diff output for JSON and SRT files

### Missing Configuration Values

**Scenario:** Refactored CLI is missing a configuration parameter from legacy config.

**Handling:**
- Before deleting `config.py`, extract all configuration keys
- Verify each key has a corresponding parameter in new config classes
- If any keys are missing, halt and report which ones
- Ensure no configuration is lost during migration

## Testing Strategy

### Dual Testing Approach

This cleanup will use both unit tests and property-based tests:

**Unit Tests:**
- Verify specific files are deleted in each phase
- Check specific import statements are removed from `api/__init__.py`
- Verify specific configuration values in refactored `main.py`
- Test CLI execution with the default `files/input.txt`

**Property-Based Tests:**
- Generate random sets of files and verify deletion completeness
- Generate random Python code and verify import detection works correctly
- Generate random configuration values and verify they're preserved after refactoring

### Property Test Configuration

All property-based tests will:
- Use `pytest` with `hypothesis` library for property-based testing
- Run minimum 100 iterations per property test
- Tag each test with a comment referencing the design property

Example tag format:
```python
# Feature: codebase-cleanup, Property 1: File Deletion Completeness
@given(st.sampled_from(Phase1Files))
def test_file_deletion_completeness(filepath):
    ...
```

### Test Organization

```
tests/
├── test_cleanup_phase1.py          # Unit tests for Phase 1 (debug scripts)
├── test_cleanup_phase2.py          # Unit tests for Phase 2 (TTS pipeline)
├── test_cleanup_phase3.py          # Unit tests for Phase 3 (legacy API)
├── test_cleanup_phase4.py          # Unit tests for Phase 4 (CLI refactor)
├── test_cleanup_properties.py      # Property-based tests for all phases
└── test_cleanup_integration.py     # End-to-end integration tests
```

### Validation Checklist

After each phase, run this validation checklist:

**Phase 1 Validation:**
- [ ] All 8 files deleted (5 debug scripts + 3 markdown docs)
- [ ] `pytest` passes
- [ ] No grep matches for deleted filenames in codebase

**Phase 2 Validation:**
- [ ] `tts_pipeline.py` and 2 test files deleted
- [ ] No imports of `tts_pipeline` in codebase
- [ ] `pytest` passes
- [ ] `make run` works

**Phase 3 Validation:**
- [ ] `api/legacy.py` and test file deleted
- [ ] `api/__init__.py` updated correctly
- [ ] `generate_video` not in `__all__`
- [ ] `pytest` passes
- [ ] Library API imports work

**Phase 4 Validation:**
- [ ] `main.py` refactored (no config.py import)
- [ ] `config.py` deleted
- [ ] `make run` produces identical output
- [ ] `python main.py` works
- [ ] All 4 output files created
- [ ] `pytest` passes

**Final Validation:**
- [ ] All phases complete
- [ ] Full test suite passes
- [ ] CLI generates video successfully
- [ ] Library API functional
- [ ] No broken imports in codebase
- [ ] Output directory contains all expected files

### Manual Testing

In addition to automated tests, perform these manual checks:

1. **Visual Inspection:** Watch the generated video to ensure subtitles appear correctly
2. **Audio Quality:** Listen to the audio to ensure TTS quality is unchanged
3. **Timing Accuracy:** Verify subtitle highlighting is synchronized with audio
4. **File Sizes:** Compare output file sizes before/after cleanup (should be similar)
5. **Performance:** Measure video generation time before/after (should be similar)

### Regression Prevention

To prevent reintroduction of deleted code:

1. **Git Hooks:** Add pre-commit hook to reject commits containing deleted filenames
2. **CI Checks:** Add CI job to verify deleted files don't exist
3. **Documentation:** Update README to remove references to deleted files
4. **Code Review:** Require review for any new files matching deleted patterns (e.g., `debug_*.py`)
