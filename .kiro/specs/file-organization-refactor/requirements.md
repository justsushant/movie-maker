# Requirements Document

## Introduction

This specification defines the requirements for reorganizing misplaced root-level files in the KokoroMoviePy codebase. Currently, `subtitle_config.py` and `renderer.py` exist at the project root but should be moved into appropriate module directories to follow the project's modular architecture pattern. This is a pure refactoring task with no behavior changes.

## Glossary

- **Root-level file**: A Python module file located at the project root directory rather than within a module subdirectory
- **Module directory**: A directory containing related Python modules with an `__init__.py` file (e.g., `subtitle/`, `api/`)
- **Import path**: The Python import statement used to reference a module (e.g., `from subtitle_config import SubtitleConfig`)
- **Refactoring**: Code restructuring that improves organization without changing external behavior
- **Backward compatibility**: Ensuring existing code continues to work after changes

## Requirements

### Requirement 1: Move subtitle_config.py to subtitle module

**User Story:** As a developer, I want subtitle configuration classes located within the subtitle module, so that related functionality is co-located and the project structure is more intuitive.

#### Acceptance Criteria

1. THE System SHALL move `subtitle_config.py` from the project root to `subtitle/config.py`
2. WHEN the file is moved, THE System SHALL preserve all class definitions, type hints, and docstrings exactly
3. THE System SHALL update all import statements across the codebase to use `from subtitle.config import` instead of `from subtitle_config import`
4. WHEN imports are updated, THE System SHALL maintain the same imported symbols (SubtitleConfig, SubtitleMode, StackingConfig, Color)

### Requirement 2: Move renderer.py to rendering module

**User Story:** As a developer, I want video composition logic organized in a dedicated rendering module, so that video assembly functionality is clearly separated from the TTS pipeline and subtitle rendering.

#### Acceptance Criteria

1. THE System SHALL create a new `rendering/` module directory with an `__init__.py` file
2. THE System SHALL move `renderer.py` from the project root to `rendering/video.py`
3. WHEN the file is moved, THE System SHALL preserve all function definitions, type hints, and docstrings exactly
4. THE System SHALL update the import statement in `api/library.py` to use `from rendering.video import create_video`
5. THE System SHALL ensure the module name clearly distinguishes video composition from subtitle rendering (subtitle/renderer.py)

### Requirement 3: Update all import references

**User Story:** As a developer, I want all import paths updated automatically, so that the codebase continues to work after the reorganization.

#### Acceptance Criteria

1. THE System SHALL identify all files importing from `subtitle_config`
2. THE System SHALL update imports in the following locations:
   - `subtitle/` module files (interfaces.py, layouts.py, renderer.py, composer.py)
   - `api/` module files (library.py, __init__.py)
   - `main.py`
   - All test files in `tests/`
   - Documentation files (README.md, docs/subtitles.md, docs/how_it_works.md)
3. THE System SHALL update the import in `api/library.py` from `from renderer import create_video` to `from rendering.video import create_video`
4. WHEN updating imports, THE System SHALL preserve the exact symbols being imported

### Requirement 4: Maintain test compatibility

**User Story:** As a developer, I want all existing tests to pass after the refactoring, so that I can verify no functionality was broken.

#### Acceptance Criteria

1. WHEN the refactoring is complete, THE System SHALL run the existing test suite
2. THE System SHALL ensure all tests that passed before the refactoring continue to pass
3. IF any test fails, THE System SHALL identify and fix the import path issue causing the failure

### Requirement 5: Update module exports

**User Story:** As a developer, I want module `__init__.py` files updated to export relocated classes, so that public APIs remain accessible.

#### Acceptance Criteria

1. THE System SHALL update `subtitle/__init__.py` to export SubtitleConfig, SubtitleMode, StackingConfig, and Color
2. THE System SHALL create `rendering/__init__.py` to export create_video function
3. WHEN exports are added, THE System SHALL use explicit `__all__` lists for clarity

### Requirement 6: Provide backward compatibility path

**User Story:** As a developer, I want a clear migration path for external code, so that users of the library can update their imports gradually.

#### Acceptance Criteria

1. THE System SHALL document the old and new import paths in a migration guide
2. THE System SHALL consider adding deprecation warnings for old import paths (optional)
3. THE System SHALL update all documentation to show the new import patterns

### Requirement 7: Preserve file history and metadata

**User Story:** As a developer, I want file metadata preserved during the move, so that git history remains traceable.

#### Acceptance Criteria

1. WHEN moving files, THE System SHALL use git mv commands to preserve file history
2. THE System SHALL ensure moved files retain their original content exactly
3. THE System SHALL not modify any logic, only file locations and import paths
