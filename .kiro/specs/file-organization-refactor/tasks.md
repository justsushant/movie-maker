# Implementation Plan: File Organization Refactor

## Overview

This plan reorganizes two misplaced root-level files into appropriate module directories. The refactoring moves `subtitle_config.py` to `subtitle/config.py` and `renderer.py` to `rendering/video.py`, then updates all import paths across the codebase. This is a pure refactoring with no behavior changes.

## Tasks

- [x] 1. Create pre-refactoring snapshot for verification
  - Capture list of all files importing subtitle_config and renderer
  - Run test suite and record which tests pass
  - Document current file locations
  - _Requirements: 4.2, 7.3_

- [x] 2. Move subtitle_config.py to subtitle module
  - [x] 2.1 Move subtitle_config.py to subtitle/config.py using git mv
    - Use `git mv subtitle_config.py subtitle/config.py` to preserve history
    - Verify file content is identical after move
    - _Requirements: 1.1, 1.2, 7.1, 7.2_
  
  - [x] 2.2 Update subtitle/__init__.py to export config classes
    - Add imports for SubtitleConfig, SubtitleMode, StackingConfig, Color
    - Add these symbols to __all__ list
    - _Requirements: 5.1, 5.3_
  
  - [x] 2.3 Write property test for content preservation
    - **Property 1: Content Preservation**
    - **Validates: Requirements 1.2, 2.3, 7.2**

- [x] 3. Update imports in subtitle module files
  - [x] 3.1 Update subtitle/interfaces.py import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - Verify file imports successfully
    - _Requirements: 1.3, 1.4_
  
  - [x] 3.2 Update subtitle/layouts.py import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - Verify file imports successfully
    - _Requirements: 1.3, 1.4_
  
  - [x] 3.3 Update subtitle/renderer.py import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - Verify file imports successfully
    - _Requirements: 1.3, 1.4_
  
  - [x] 3.4 Update subtitle/composer.py import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - Verify file imports successfully
    - _Requirements: 1.3, 1.4_

- [x] 4. Create rendering module and move renderer.py
  - [x] 4.1 Create rendering module directory
    - Create `rendering/` directory
    - Create `rendering/__init__.py` with create_video export
    - Add __all__ list with create_video
    - _Requirements: 2.1, 5.2, 5.3_
  
  - [x] 4.2 Move renderer.py to rendering/video.py using git mv
    - Use `git mv renderer.py rendering/video.py` to preserve history
    - Verify file content is identical after move
    - _Requirements: 2.2, 2.3, 7.1, 7.2_
  
  - [x] 4.3 Update rendering/video.py internal import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - Verify file imports successfully
    - _Requirements: 1.3, 1.4_

- [x] 5. Update imports in api module
  - [x] 5.1 Update api/library.py imports
    - Change `from subtitle_config import` to `from subtitle.config import`
    - Change `from renderer import create_video` to `from rendering.video import create_video`
    - Verify file imports successfully
    - _Requirements: 1.3, 2.4, 3.3_
  
  - [x] 5.2 Update api/__init__.py import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - Verify file imports successfully
    - _Requirements: 1.3, 1.4_

- [x] 6. Update imports in root files
  - [x] 6.1 Update main.py import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - Verify file imports successfully
    - _Requirements: 1.3, 1.4_

- [x] 7. Checkpoint - Verify core functionality
  - Run basic import tests to ensure all modules load correctly
  - Test: `python -c "from subtitle.config import SubtitleConfig"`
  - Test: `python -c "from rendering.video import create_video"`
  - Test: `python -c "from api.library import generate_video_from_text"`
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Update imports in test files
  - [x] 8.1 Update tests/test_subtitle_layouts.py import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - _Requirements: 3.2_
  
  - [x] 8.2 Update tests/test_library_api.py import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - _Requirements: 3.2_
  
  - [x] 8.3 Update tests/integration/helpers.py import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - _Requirements: 3.2_
  
  - [x] 8.4 Update tests/benchmark_performance.py import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - _Requirements: 3.2_
  
  - [x] 8.5 Update tests/profile_performance.py import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - _Requirements: 3.2_
  
  - [x] 8.6 Update tests/profile_pipeline.py import
    - Change `from subtitle_config import` to `from subtitle.config import`
    - _Requirements: 3.2_

- [x] 9. Update documentation files
  - [x] 9.1 Update README.md code examples
    - Replace all `from subtitle_config import` with `from subtitle.config import`
    - Replace all `from renderer import` with `from rendering.video import`
    - _Requirements: 3.2, 6.3_
  
  - [x] 9.2 Update docs/subtitles.md code examples
    - Replace all `from subtitle_config import` with `from subtitle.config import`
    - _Requirements: 3.2, 6.3_
  
  - [x] 9.3 Update docs/how_it_works.md code examples
    - Replace all `from subtitle_config import` with `from subtitle.config import`
    - _Requirements: 3.2, 6.3_

- [x] 10. Write property tests for refactoring correctness
  - [x] 10.1 Write property test for import path modernization
    - **Property 2: Import Path Modernization**
    - **Validates: Requirements 1.3, 6.3**
  
  - [x] 10.2 Write property test for symbol availability
    - **Property 3: Symbol Availability**
    - **Validates: Requirements 1.4, 3.4**
  
  - [x] 10.3 Write property test for behavior preservation
    - **Property 4: Behavior Preservation**
    - **Validates: Requirements 4.2, 7.3**

- [x] 11. Run full test suite and verify
  - [x] 11.1 Run pytest to execute all tests
    - Execute full test suite
    - Compare results with pre-refactoring snapshot
    - _Requirements: 4.1, 4.2_
  
  - [x] 11.2 Write unit tests for specific file locations
    - Test that subtitle/config.py exists
    - Test that rendering/video.py exists
    - Test that old files don't exist at root
    - _Requirements: 1.1, 2.1, 2.2_
  
  - [x] 11.3 Write unit tests for module exports
    - Test that subtitle.__init__ exports config classes
    - Test that rendering.__init__ exports create_video
    - Test that __all__ lists are defined
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 12. Final verification checkpoint
  - Verify no files contain old import patterns using ripgrep
  - Verify git history preserved: `git log --follow subtitle/config.py`
  - Verify git history preserved: `git log --follow rendering/video.py`
  - Run full test suite one final time
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster completion
- Each task references specific requirements for traceability
- File moves use `git mv` to preserve history
- Import updates follow dependency order (leaf modules first)
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and file locations
