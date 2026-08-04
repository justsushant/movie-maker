# Implementation Plan: Codebase Cleanup

## Overview

This implementation plan breaks down the codebase cleanup into four sequential phases, each with validation steps to ensure the codebase remains functional. The cleanup removes deprecated code, debug artifacts, and obsolete documentation while maintaining backward compatibility where needed.

Each phase includes:
1. File deletion or modification tasks
2. Validation tasks to verify no breakage
3. Test execution to confirm functionality

## Tasks

- [x] 1. Phase 1: Remove debug scripts and analysis documents
  - [x] 1.1 Delete debug scripts
    - Delete `debug_audio_duration.py`
    - Delete `debug_renderer_width.py`
    - Delete `debug_subtitle_rendering.py`
    - Delete `debug_subtitle_rendering2.py`
    - Delete `debug_timestamp_issue.py`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 1.2 Delete bug analysis documents
    - Delete `BUG_ANALYSIS.md`
    - Delete `SUBTITLE_BUG_ANALYSIS.md`
    - Delete `CLEANUP_ANALYSIS.md`
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [x] 1.3 Write property test for file deletion completeness
    - **Property 1: File Deletion Completeness**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3**
  
  - [x] 1.4 Validate Phase 1 completion
    - Run `pytest` to verify all tests pass
    - Verify no references to deleted files in codebase
    - _Requirements: 1.6, 2.4_

- [x] 2. Checkpoint - Verify Phase 1 success
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Phase 2: Remove deprecated TTS pipeline module
  - [x] 3.1 Delete deprecated TTS pipeline files
    - Delete `tts_pipeline.py`
    - Delete `tests/test_tts_pipeline.py`
    - Delete `tests/test_tts_pipeline_deprecation.py`
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 3.2 Verify no imports of deleted module
    - Search codebase for `import tts_pipeline` or `from tts_pipeline`
    - Verify search returns no results
    - _Requirements: 3.4_
  
  - [x] 3.3 Write property test for no broken imports
    - **Property 2: No Broken Imports After Deletion**
    - **Validates: Requirements 3.4, 6.2, 7.5**
  
  - [x] 3.4 Validate Phase 2 completion
    - Run `pytest` to verify all tests pass
    - Run `make run` to verify CLI still works
    - _Requirements: 3.5_

- [x] 4. Checkpoint - Verify Phase 2 success
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Phase 3: Remove legacy API
  - [x] 5.1 Delete legacy API files
    - Delete `api/legacy.py`
    - Delete `tests/test_api_backward_compatibility.py`
    - _Requirements: 4.1, 4.2_
  
  - [x] 5.2 Update api/__init__.py to remove legacy exports
    - Remove `from api.legacy import generate_video` import
    - Remove `generate_video` from `__all__` list
    - Verify `__all__` only contains: `generate_video_from_text`, `generate_video_from_file`, `TTSConfig`, `VideoConfig`, `SubtitleConfig`, `SubtitleMode`
    - _Requirements: 4.3, 4.4, 4.5_
  
  - [x] 5.3 Write property test for API import stability
    - **Property 5: API Import Stability**
    - **Validates: Requirements 4.3, 4.4, 4.5**
  
  - [x] 5.4 Validate Phase 3 completion
    - Run `pytest` to verify all tests pass
    - Test importing `generate_video_from_text` and `generate_video_from_file` from `api`
    - Verify importing `generate_video` from `api` raises ImportError
    - _Requirements: 4.6_

- [x] 6. Checkpoint - Verify Phase 3 success
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Phase 4: Refactor CLI and remove legacy config
  - [x] 7.1 Refactor main.py to use new config classes directly
    - Create `get_default_tts_config()` function returning `TTSConfig` with defaults
    - Create `get_default_video_config()` function returning `VideoConfig` with defaults
    - Create `get_default_subtitle_config()` function returning `SubtitleConfig` with defaults
    - Create `create_run_directory()` function for timestamped output directory
    - Update `run_pipeline()` to use new config functions
    - Remove `importlib.util` import and config.py loading
    - Preserve SRT generation functionality
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [x] 7.2 Write property test for configuration object construction
    - **Property 6: Configuration Object Construction**
    - **Validates: Requirements 5.1, 5.2**
  
  - [x] 7.3 Validate CLI functional equivalence
    - Run `make run` with test input
    - Verify output files are created
    - Compare output with previous run (if available)
    - _Requirements: 5.4, 5.5_
  
  - [x] 7.4 Delete legacy config.py
    - Delete `config.py` from project root
    - _Requirements: 6.1_
  
  - [x] 7.5 Verify no imports of config.py remain
    - Search codebase for `import config` or `from config import` (excluding `config/` package)
    - Verify search returns no results
    - _Requirements: 6.2_
  
  - [x] 7.6 Validate Phase 4 completion
    - Run `pytest` to verify all tests pass
    - Run `python main.py` to verify CLI works
    - Verify all 4 output files created (WAV, JSON, SRT, MP4)
    - _Requirements: 6.3, 6.4_

- [x] 8. Checkpoint - Verify Phase 4 success
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Final validation and integration tests
  - [x] 9.1 Run full test suite
    - Execute `pytest` and verify all tests pass
    - _Requirements: 7.1_
  
  - [x] 9.2 Validate CLI end-to-end
    - Run `make run` with default input
    - Run `python main.py` directly
    - Verify video file exists in timestamped output directory
    - Verify all 4 output files present (WAV, JSON, SRT, MP4)
    - _Requirements: 7.2, 7.3, 7.6, 7.7_
  
  - [x] 9.3 Write property test for CLI functional equivalence
    - **Property 4: CLI Functional Equivalence**
    - **Validates: Requirements 5.4, 5.5, 6.4, 7.2, 7.6**
  
  - [x] 9.4 Write property test for output file completeness
    - **Property 7: Output File Completeness**
    - **Validates: Requirements 7.3, 7.7**
  
  - [x] 9.5 Validate library API functionality
    - Import `api.library.generate_video_from_text`
    - Call with test text input
    - Verify video file is generated and path is returned
    - _Requirements: 7.4_
  
  - [x] 9.6 Write property test for library API functionality
    - **Property 8: Library API Functionality**
    - **Validates: Requirements 7.4**
  
  - [x] 9.7 Verify no broken imports in codebase
    - Attempt to import all Python modules in the project
    - Verify no ImportError exceptions occur
    - _Requirements: 7.5_
  
  - [x] 9.8 Write property test for test suite integrity
    - **Property 3: Test Suite Integrity After Cleanup**
    - **Validates: Requirements 1.6, 3.5, 4.6, 6.3, 7.1**

- [x] 10. Final checkpoint - Cleanup complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based tests that can be skipped for faster completion
- Each phase must be validated before proceeding to the next phase
- Checkpoints ensure incremental validation and provide opportunities to address issues
- The cleanup is designed to be reversible via git if any phase fails validation
- Property tests validate universal correctness properties across all cleanup phases
- Unit tests validate specific examples and edge cases for each phase
- All file deletions should be performed using safe deletion methods (check existence first)
- Import verification should use AST parsing for reliability, not regex
- Configuration value preservation is critical in Phase 4 - verify all defaults match legacy config
