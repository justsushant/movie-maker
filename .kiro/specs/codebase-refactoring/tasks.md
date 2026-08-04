# Implementation Plan: Codebase Refactoring

## Overview

This implementation plan breaks down the KokoroMoviePy refactoring into discrete, testable tasks. The refactoring follows a bottom-up approach: first establishing core abstractions and data models, then building processing components, and finally wiring everything together through the pipeline orchestrator and library API.

The plan prioritizes incremental progress with frequent checkpoints to ensure the system remains functional throughout the refactoring process.

## Tasks

- [x] 1. Create core data models and TTS interfaces
  - [x] 1.1 Create tts/ module directory structure
    - Create `tts/__init__.py`
    - Create `tts/interfaces.py` for core abstractions
    - Create `tts/config.py` for TTS configuration
    - _Requirements: 2.1, 2.2, 2.3, 4.1_

  - [x] 1.2 Implement TTSToken and TTSResult data classes
    - Define `TTSToken` dataclass with text, whitespace, start_ts, end_ts fields
    - Define `TTSResult` dataclass with audio, sample_rate, tokens fields
    - Add type hints using `from __future__ import annotations`
    - _Requirements: 2.2, 2.3_

  - [x] 1.3 Define ITTSEngine interface
    - Create abstract base class `ITTSEngine` with `generate()` method
    - Document the interface contract in docstrings
    - _Requirements: 2.1, 2.2, 2.3, 9.4_

  - [x] 1.4 Implement TTSConfig dataclass
    - Define fields: lang_code, voice, speed with defaults
    - Add `from_dict()` class method for backward compatibility
    - _Requirements: 4.1, 4.6_

  - [x] 1.5 Write unit tests for TTSConfig
    - Test default values
    - Test from_dict() conversion
    - Test field validation
    - _Requirements: 6.4_

- [x] 2. Implement KokoroTTSEngine
  - [x] 2.1 Create KokoroTTSEngine class implementing ITTSEngine
    - Create `tts/kokoro_engine.py`
    - Implement constructor accepting TTSConfig
    - Initialize KPipeline with config parameters
    - _Requirements: 2.4, 9.5_

  - [x] 2.2 Implement generate() method
    - Extract paragraph splitting logic from existing code
    - Convert Kokoro tokens to TTSToken format
    - Handle time offset calculation for multiple paragraphs
    - Return TTSResult with audio and tokens
    - _Requirements: 2.4, 2.6, 3.7_

  - [x] 2.3 Write unit tests for KokoroTTSEngine
    - Test single paragraph generation
    - Test multi-paragraph generation with time offsets
    - Test token conversion accuracy
    - _Requirements: 6.1_

- [x] 3. Create text processing components
  - [x] 3.1 Create processing/ module directory
    - Create `processing/__init__.py`
    - Create `processing/models.py` for data models
    - Create `processing/punctuation.py` for punctuation merging
    - Create `processing/grouping.py` for sentence grouping
    - _Requirements: 3.1, 3.2_

  - [x] 3.2 Implement WordToken dataclass
    - Define fields: text, clean_word, start_time, end_time
    - Add to `processing/models.py`
    - _Requirements: 3.3, 3.4_

  - [x] 3.3 Implement SentenceSegment dataclass
    - Define fields: sentence_text, start_time, end_time, words
    - Add to `processing/models.py`
    - _Requirements: 3.4_

  - [x] 3.4 Implement PunctuationMerger class
    - Extract punctuation detection logic from existing code
    - Implement merge() method accepting List[TTSToken]
    - Return List[WordToken] with punctuation merged
    - _Requirements: 3.1, 3.3, 3.5, 3.7_

  - [x] 3.5 Write unit tests for PunctuationMerger
    - Test merging trailing punctuation
    - Test standalone punctuation handling
    - Test empty input
    - Test words without punctuation
    - _Requirements: 6.2_

  - [x] 3.6 Implement SentenceGrouper class
    - Extract sentence detection logic from existing code
    - Implement constructor with max_duration parameter
    - Implement group() method accepting List[WordToken]
    - Return List[SentenceSegment]
    - _Requirements: 3.2, 3.4, 3.6, 3.7_

  - [x] 3.7 Write unit tests for SentenceGrouper
    - Test sentence boundary detection (periods, question marks, exclamation points)
    - Test duration-based splitting
    - Test last word handling
    - Test empty input
    - _Requirements: 6.3_

- [x] 4. Checkpoint - Verify core components
  - Ensure all tests pass for data models and processing components
  - Verify type hints are correct with mypy (if available)
  - Ask the user if questions arise

- [x] 5. Create configuration classes
  - [x] 5.1 Implement VideoConfig dataclass
    - Create `config/video_config.py`
    - Define fields: width, height, fps, bg_color with defaults
    - Add from_dict() class method
    - _Requirements: 4.2, 4.6_

  - [x] 5.2 Implement IOConfig dataclass
    - Create `config/io_config.py`
    - Define fields for all input/output paths
    - Add from_dict() class method
    - _Requirements: 4.3, 4.6_

  - [x] 5.3 Write unit tests for VideoConfig and IOConfig
    - Test default values
    - Test from_dict() conversion
    - Test path handling in IOConfig
    - _Requirements: 6.4_

- [x] 6. Create I/O abstractions
  - [x] 6.1 Create io/ module directory
    - Create `io/__init__.py`
    - Create `io/interfaces.py` for I/O interfaces
    - Create `io/implementations.py` for concrete implementations
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 6.2 Define ITextReader interface
    - Create abstract base class with read() method
    - _Requirements: 5.1, 9.4_

  - [x] 6.3 Implement FileTextReader and StringTextReader
    - FileTextReader reads from Path
    - StringTextReader reads from string (for testing)
    - _Requirements: 5.4, 5.6_

  - [x] 6.4 Define IAudioWriter interface
    - Create abstract base class with write() method accepting audio array and sample rate
    - _Requirements: 5.2, 9.4_

  - [x] 6.5 Implement FileAudioWriter and InMemoryAudioWriter
    - FileAudioWriter uses soundfile to write WAV
    - InMemoryAudioWriter stores in memory (for testing)
    - _Requirements: 5.4, 5.6, 5.7_

  - [x] 6.6 Define IMetadataWriter interface
    - Create abstract base class with write() method accepting List[SentenceSegment]
    - _Requirements: 5.3, 9.4_

  - [x] 6.7 Implement JsonMetadataWriter and InMemoryMetadataWriter
    - JsonMetadataWriter writes to JSON file with existing format
    - InMemoryMetadataWriter stores in memory (for testing)
    - Preserve hierarchical structure: sentences with nested words
    - _Requirements: 1.4, 5.4, 5.6, 5.7_

  - [x] 6.8 Write unit tests for I/O abstractions
    - Test FileTextReader with sample files
    - Test StringTextReader with various inputs
    - Test FileAudioWriter output format
    - Test InMemoryAudioWriter storage
    - Test JsonMetadataWriter JSON structure
    - Test InMemoryMetadataWriter storage
    - _Requirements: 6.5_

- [x] 7. Checkpoint - Verify configuration and I/O
  - Ensure all configuration classes work correctly
  - Verify I/O abstractions can read/write as expected
  - Ensure all tests pass
  - Ask the user if questions arise

- [x] 8. Implement pipeline orchestrator
  - [x] 8.1 Create TTSPipeline class
    - Create `pipeline/orchestrator.py`
    - Define constructor accepting all component dependencies
    - Use dependency injection for all components
    - _Requirements: 2.5, 9.5_

  - [x] 8.2 Implement process() method
    - Chain TTS generation → punctuation merging → sentence grouping
    - Write audio and metadata using provided writers
    - Return List[SentenceSegment]
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 8.3 Write unit tests for TTSPipeline
    - Use mock implementations of all dependencies
    - Test complete pipeline flow
    - Test error handling
    - Verify correct method calls on dependencies
    - _Requirements: 6.6_

- [x] 9. Create library API
  - [x] 9.1 Implement generate_video_from_text() function
    - Create `api/library.py`
    - Accept text, output_dir, and optional config objects
    - Instantiate all pipeline components with configs
    - Call TTSPipeline.process()
    - Call video renderer with results
    - Return Path to generated video
    - _Requirements: 1.3, 4.5, 8.1_

  - [x] 9.2 Implement generate_video_from_file() function
    - Accept input_file path instead of text string
    - Read file content and delegate to generate_video_from_text()
    - _Requirements: 1.3, 5.1_

  - [x] 9.3 Write integration tests for library API
    - Test generate_video_from_text() with sample text
    - Test generate_video_from_file() with test fixtures
    - Verify output files are created
    - Compare output with baseline (if available)
    - _Requirements: 6.6, 7.2_

- [x] 10. Update existing code to use new architecture
  - [x] 10.1 Refactor main.py to use new library API
    - Replace direct TTS calls with generate_video_from_file()
    - Maintain existing CLI behavior
    - Preserve timestamped output directory creation
    - _Requirements: 1.2, 4.7, 8.1_

  - [x] 10.2 Update api.py to use new library API
    - Refactor generate_video() to use new components
    - Maintain backward compatibility with existing parameters
    - _Requirements: 1.3, 1.6, 4.7_

  - [x] 10.3 Update renderer.py if needed
    - Ensure renderer works with new JSON format (should be unchanged)
    - Update imports if module structure changed
    - _Requirements: 1.1, 1.4_

  - [x] 10.4 Deprecate or remove old tts_pipeline.py
    - Mark MoviePySubtitleExtractor as deprecated
    - Add migration notes in docstring
    - Consider keeping for one version with deprecation warning
    - _Requirements: 1.6, 4.7_

- [x] 11. Checkpoint - Verify integration
  - Run existing integration tests (test_subtitle_stress.py)
  - Verify all tests pass with new architecture
  - Test CLI with `make run`
  - Compare output with baseline
  - Ensure all tests pass
  - Ask the user if questions arise

- [x] 12. Update documentation
  - [x] 12.1 Update docs/how_it_works.md
    - Document new architecture with component diagram
    - Explain TTS abstraction and processing pipeline
    - Update code examples to use new API
    - _Requirements: 8.5_

  - [x] 12.2 Create docs/architecture.md
    - Document SOLID principles applied
    - Explain dependency injection pattern
    - Show component interaction diagrams
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 12.3 Update README if needed
    - Update installation instructions if dependencies changed
    - Update usage examples to show new API
    - Add migration guide for existing users
    - _Requirements: 1.6_

- [x] 13. Performance validation
  - [x] 13.1 Run performance benchmarks
    - Measure video generation time before and after refactoring
    - Measure memory usage before and after refactoring
    - Document results
    - _Requirements: 10.1, 10.2_

  - [x] 13.2 Profile for bottlenecks
    - Use cProfile or similar to identify any new bottlenecks
    - Optimize if necessary
    - _Requirements: 10.3_

- [x] 14. Final checkpoint - Complete refactoring
  - Ensure all integration tests pass
  - Verify CLI works correctly with `make run`
  - Verify programmatic API works correctly
  - Confirm no performance regressions
  - Ensure all documentation is updated
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster completion
- Each task references specific requirements for traceability
- The refactoring follows a bottom-up approach: data models → components → orchestration → integration
- Checkpoints ensure the system remains functional throughout the refactoring
- Unit tests are optional but highly recommended for long-term maintainability
- Integration tests are critical and should be run at each checkpoint
- The existing subtitle system (source → layout → renderer) is not modified in this refactoring
- Backward compatibility is maintained throughout to avoid breaking existing users
