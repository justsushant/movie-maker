# Requirements Document

## Introduction

This specification defines the requirements for cleaning up the KokoroMoviePy codebase by removing deprecated code, debug scripts, bug analysis documents, and completed spec directories. The cleanup is organized into four phases to minimize risk and maintain backward compatibility where appropriate.

The codebase has been successfully refactored with new modular APIs (`api.library`), new configuration classes (`TTSConfig`, `VideoConfig`, `SubtitleConfig`), and a new modular architecture (`tts/`, `processing/`, `pipeline/` packages). This cleanup removes artifacts from the development and refactoring process that are no longer needed.

## Glossary

- **Debug_Script**: Python files prefixed with `debug_` used for troubleshooting during development
- **Bug_Analysis_Document**: Markdown files documenting bug investigations (e.g., `BUG_ANALYSIS.md`)
- **Legacy_API**: The `api.legacy.generate_video()` function that works with pre-generated audio and JSON files
- **Legacy_Config**: The `config.py` module containing the `get_config()` function that returns a dictionary
- **Deprecated_TTS_Pipeline**: The `tts_pipeline.py` module containing the `MoviePySubtitleExtractor` class
- **Completed_Spec**: A spec directory under `.kiro/specs/` for a feature that has been fully implemented
- **CLI**: The command-line interface entry point in `main.py`
- **Library_API**: The new programmatic API in `api.library` with `generate_video_from_text()` and `generate_video_from_file()`

## Requirements

### Requirement 1: Remove Debug Scripts

**User Story:** As a developer, I want debug scripts removed from the codebase, so that the repository only contains production code and the project structure is cleaner.

#### Acceptance Criteria

1. THE System SHALL delete `debug_audio_duration.py` from the project root
2. THE System SHALL delete `debug_renderer_width.py` from the project root
3. THE System SHALL delete `debug_subtitle_rendering.py` from the project root
4. THE System SHALL delete `debug_subtitle_rendering2.py` from the project root
5. THE System SHALL delete `debug_timestamp_issue.py` from the project root
6. WHEN all debug scripts are deleted, THEN the test suite SHALL continue to pass without errors

### Requirement 2: Remove Bug Analysis Documents

**User Story:** As a developer, I want bug analysis documents removed from the codebase, so that historical debugging notes don't clutter the repository.

#### Acceptance Criteria

1. THE System SHALL delete `BUG_ANALYSIS.md` from the project root
2. THE System SHALL delete `SUBTITLE_BUG_ANALYSIS.md` from the project root
3. THE System SHALL delete `CLEANUP_ANALYSIS.md` from the project root
4. WHEN all bug analysis documents are deleted, THEN the documentation structure SHALL remain intact

### Requirement 3: Remove Deprecated TTS Pipeline Module

**User Story:** As a developer, I want the deprecated `tts_pipeline.py` module removed, so that the codebase only contains the new modular TTS architecture.

#### Acceptance Criteria

1. THE System SHALL delete `tts_pipeline.py` from the project root
2. THE System SHALL delete `tests/test_tts_pipeline.py` from the tests directory
3. THE System SHALL delete `tests/test_tts_pipeline_deprecation.py` from the tests directory
4. WHEN the deprecated TTS pipeline is removed, THEN no import statements in the codebase SHALL reference `tts_pipeline`
5. WHEN the deprecated TTS pipeline is removed, THEN the test suite SHALL pass without errors

### Requirement 4: Remove Legacy API

**User Story:** As a developer, I want the legacy API removed after a deprecation period, so that the codebase only maintains the new library API.

#### Acceptance Criteria

1. THE System SHALL delete `api/legacy.py` from the api directory
2. THE System SHALL delete `tests/test_api_backward_compatibility.py` from the tests directory
3. THE System SHALL remove the `generate_video` import from `api/__init__.py`
4. THE System SHALL remove `generate_video` from the `__all__` list in `api/__init__.py`
5. WHEN the legacy API is removed, THEN `api/__init__.py` SHALL only export `generate_video_from_text` and `generate_video_from_file`
6. WHEN the legacy API is removed, THEN the test suite SHALL pass without errors

### Requirement 5: Refactor CLI to Use New Configuration Classes

**User Story:** As a developer, I want the CLI to use the new configuration classes directly, so that the codebase has a consistent configuration approach.

#### Acceptance Criteria

1. WHEN `main.py` is refactored, THEN it SHALL import `TTSConfig`, `VideoConfig`, and `SubtitleConfig` directly
2. WHEN `main.py` is refactored, THEN it SHALL NOT import from `config.py`
3. WHEN `main.py` is refactored, THEN it SHALL construct configuration objects from command-line arguments or defaults
4. WHEN `main.py` is refactored, THEN the CLI SHALL maintain the same user-facing behavior
5. WHEN `main.py` is refactored, THEN running `make run` SHALL produce the same output as before

### Requirement 6: Remove Legacy Config Module

**User Story:** As a developer, I want the legacy `config.py` module removed, so that the codebase only uses the new configuration classes.

#### Acceptance Criteria

1. THE System SHALL delete `config.py` from the project root
2. WHEN `config.py` is removed, THEN no import statements in the codebase SHALL reference it
3. WHEN `config.py` is removed, THEN the test suite SHALL pass without errors
4. WHEN `config.py` is removed, THEN the CLI SHALL continue to function correctly

### Requirement 7: Verify Codebase Integrity After Cleanup

**User Story:** As a developer, I want to verify that the cleanup hasn't broken any functionality, so that I can be confident the codebase is still working correctly.

#### Acceptance Criteria

1. WHEN all cleanup phases are complete, THEN running `pytest` SHALL pass all tests
2. WHEN all cleanup phases are complete, THEN running `make run` SHALL successfully generate a video from `files/input.txt`
3. WHEN all cleanup phases are complete, THEN the generated video file SHALL exist in the output directory
4. WHEN all cleanup phases are complete, THEN the Library_API SHALL be importable and functional
5. WHEN all cleanup phases are complete, THEN no broken import statements SHALL exist in the codebase
6. WHEN the CLI is executed with `python main.py`, THEN it SHALL complete without errors
7. WHEN the CLI completes, THEN it SHALL produce audio, JSON, SRT, and MP4 files in the timestamped output directory
