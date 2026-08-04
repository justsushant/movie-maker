# Requirements Document

## Introduction

This specification defines the requirements for refactoring the KokoroMoviePy codebase to improve readability, modularity, and maintainability while preserving all existing functionality. The refactoring will introduce proper abstractions for the TTS engine, improve configuration management, enhance testability, and clarify control flow throughout the pipeline.

## Glossary

- **TTS_Engine**: The text-to-speech component that converts text into audio with word-level timestamps
- **Kokoro**: The current TTS implementation (Kokoro TTS library)
- **Pipeline**: The complete flow from text input through TTS generation to video rendering
- **Subtitle_System**: The existing modular subtitle pipeline (source → layout → renderer)
- **Config_Dict**: The configuration dictionary passed throughout the system
- **JSON_Format**: The hierarchical subtitle data structure containing sentences and word-level timing
- **Integration_Test**: End-to-end test that validates the complete pipeline
- **Unit_Test**: Test that validates a single component in isolation
- **Property_Test**: Test that validates universal properties across many generated inputs

## Requirements

### Requirement 1: Preserve Existing Functionality

**User Story:** As a user of KokoroMoviePy, I want all existing features to continue working after the refactoring, so that I can upgrade without breaking my workflows.

#### Acceptance Criteria

1. WHEN the refactored code is executed, THE System SHALL produce identical video output for the same input text
2. WHEN the CLI is invoked with `make run`, THE System SHALL execute the complete pipeline as before
3. WHEN the programmatic API is called, THE System SHALL accept the same parameters and produce the same results
4. THE System SHALL maintain the existing JSON subtitle format with sentence and word-level timing data
5. THE System SHALL preserve all existing subtitle modes (sentence, word, sentence_with_word_highlight, stacking)
6. THE System SHALL maintain backward compatibility with the existing public API in api.py

### Requirement 2: TTS Engine Abstraction

**User Story:** As a developer, I want to swap TTS engines without modifying the rest of the pipeline, so that I can experiment with different TTS providers or upgrade to newer models.

#### Acceptance Criteria

1. THE System SHALL define an ITTSEngine interface that abstracts TTS operations
2. THE ITTSEngine SHALL specify a method for generating audio from text
3. THE ITTSEngine SHALL specify a method for extracting word-level timing data
4. THE System SHALL implement KokoroTTSEngine as a concrete implementation of ITTSEngine
5. WHEN a different TTS engine is provided, THE System SHALL use it without requiring changes to downstream components
6. THE KokoroTTSEngine SHALL preserve the existing JSON output format
7. THE System SHALL allow TTS engine selection through configuration or dependency injection

### Requirement 3: Separate Text Processing Concerns

**User Story:** As a developer, I want punctuation merging and sentence grouping to be separate, testable components, so that I can understand, modify, and test them independently.

#### Acceptance Criteria

1. THE System SHALL extract punctuation merging logic into a standalone component
2. THE System SHALL extract sentence grouping logic into a standalone component
3. WHEN punctuation merging is applied, THE System SHALL merge punctuation tokens into adjacent words
4. WHEN sentence grouping is applied, THE System SHALL group words into sentences based on punctuation and duration limits
5. THE Punctuation_Merger SHALL be testable in isolation with unit tests
6. THE Sentence_Grouper SHALL be testable in isolation with unit tests
7. THE System SHALL maintain the existing behavior of both operations

### Requirement 4: Improve Configuration Management

**User Story:** As a developer, I want domain-specific configuration classes instead of a single config dictionary, so that I can understand what configuration applies to each component.

#### Acceptance Criteria

1. THE System SHALL define a TTSConfig class for TTS-related settings (lang_code, voice, speed)
2. THE System SHALL define a VideoConfig class for video-related settings (width, height, fps, bg_color)
3. THE System SHALL define an IOConfig class for input/output paths
4. THE System SHALL maintain the existing SubtitleConfig class
5. WHEN configuration is propagated, THE System SHALL pass only relevant config to each component
6. THE System SHALL provide a factory function to build domain configs from the legacy config dictionary
7. THE System SHALL maintain backward compatibility with the existing config.py interface

### Requirement 5: Abstract Input/Output Operations

**User Story:** As a developer, I want file I/O operations abstracted into clear interfaces, so that I can test components without touching the filesystem and understand data flow better.

#### Acceptance Criteria

1. THE System SHALL define an ITextReader interface for reading input text
2. THE System SHALL define an IAudioWriter interface for writing audio files
3. THE System SHALL define an IMetadataWriter interface for writing JSON metadata
4. THE System SHALL implement concrete file-based implementations of these interfaces
5. WHEN components need I/O, THE System SHALL accept interfaces rather than file paths
6. THE System SHALL allow in-memory implementations for testing
7. THE System SHALL maintain the existing file output structure and naming conventions

### Requirement 6: Comprehensive Unit Testing

**User Story:** As a developer, I want unit tests for all new abstractions and extracted components, so that I can verify correctness and catch regressions early.
 
#### Acceptance Criteria

1. THE System SHALL include unit tests for the ITTSEngine interface and KokoroTTSEngine implementation
2. THE System SHALL include unit tests for punctuation merging logic
3. THE System SHALL include unit tests for sentence grouping logic
4. THE System SHALL include unit tests for configuration classes (TTSConfig, VideoConfig, IOConfig)
5. THE System SHALL include unit tests for I/O abstractions
6. WHEN unit tests are executed, THE System SHALL run them in isolation without external dependencies
7. THE System SHALL achieve at least 80% code coverage for new components

### Requirement 7: Maintain Integration Tests

**User Story:** As a developer, I want existing integration tests to continue passing, so that I can verify the complete pipeline still works correctly.

#### Acceptance Criteria

1. WHEN existing integration tests are run before refactoring, THE System SHALL record their pass/fail status as baseline
2. WHEN existing integration tests are run after refactoring, THE System SHALL produce the same pass/fail results
3. THE System SHALL preserve the test_subtitle_stress.py test suite
4. THE System SHALL preserve the pytest fixtures in conftest.py
5. THE System SHALL maintain the test output directory structure under output/test/

### Requirement 8: Improve Control Flow Clarity

**User Story:** As a developer reading the code, I want to understand the pipeline flow easily, so that I can modify or debug it efficiently.

#### Acceptance Criteria

1. THE System SHALL organize the pipeline into clear sequential stages (read → TTS → process → render)
2. WHEN reading main.py, THE Pipeline SHALL show a linear flow of operations
3. THE System SHALL eliminate deeply nested logic in favor of composed functions
4. THE System SHALL use descriptive function and variable names that reflect their purpose
5. THE System SHALL document the data flow between pipeline stages

### Requirement 9: Apply SOLID Principles

**User Story:** As a developer, I want the codebase to follow SOLID principles, so that it's easier to extend and maintain.

#### Acceptance Criteria

1. THE System SHALL follow the Single Responsibility Principle (each class has one reason to change)
2. THE System SHALL follow the Open/Closed Principle (open for extension, closed for modification)
3. THE System SHALL follow the Liskov Substitution Principle (implementations are substitutable for interfaces)
4. THE System SHALL follow the Interface Segregation Principle (clients depend only on methods they use)
5. THE System SHALL follow the Dependency Inversion Principle (depend on abstractions, not concretions)

### Requirement 10: No Performance Regressions

**User Story:** As a user, I want the refactored code to perform at least as well as the original, so that my video generation doesn't slow down.

#### Acceptance Criteria

1. WHEN generating a video with the refactored code, THE System SHALL complete in comparable time to the original
2. WHEN measuring memory usage, THE System SHALL use comparable memory to the original
3. THE System SHALL not introduce unnecessary object allocations or copies
4. THE System SHALL maintain efficient audio and video processing
